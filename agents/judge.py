"""
agents/judge.py — JudgeAgent: juez de la CSJN con MindProfile Aristotle+Aurelius.

Hereda de BaseSyntheticAgent e importa su MindProfile correspondiente.
Lógica específica: prioriza LITIGATE/RESIST cuando la norma amenaza precedentes,
COMPLY solo cuando el CLI está en zona de "consolidación institucional".

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.juez_csjn import JUEZ_CSJN_MIND


class JudgeAgent(BaseSyntheticAgent):
    """Agente Juez CSJN.

    Características diferenciales:
    - Resistencia doctrinal alta (CRI 0.82, modulado al alza por la mente)
    - Prioriza LITIGATE cuando CLI > 0.80 y norm_validity_belief < 0.5
    - Prioriza RESIST cuando hay señal coalicional negativa fuerte
    - Casi nunca DEFECT o LOBBY (no son acciones de su rol institucional)
    """

    def __init__(
        self,
        agent_id: str,
        cri_base: float = 0.82,
        institutional_capital: float = 0.90,
        rng: random.Random | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            archetype_id="juez_csjn",
            cri_base=cri_base,
            institutional_capital=institutional_capital,
            mind=JUEZ_CSJN_MIND,
            available_actions=[
                ActionType.COMPLY,
                ActionType.RESIST,
                ActionType.LITIGATE,
                ActionType.NEGOTIATE,
            ],
            rng=rng or random.Random(),
        )

    def decide_action(self, environment) -> ActionType:
        """Juez: prioriza LITIGATE cuando la norma amenaza precedentes.

        Lógica específica:
        - CLI > 0.80 + norm_validity_belief < 0.5 → LITIGATE (activa control constitucional)
        - norm_validity_belief < 0.35 + precedent_weight alto → RESIST (posición previa)
        - CLI < 0.40 → COMPLY (norma en consolidación, no hay batalla a dar)
        - Resto: utilidad percibida estándar de BaseSyntheticAgent
        """
        # Control constitucional activo: alta tensión sistémica + baja validez percibida
        if environment.cli > 0.80 and self.norm_validity_belief < 0.50:
            self.last_action = ActionType.LITIGATE
            return ActionType.LITIGATE

        # Resistencia doctrinal: muy baja creencia en validez
        if self.norm_validity_belief < 0.35 and self.mind.doctrinal.precedent_weight > 0.80:
            self.last_action = ActionType.RESIST
            return ActionType.RESIST

        # Zona de consolidación: CLI bajo, el sistema está en equilibrio
        if environment.cli < 0.40:
            self.last_action = ActionType.COMPLY
            return ActionType.COMPLY

        # Default: utilidad percibida
        return super().decide_action(environment)
