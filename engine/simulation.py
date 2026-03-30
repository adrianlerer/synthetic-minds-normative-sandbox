"""
engine/simulation.py — Motor principal de simulación SNMS.

Integra todos los módulos del sistema en un loop de simulación completo:
1. Carga el experimento YAML
2. Instancia agentes con sus MindProfiles
3. Loop: N_rounds × todos los agentes
   - decide_action() → apply_actions() → hbu_update()
   - spandrel_detector.scan_round() → multilevel_engine.compute_snapshot()
4. Registra métricas CLI, FDI, MSR, spandrels por ronda
5. Retorna SimulationResults

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from agents.base_agent import ActionType
from agents.judge import JudgeAgent
from agents.legislator import LegislatorAgent
from agents.union_leader import UnionLeaderAgent
from agents.firm import FirmAgent
from agents.citizen import CitizenAgent
from agents.regulator import RegulatorAgent
from engine.environment import LegalEnvironment
from engine.hbu import hbu_batch_update, compute_belief_distribution
from engine.multilevel import MultilevelSelectionEngine
from engine.spandrel_detector import SpandrelDetector
from norms.norm import Norm, NormType, NormFunction, SelectionLevel


# ─────────────────────────── Resultados ────────────────────────────────────

@dataclass
class RoundMetrics:
    """Métricas registradas por ronda."""
    round_number: int
    cli: float
    fdi: float
    msr: float
    norm_compliance_rate: float
    l1_fitness: float
    l2_fitness: float
    l3_fitness: float
    n_spandrels_confirmed: int
    belief_distribution: dict = field(default_factory=dict)


@dataclass
class SimulationResults:
    """Resultados completos de una ejecución de simulación.

    Attributes:
        experiment_id: ID del experimento.
        seed: Semilla utilizada.
        rounds_run: Número de rondas ejecutadas.
        round_metrics: Lista de métricas por ronda.
        spandrels: Todos los spandrels confirmados.
        final_cli: CLI al final de la simulación.
        final_fdi: FDI al final de la simulación.
        final_msr: MSR al final de la simulación.
        hypotheses_tested: Resultado del test de hipótesis.
    """
    experiment_id: str
    seed: int
    rounds_run: int
    round_metrics: list[RoundMetrics] = field(default_factory=list)
    spandrels: list = field(default_factory=list)
    final_cli: float = 0.0
    final_fdi: float = 0.0
    final_msr: float = 1.0
    hypotheses_tested: dict = field(default_factory=dict)

    def get_metric_by_round(self, metric: str, round_n: int) -> float | None:
        """Retorna el valor de una métrica en una ronda específica."""
        for rm in self.round_metrics:
            if rm.round_number == round_n:
                return getattr(rm, metric, None)
        return None

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "rounds_run": self.rounds_run,
            "final_cli": round(self.final_cli, 4),
            "final_fdi": round(self.final_fdi, 4),
            "final_msr": round(self.final_msr, 4),
            "spandrels_count": len(self.spandrels),
            "spandrels": [
                {
                    "spandrel_id": sp.spandrel_id,
                    "origin_norm_id": sp.origin_norm_id,
                    "emergence_round": sp.emergence_round,
                    "description": sp.description,
                    "fitness_contribution": round(sp.fitness_contribution, 4),
                    "is_parasitic": sp.is_parasitic,
                }
                for sp in self.spandrels
            ],
            "hypotheses_tested": self.hypotheses_tested,
            "round_metrics": [
                {
                    "round": rm.round_number,
                    "cli": round(rm.cli, 4),
                    "fdi": round(rm.fdi, 4),
                    "msr": round(rm.msr, 4),
                }
                for rm in self.round_metrics
            ],
        }


# ─────────────────────────── Fábrica de agentes ────────────────────────────

def _build_agents(agent_config: dict, rng: random.Random) -> list:
    """Instancia todos los agentes según la configuración del experimento.

    Args:
        agent_config: Sección 'agents' del YAML.
        rng: Generador aleatorio con seed controlada.

    Returns:
        Lista de todos los agentes instanciados.
    """
    agents = []

    archetype_factory = {
        "juez_csjn": lambda idx, cfg: JudgeAgent(
            agent_id=f"judge_{idx}",
            cri_base=cfg.get("cri_base", 0.82),
            institutional_capital=cfg.get("institutional_capital", 0.90),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "legislador_oficialista": lambda idx, cfg: LegislatorAgent(
            agent_id=f"leg_of_{idx}",
            is_ruling_party=True,
            cri_base=cfg.get("cri_base", 0.61),
            institutional_capital=cfg.get("institutional_capital", 0.65),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "legislador_opositor": lambda idx, cfg: LegislatorAgent(
            agent_id=f"leg_op_{idx}",
            is_ruling_party=False,
            cri_base=cfg.get("cri_base", 0.55),
            institutional_capital=cfg.get("institutional_capital", 0.60),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "dirigente_gremial": lambda idx, cfg: UnionLeaderAgent(
            agent_id=f"union_{idx}",
            cri_base=cfg.get("cri_base", 0.88),
            institutional_capital=cfg.get("institutional_capital", 0.78),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "firma_regulada": lambda idx, cfg: FirmAgent(
            agent_id=f"firm_{idx}",
            cri_base=cfg.get("cri_base", 0.45),
            institutional_capital=cfg.get("institutional_capital", 0.55),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "ciudadano_informado": lambda idx, cfg: CitizenAgent(
            agent_id=f"citizen_{idx}",
            cri_base=cfg.get("cri_base", 0.30),
            institutional_capital=cfg.get("institutional_capital", 0.20),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "firma": lambda idx, cfg: FirmAgent(  # alias
            agent_id=f"firm_{idx}",
            cri_base=cfg.get("cri_base", 0.45),
            institutional_capital=cfg.get("institutional_capital", 0.55),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
        "ciudadano": lambda idx, cfg: CitizenAgent(  # alias
            agent_id=f"citizen_{idx}",
            cri_base=cfg.get("cri_base", 0.30),
            institutional_capital=cfg.get("institutional_capital", 0.20),
            rng=random.Random(rng.randint(0, 2**31)),
        ),
    }

    for archetype_key, cfg in agent_config.items():
        count = cfg.get("count", 1)
        factory = archetype_factory.get(archetype_key)
        if factory is None:
            # Fallback: ciudadano
            factory = archetype_factory["ciudadano_informado"]
        for i in range(count):
            agents.append(factory(i, cfg))

    return agents


def _build_norm(norm_config: dict, introduction_round: int) -> Norm:
    """Construye el objeto Norm desde la configuración YAML."""
    origin_cfg = norm_config.get("origin_function", {})
    sl_map = {
        "L1": SelectionLevel.INDIVIDUAL,
        "L2": SelectionLevel.GROUP,
        "L3": SelectionLevel.POPULATION,
        "MLV": SelectionLevel.MULTILEVEL,
    }
    selection_level = sl_map.get(
        origin_cfg.get("selection_level", "L3"),
        SelectionLevel.POPULATION
    )
    norm_type_map = {
        "statutory": NormType.STATUTORY,
        "constitutional": NormType.CONSTITUTIONAL,
        "regulatory": NormType.REGULATORY,
        "informal": NormType.INFORMAL,
        "synthetic": NormType.SYNTHETIC,
    }
    norm_type = norm_type_map.get(
        norm_config.get("norm_type", "statutory"),
        NormType.STATUTORY
    )

    origin_function = NormFunction(
        label=origin_cfg.get("label", "unknown"),
        description=origin_cfg.get("description", ""),
        target_agents=origin_cfg.get("target_agents", []),
        expected_fitness_delta=origin_cfg.get("expected_fitness_delta", 0.0),
        selection_level=selection_level,
    )

    return Norm(
        norm_id=norm_config.get("norm_id", "norm_001"),
        name=norm_config.get("name", "Norma Experimental"),
        norm_type=norm_type,
        complexity=norm_config.get("complexity", 0.70),
        origin_function=origin_function,
        introduction_round=introduction_round,
        text_excerpt=norm_config.get("text_excerpt", ""),
    )


def _build_coalitions(agents: list, agent_config: dict) -> dict[str, list[str]]:
    """Construye el mapa de coaliciones para el MultilevelEngine."""
    coalitions: dict[str, list[str]] = {}

    # Agrupar por archetype_id
    for agent in agents:
        arch = agent.archetype_id
        if arch not in coalitions:
            coalitions[arch] = []
        coalitions[arch].append(agent.agent_id)

    # Agregar coaliciones explícitas del YAML si las hubiera
    return coalitions


def _update_norm_current_function(norm: Norm, environment: LegalEnvironment, round_number: int) -> None:
    """Actualiza la función actual de la norma según el estado del entorno.

    Detecta la deriva funcional: si la norma está siendo usada principalmente
    como arena de litigio (en lugar de su función declarada), actualiza
    current_function para reflejar esa deriva.
    """
    if round_number < norm.introduction_round:
        return

    # Si hay alta intensidad de sanciones y bajo compliance, la norma está "endurecida"
    # — su función actual es diferente a la declarada
    fdi_signal = environment.sanction_intensity * (1.0 - environment.norm_compliance_rate)
    # Also trigger drift from low compliance directly (norma no funciona como fue diseñada)
    low_compliance_drift = max(0.0, 0.60 - environment.norm_compliance_rate)  # empieza con compliance < 0.6
    total_drift_signal = fdi_signal + low_compliance_drift * 0.30

    if total_drift_signal > 0.08 and norm.current_function is not None:
        # Actualizar el delta de fitness actual para reflejar la deriva acumulada
        # La función "actual" se aleja progresivamente de la declarada
        current_delta = norm.current_function.expected_fitness_delta
        # Deriva proporcional a la señal: más fuerte con alta resistencia
        drift_magnitude = min(0.08, total_drift_signal * 0.15)
        drift_direction = -drift_magnitude  # la norma se vuelve menos beneficiosa en L3

        # Preservar label base sin concatenar indefinidamente
        base_label = norm.origin_function.label
        norm.current_function = NormFunction(
            label=f"{base_label}_derivada_r{round_number}",
            description=(
                f"[DERIVA activa ronda {round_number}] Función original: {norm.origin_function.label}. "
                f"Uso actual: arena de litigio y negociación informal."
            ),
            target_agents=norm.current_function.target_agents,
            expected_fitness_delta=max(-1.0, min(1.0, current_delta + drift_direction)),
            selection_level=SelectionLevel.GROUP,  # Deriva hacia nivel grupal (litigio)
        )


# ─────────────────────────── Motor principal ───────────────────────────────

class SNMSSimulation:
    """Motor principal de simulación SNMS.

    Orquesta todos los subsistemas: agentes, entorno, HBU, multinivel, spandrels.
    """

    def __init__(
        self,
        experiment_config: dict,
        seed: int = 42,
        rounds_override: int | None = None,
        verbose: bool = False,
    ):
        self.config = experiment_config
        self.seed = seed
        self.verbose = verbose
        self.rng = random.Random(seed)

        sim_cfg = experiment_config.get("simulation", {})
        self.n_rounds = rounds_override or sim_cfg.get("rounds", 100)
        self.norm_introduction_round = sim_cfg.get("norm_introduction_round", 5)

        # Instanciar componentes
        self.agents = _build_agents(
            experiment_config.get("agents", {}),
            self.rng,
        )
        self.norm = _build_norm(
            experiment_config.get("norm", {}),
            self.norm_introduction_round,
        )
        self.environment = LegalEnvironment(
            cli=0.50,
            norm_compliance_rate=0.60,
            norm_id=self.norm.norm_id,
            coalition_signal=self._init_coalition_signals(experiment_config),
        )
        self.environment.set_agents(self.agents)

        coalitions = _build_coalitions(
            self.agents,
            experiment_config.get("agents", {}),
        )
        self.multilevel_engine = MultilevelSelectionEngine(coalitions=coalitions)
        self.spandrel_detector = SpandrelDetector(rng=random.Random(seed + 1))

    def _init_coalition_signals(self, config: dict) -> dict[str, float]:
        """Inicializa las señales coalicionales desde el YAML."""
        signals: dict[str, float] = {}
        coalitions_cfg = config.get("coalitions", {})
        for cid, ccfg in coalitions_cfg.items():
            signal_value = ccfg.get("coalition_signal", 0.0)
            members = ccfg.get("members", [])
            for member_archetype in members:
                signals[member_archetype] = signal_value
        return signals

    def run(self) -> SimulationResults:
        """Ejecuta la simulación completa y retorna los resultados.

        Returns:
            SimulationResults con todas las métricas registradas.
        """
        results = SimulationResults(
            experiment_id=self.config.get("experiment_id", "exp_001"),
            seed=self.seed,
            rounds_run=self.n_rounds,
        )

        for round_n in range(1, self.n_rounds + 1):
            self.environment.round_number = round_n

            # ── 1. Cada agente decide su acción ──
            for agent in self.agents:
                agent.decide_action(self.environment)

            # ── 2. Aplicar acciones al entorno ──
            for agent in self.agents:
                delta = self.environment.apply_action(agent, agent.last_action)
                agent.update_fitness(delta)

            # ── 3. HBU: update bayesiano de creencias ──
            hbu_batch_update(
                agents=self.agents,
                environment=self.environment,
                norm_complexity=self.norm.complexity,
            )

            # ── 4. Actualizar función actual de la norma (deriva) ──
            _update_norm_current_function(self.norm, self.environment, round_n)

            # ── 5. Detectar spandrels ──
            new_spandrels = self.spandrel_detector.scan_round(
                round_number=round_n,
                agents=self.agents,
                active_norms=[self.norm],
            )
            for sp in new_spandrels:
                self.norm.register_spandrel(sp)
                results.spandrels.append(sp)

            # ── 6. Snapshot multinivel ──
            snapshot = self.multilevel_engine.compute_snapshot(
                round_number=round_n,
                agents=self.agents,
                norm=self.norm,
                environment_stability=self.environment.cli,
            )

            # ── 7. Actualizar CLI ──
            self.environment.compute_cli()

            # ── 8. Registrar métricas de la ronda ──
            belief_dist = compute_belief_distribution(self.agents)
            metrics = RoundMetrics(
                round_number=round_n,
                cli=self.environment.cli,
                fdi=self.norm.functional_drift_index(),
                msr=snapshot.msr,
                norm_compliance_rate=self.environment.norm_compliance_rate,
                l1_fitness=snapshot.l1_fitness,
                l2_fitness=snapshot.l2_fitness,
                l3_fitness=snapshot.l3_fitness,
                n_spandrels_confirmed=len(results.spandrels),
                belief_distribution=belief_dist,
            )
            results.round_metrics.append(metrics)

            if self.verbose and round_n % 10 == 0:
                print(
                    f"  Ronda {round_n:3d} | CLI={self.environment.cli:.3f} | "
                    f"FDI={metrics.fdi:.3f} | MSR={snapshot.msr:.3f} | "
                    f"Spandrels={len(results.spandrels)}"
                )

        # ── Resultados finales ──
        last = results.round_metrics[-1] if results.round_metrics else None
        results.final_cli = last.cli if last else 0.0
        results.final_fdi = last.fdi if last else 0.0
        results.final_msr = last.msr if last else 1.0

        # Test de hipótesis
        results.hypotheses_tested = self._test_hypotheses(results)

        return results

    def _test_hypotheses(self, results: SimulationResults) -> dict:
        """Evalúa las hipótesis del experimento contra los resultados.

        Returns:
            Diccionario {hypothesis_id: {confirmed: bool, value: float, prediction: str}}
        """
        hypotheses_cfg = self.config.get("hypotheses", {})
        tested: dict = {}

        for hid, h_cfg in hypotheses_cfg.items():
            prediction = h_cfg.get("prediction", "")
            label = h_cfg.get("label", hid)
            confirmed = False
            value = None

            if "CLI_final > 0.85" in prediction:
                value = results.final_cli
                confirmed = value > 0.85

            elif "FDI_norma > 0.40" in prediction:
                # FDI en ronda 50 o en la última ronda disponible
                target_round = min(50, results.rounds_run)
                for rm in results.round_metrics:
                    if rm.round_number == target_round:
                        value = rm.fdi
                        break
                if value is None:
                    value = results.final_fdi
                confirmed = value > 0.40

            elif "spandrel" in prediction.lower() or "Spandrel" in prediction:
                value = len(results.spandrels)
                confirmed = value >= 1

            elif "MSR < 0.80" in prediction:
                target_round = min(70, results.rounds_run)
                for rm in results.round_metrics:
                    if rm.round_number == target_round:
                        value = rm.msr
                        break
                if value is None:
                    value = results.final_msr
                confirmed = value < 0.80

            tested[hid] = {
                "label": label,
                "prediction": prediction,
                "confirmed": confirmed,
                "value": round(value, 4) if value is not None else None,
            }

        return tested


# ─────────────────────────── Función de conveniencia ───────────────────────

def run_from_yaml(
    yaml_path: str,
    seed: int = 42,
    rounds_override: int | None = None,
    verbose: bool = False,
) -> SimulationResults:
    """Ejecuta una simulación completa a partir de un archivo YAML.

    Args:
        yaml_path: Ruta al archivo YAML del experimento.
        seed: Semilla aleatoria.
        rounds_override: Si se provee, sobreescribe el número de rondas del YAML.
        verbose: Si True, imprime progreso por ronda.

    Returns:
        SimulationResults con todos los resultados.
    """
    with open(yaml_path) as f:
        config = yaml.safe_load(f)

    sim = SNMSSimulation(
        experiment_config=config,
        seed=seed,
        rounds_override=rounds_override,
        verbose=verbose,
    )
    return sim.run()
