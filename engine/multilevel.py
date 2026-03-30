"""
engine/multilevel.py — Motor de selección multinivel (L1/L2/L3).

Implementa la selección simultánea en tres niveles siguiendo
Wilson & Sober (1994) y Okasha (2006):

- L1 (Individual): Fitness del agente individual
- L2 (Grupal):    Fitness de coaliciones e instituciones
- L3 (Poblacional): Fitness de la norma en el ecosistema

Una norma puede ser:
- Mutualista:  L3 ↑ y L1 ↑ (bien común genuino)
- Parasitaria: L1 ↑ de algunos actores, L3 ↓ (rent-seeking)
- Altruista:   L3 ↑ pero L1 ↓ (auto-sacrificio institucional, raro)
- Delétrea:    L1 ↓ y L3 ↓ (norma inviable que persiste por inercia/CRI)

El Multilevel Selection Ratio (MSR) = fitness_L3 / fitness_L1_promedio
indica el tipo de norma:
- MSR > 1.2: mutualista
- 0.8 ≤ MSR ≤ 1.2: neutral
- MSR < 0.8: parasitaria o delétrea

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseSyntheticAgent
    from norms.norm import Norm


@dataclass
class LevelFitness:
    """Fitness calculado para un nivel de selección en una ronda."""
    level: str          # "L1", "L2", "L3"
    round_number: int
    fitness_value: float    # [-1, 1]
    component_agents: list[str] = field(default_factory=list)  # agent_ids contribuyentes
    notes: str = ""


@dataclass
class MultilevelFitnessSnapshot:
    """Snapshot de fitness en los tres niveles para una norma en una ronda."""
    norm_id: str
    round_number: int
    l1_fitness: float   # Promedio ponderado de fitness individual
    l2_fitness: float   # Fitness de coaliciones activas
    l3_fitness: float   # Fitness del ecosistema normativo completo
    msr: float          # Multilevel Selection Ratio = l3 / l1

    @property
    def norm_type_classification(self) -> str:
        """Clasifica la norma según su patrón de selección multinivel."""
        if self.l3_fitness > 0 and self.l1_fitness > 0 and self.msr > 1.2:
            return "mutualista"
        elif self.l3_fitness > 0 and self.l1_fitness < 0:
            return "altruista"
        elif self.l3_fitness < 0 and self.l1_fitness > 0:
            return "parasitaria"
        elif self.l3_fitness < 0 and self.l1_fitness < 0:
            return "deleterea"
        else:
            return "neutral"


class MultilevelSelectionEngine:
    """Motor de selección multinivel.

    Calcula simultáneamente el fitness de una norma en los tres niveles
    y detecta desacoples entre ellos (señal de parasitismo o altruismo).
    """

    def __init__(self, coalitions: dict[str, list[str]]):
        """Inicializa el motor.

        Args:
            coalitions: Diccionario {coalition_id: [agent_ids]}.
                Ejemplo: {"cgt": ["union_0", "union_1"], "csjn": ["judge_0", ...]}
        """
        self.coalitions = coalitions
        self.fitness_history: list[MultilevelFitnessSnapshot] = []

    def compute_l1_fitness(
        self,
        agents: list["BaseSyntheticAgent"],
        norm: "Norm",
    ) -> float:
        """Calcula fitness promedio ponderado a nivel individual.

        El peso de cada agente es su capital institucional (más capital
        → más influencia en el fitness del sistema).

        Args:
            agents: Lista de todos los agentes activos.
            norm: Norma cuyo efecto se evalúa.

        Returns:
            Fitness L1 promedio ponderado [-1, 1].
        """
        if not agents:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for agent in agents:
            # Fitness individual: cambio en capital institucional en última ronda
            delta = getattr(agent, 'fitness_last_delta', 0.0)
            weight = agent.institutional_capital
            weighted_sum += delta * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def compute_l2_fitness(
        self,
        agents: list["BaseSyntheticAgent"],
        norm: "Norm",
    ) -> float:
        """Calcula fitness a nivel de coaliciones.

        Para cada coalición activa, computa la variación media de capital
        de sus miembros. Retorna el promedio ponderado entre coaliciones
        (ponderado por tamaño).

        Args:
            agents: Lista de todos los agentes activos.
            norm: Norma cuyo efecto se evalúa.

        Returns:
            Fitness L2 [-1, 1].
        """
        agent_map = {a.agent_id: a for a in agents}
        coalition_fitnesses = []

        for coalition_id, member_ids in self.coalitions.items():
            members = [agent_map[mid] for mid in member_ids if mid in agent_map]
            if not members:
                continue
            coalition_fitness = sum(
                getattr(m, 'fitness_last_delta', 0.0) for m in members
            ) / len(members)
            coalition_fitnesses.append((len(members), coalition_fitness))

        if not coalition_fitnesses:
            return 0.0

        total_size = sum(s for s, _ in coalition_fitnesses)
        return sum(s * f for s, f in coalition_fitnesses) / total_size

    def compute_l3_fitness(
        self,
        agents: list["BaseSyntheticAgent"],
        norm: "Norm",
        environment_stability: float,
    ) -> float:
        """Calcula fitness a nivel poblacional (ecosistema normativo).

        El fitness del ecosistema combina:
        - Estabilidad del entorno (CLI actual)
        - Tasa de adopción de la norma
        - Ausencia de conflicto sistémico

        Args:
            agents: Lista de todos los agentes activos.
            norm: Norma cuyo efecto se evalúa.
            environment_stability: CLI actual del entorno [0,1].

        Returns:
            Fitness L3 [-1, 1].
        """
        if not agents:
            return 0.0

        # Tasa de adopción: agentes que consideran la norma válida
        adopters = sum(
            1 for a in agents
            if a.norm_validity_belief >= 0.5
        )
        adoption_rate = adopters / len(agents)

        # Conflicto sistémico: varianza de creencias (alta varianza = conflicto)
        beliefs = [a.norm_validity_belief for a in agents]
        mean_belief = sum(beliefs) / len(beliefs)
        variance = sum((b - mean_belief) ** 2 for b in beliefs) / len(beliefs)
        conflict_penalty = min(0.5, variance * 2)

        # FDI de la norma: alta deriva funcional reduce el fitness del ecosistema
        fdi_penalty = norm.functional_drift_index() * 0.3

        l3 = (adoption_rate * 2 - 1)  # normalizar [0,1] → [-1,1]
        l3 += (environment_stability * 2 - 1) * 0.3
        l3 -= conflict_penalty
        l3 -= fdi_penalty

        return max(-1.0, min(1.0, l3))

    def compute_snapshot(
        self,
        round_number: int,
        agents: list["BaseSyntheticAgent"],
        norm: "Norm",
        environment_stability: float,
    ) -> MultilevelFitnessSnapshot:
        """Calcula y registra el snapshot de fitness multinivel.

        Args:
            round_number: Número de ronda actual.
            agents: Lista de todos los agentes activos.
            norm: Norma bajo análisis.
            environment_stability: CLI actual.

        Returns:
            MultilevelFitnessSnapshot con todos los niveles calculados.
        """
        l1 = self.compute_l1_fitness(agents, norm)
        l2 = self.compute_l2_fitness(agents, norm)
        l3 = self.compute_l3_fitness(agents, norm, environment_stability)

        msr = l3 / l1 if abs(l1) > 0.01 else 1.0  # evitar div/0

        snapshot = MultilevelFitnessSnapshot(
            norm_id=norm.norm_id,
            round_number=round_number,
            l1_fitness=l1,
            l2_fitness=l2,
            l3_fitness=l3,
            msr=msr,
        )
        self.fitness_history.append(snapshot)
        return snapshot
