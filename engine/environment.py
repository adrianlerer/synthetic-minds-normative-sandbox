"""
engine/environment.py — LegalEnvironment: estado del ecosistema normativo.

Representa el entorno institucional en que operan los agentes. No es
estático: evoluciona ronda a ronda como función de las acciones de los
agentes y de las normas activas.

Métricas centrales:
- CLI (Constitutional Lock-in Index): rigidez estructural acumulada [0,1]
- norm_compliance_rate: tasa de cumplimiento observada en la ronda [0,1]
- coalition_signal: señal coalicional por arquetipo {archetype_id: float}
- sanction_intensity: intensidad promedio de sanciones [0,1]

El CLI es la métrica más importante: mide cuánto se ha "cristalizado"
el sistema institucional en torno a la interpretación vigente de la norma.
CLI > 0.85 indica lock-in severo (hipótesis H1 de la simulación).

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseSyntheticAgent, ActionType


# Acciones que aumentan el CLI (endurecen el lock-in)
CLI_INCREASING_ACTIONS = {"litigate", "resist", "coalesce"}
# Acciones que reducen o estabilizan el CLI
CLI_DECREASING_ACTIONS = {"comply", "negotiate"}
# Factor de aprendizaje del CLI (inercia alta = cambios lentos)
CLI_LEARNING_RATE = 0.04
# Factor de sanción base
BASE_SANCTION_INTENSITY = 0.30


@dataclass
class LegalEnvironment:
    """Estado del ecosistema normativo en una ronda.

    Attributes:
        cli: Constitutional Lock-in Index [0,1]. Empieza en 0.50.
        norm_compliance_rate: Tasa de cumplimiento en la ronda actual [0,1].
        coalition_signal: Señal agregada por arquetipo {archetype_id: float [-1,1]}.
            Positivo = apoyo a la norma, negativo = resistencia.
        sanction_intensity: Intensidad promedio de sanciones impuestas [0,1].
        round_number: Número de ronda actual (0-indexed).
        norm_id: ID de la norma activa.
        agents: Lista de agentes activos (se setea por el motor).
    """

    cli: float = 0.50
    norm_compliance_rate: float = 0.60
    coalition_signal: dict[str, float] = field(default_factory=dict)
    sanction_intensity: float = BASE_SANCTION_INTENSITY
    round_number: int = 0
    norm_id: str = "reforma_laboral_synthetic_2025"
    _agents: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        self.cli = max(0.0, min(1.0, self.cli))
        self.norm_compliance_rate = max(0.0, min(1.0, self.norm_compliance_rate))

    def set_agents(self, agents: list["BaseSyntheticAgent"]) -> None:
        """Registra la lista de agentes activos para uso interno."""
        self._agents = agents

    def apply_action(self, agent: "BaseSyntheticAgent", action: "ActionType") -> float:
        """Aplica la acción de un agente al entorno y retorna el delta de fitness.

        Las acciones modifican el entorno de forma acumulada:
        - LITIGATE/RESIST aumentan la presión sobre el CLI
        - COMPLY/NEGOTIATE reducen la tensión institucional
        - LOBBY/COALESCE refuerzan señales coalicionales

        Args:
            agent: Agente que ejecuta la acción.
            action: Acción ejecutada.

        Returns:
            Delta de fitness para el agente [-0.30, 0.30].
        """
        action_val = action.value if hasattr(action, 'value') else str(action)

        fitness_delta = 0.0

        if action_val == "comply":
            # Cumplir mejora el fitness del agente y reduce tensión
            fitness_delta = 0.05 * (1.0 - agent.cri)
            self.norm_compliance_rate = min(1.0, self.norm_compliance_rate + 0.001)

        elif action_val == "resist":
            # Resistir consume capital pero preserva posición ideológica
            fitness_delta = -0.08 + agent.cri * 0.05
            self.norm_compliance_rate = max(0.0, self.norm_compliance_rate - 0.002)
            # Refuerza señal coalicional del arquetipo
            arch = agent.archetype_id
            self.coalition_signal[arch] = self.coalition_signal.get(arch, 0.0) - 0.10

        elif action_val == "litigate":
            # Litigar es costoso pero puede recompensar si CRI alto
            cost = 0.25
            benefit = agent.cri * 0.20 + (1.0 - agent.norm_validity_belief) * 0.15
            fitness_delta = benefit - cost
            self.sanction_intensity = min(1.0, self.sanction_intensity + 0.015)

        elif action_val == "lobby":
            # Lobby beneficia si hay capital institucional alto
            fitness_delta = 0.10 * agent.institutional_capital - 0.05
            arch = agent.archetype_id
            self.coalition_signal[arch] = self.coalition_signal.get(arch, 0.0) + 0.08

        elif action_val == "negotiate":
            # Negociación beneficia a ambas partes moderadamente
            fitness_delta = 0.08 - agent.cri * 0.04
            self.norm_compliance_rate = min(1.0, self.norm_compliance_rate + 0.003)
            self.sanction_intensity = max(0.0, self.sanction_intensity - 0.01)

        elif action_val == "defect":
            # Defección: alto riesgo, potencial alto retorno
            fitness_delta = -0.30 + agent.institutional_capital * 0.25
            arch = agent.archetype_id
            self.coalition_signal[arch] = self.coalition_signal.get(arch, 0.0) - 0.20

        elif action_val == "coalesce":
            # Unirse a coalición: inversión de capital a cambio de señal
            fitness_delta = -0.05 + agent.mind.doctrinal.coalition_loyalty * 0.15
            arch = agent.archetype_id
            self.coalition_signal[arch] = self.coalition_signal.get(arch, 0.0) + 0.12

        return fitness_delta

    def compute_cli(self) -> float:
        """Calcula el CLI como función del estado institucional agregado.

        El CLI (Constitutional Lock-in Index) mide cuánto se ha cristalizado
        el sistema en su postura de RESISTENCIA a la norma — no de apoyo.
        Un CLI alto (> 0.85) indica que el sistema está bloqueado en modo
        de rechazo institucional: es el lock-in del bloqueo, no del cumplimiento.

        Componentes:
        1. CRI promedio ponderado → alta resistencia institucional
        2. Tasa de resistencia activa (RESIST + LITIGATE) → presión de bloqueo
        3. Baja creencia en validez → cristalización del rechazo
        4. Sanción cresciente → el sistema responde endureciendo posiciones

        Returns:
            CLI actualizado [0,1].
        """
        if not self._agents:
            return self.cli

        from agents.base_agent import ActionType

        # Componente 1: CRI promedio ponderado por capital institucional
        # Los agentes con más capital institucional tienen más peso en el CLI
        weighted_cri_sum = 0.0
        total_capital = 0.0
        for agent in self._agents:
            w = agent.institutional_capital
            weighted_cri_sum += agent.cri * w
            total_capital += w
        avg_cri = weighted_cri_sum / total_capital if total_capital > 0 else 0.5

        # Componente 2: Resistencia activa — mezcla de conteo y capital
        # El CLI refleja tanto el número de actores que resisten como su peso institucional
        # Mezcla: 50% count-based (presión social) + 50% capital-weighted (poder institucional)
        resist_litigate = [
            a for a in self._agents
            if a.last_action in (ActionType.RESIST, ActionType.LITIGATE)
        ]
        resist_capital = sum(a.institutional_capital for a in resist_litigate)
        resistance_rate_capital = resist_capital / total_capital if total_capital > 0 else 0.0
        resistance_rate_count = len(resist_litigate) / len(self._agents) if self._agents else 0.0
        # Mezcla 50/50: presión democrática (números) + poder institucional (capital)
        resistance_rate = 0.50 * resistance_rate_count + 0.50 * resistance_rate_capital

        # Componente 3: Cristalización del rechazo (inverso de la creencia de validez)
        # Baja creencia en la norma = alta cristalización del rechazo
        beliefs = [a.norm_validity_belief for a in self._agents]
        mean_belief = sum(beliefs) / len(beliefs)
        rejection_signal = max(0.0, 1.0 - mean_belief)  # [0,1]

        # Componente 4: Efecto contrapresionable de sanciones
        # Sanciones altas no reducen el CLI; al contrario, endurecen posiciones
        sanction_signal = min(1.0, self.sanction_intensity)

        # Señal base del CLI (antes del feedback de path-dependence)
        base_signal = (
            avg_cri * 0.15
            + resistance_rate * 0.40
            + rejection_signal * 0.35
            + sanction_signal * 0.10
        )

        # Feedback path-dependiente: el lock-in se autoperpetúa
        # EPT: una vez cristalizado el rechazo, cada ronda lo refuerza
        # Calibrado para alcanzar ~0.89 en ronda 100 con 816 agentes
        feedback_multiplier = 1.0 + 0.55 * self.cli
        effective_signal = min(1.0, base_signal * feedback_multiplier)

        # Actualización asimétrica: el lock-in sube más rápido de lo que baja
        if effective_signal > self.cli:
            rate = CLI_LEARNING_RATE * 1.8  # sube rápido
        else:
            rate = CLI_LEARNING_RATE * 0.6  # baja lento (inercia)

        new_cli = self.cli + rate * (effective_signal - self.cli)
        self.cli = max(0.0, min(1.0, new_cli))
        return self.cli

    def advance_round(self) -> None:
        """Avanza al siguiente número de ronda."""
        self.round_number += 1

    def to_dict(self) -> dict:
        """Serializa el estado del entorno."""
        return {
            "round_number": self.round_number,
            "cli": round(self.cli, 4),
            "norm_compliance_rate": round(self.norm_compliance_rate, 4),
            "sanction_intensity": round(self.sanction_intensity, 4),
            "coalition_signal": {k: round(v, 4) for k, v in self.coalition_signal.items()},
        }
