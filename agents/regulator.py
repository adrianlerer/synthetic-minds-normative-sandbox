"""
agents/regulator.py — RegulatorAgent: regulador técnico de entes argentinos.

El agente con mayor processing_load (0.92) y menor coalition_loyalty (0.20).
Opera con relativa autonomía política, guiado por coherencia técnica del sistema.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.regulador_tecnico import REGULADOR_TECNICO_MIND


class RegulatorAgent(BaseSyntheticAgent):
    """Agente Regulador Técnico.

    Características diferenciales:
    - processing_load 0.92: mayor capacidad de análisis normativo
    - coalition_loyalty 0.20: relativa autonomía política
    - Preferencia por NEGOTIATE como herramienta primaria
    - RESIST ante inconsistencias técnicas graves
    """

    def __init__(
        self,
        agent_id: str,
        cri_base: float = 0.70,
        institutional_capital: float = 0.65,
        rng: random.Random | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            archetype_id="regulador_tecnico",
            cri_base=cri_base,
            institutional_capital=institutional_capital,
            mind=REGULADOR_TECNICO_MIND,
            available_actions=[
                ActionType.COMPLY,
                ActionType.RESIST,
                ActionType.NEGOTIATE,
                ActionType.LOBBY,
            ],
            rng=rng or random.Random(),
        )

    def decide_action(self, environment) -> ActionType:
        """Regulador: prioriza coherencia técnica del sistema.

        Lógica:
        - Norma percibida como técnicamente coherente (alta validez) + CLI bajo → COMPLY
        - Inconsistencia técnica (varianza alta en señales) → NEGOTIATE
        - CLI muy alto = crisis sistémica → LOBBY por reforma técnica
        - Sanción alta = sistema funcionando → COMPLY (señal de efectividad)
        """
        # Sistema con sanciones efectivas = norma con dientes técnicos → cumplir
        if environment.sanction_intensity > 0.50 and self.norm_validity_belief > 0.60:
            self.last_action = ActionType.COMPLY
            return ActionType.COMPLY

        # Crisis sistémica → presión por mejora técnica de la norma
        if environment.cli > 0.82:
            self.last_action = ActionType.LOBBY
            return ActionType.LOBBY

        # Inconsistencia (señales contradictorias) → negociar antes de resistir
        coalition_variance = len(environment.coalition_signal) > 3
        if coalition_variance and self.norm_validity_belief < 0.55:
            self.last_action = ActionType.NEGOTIATE
            return ActionType.NEGOTIATE

        # Norma técnicamente incoherente (muy baja validez percibida por técnico)
        if self.norm_validity_belief < 0.30:
            self.last_action = ActionType.RESIST
            return ActionType.RESIST

        return super().decide_action(environment)
