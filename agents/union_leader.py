"""
agents/union_leader.py — UnionLeaderAgent: dirigente gremial (CGT/CTA).

El agente con mayor coalition_loyalty (0.92) y CRI (0.88) del sistema.
Opera casi exclusivamente con framing de pérdida y señal gremial.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.dirigente_gremial import DIRIGENTE_GREMIAL_MIND


class UnionLeaderAgent(BaseSyntheticAgent):
    """Agente Dirigente Gremial.

    Características diferenciales:
    - CRI 0.88: segundo más alto del sistema
    - coalition_loyalty 0.92: casi siempre sigue la señal gremial
    - Preferencia fuerte por RESIST, LITIGATE, COALESCE
    - Loss_framing 0.90: percibe casi cualquier cambio como amenaza
    """

    def __init__(
        self,
        agent_id: str,
        cri_base: float = 0.88,
        institutional_capital: float = 0.78,
        coalition_id: str = "cgt_cta",
        rng: random.Random | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            archetype_id="dirigente_gremial",
            cri_base=cri_base,
            institutional_capital=institutional_capital,
            mind=DIRIGENTE_GREMIAL_MIND,
            available_actions=[
                ActionType.RESIST,
                ActionType.LITIGATE,
                ActionType.LOBBY,
                ActionType.COALESCE,
                ActionType.NEGOTIATE,
            ],
            rng=rng or random.Random(),
        )
        self.coalition_id = coalition_id

    def decide_action(self, environment) -> ActionType:
        """Dirigente gremial: máxima lealtad a la señal gremial.

        Lógica:
        - Señal gremial negativa (resistencia) → RESIST o LITIGATE con alta prob.
        - CLI en escalada → LITIGATE (usa el sistema judicial como herramienta)
        - Norma percibida como inválida + capital alto → LITIGATE
        - Resto: utilidad percibida con fuerte peso de loss_framing
        """
        coalition_signal = environment.coalition_signal.get("dirigente_gremial", -0.85)

        # La señal gremial es casi siempre negativa para reformas laborales
        if coalition_signal < -0.50:
            loyalty = self.mind.doctrinal.coalition_loyalty  # 0.92
            if self.rng.random() < loyalty:
                # Elegir entre RESIST y LITIGATE según fase del CLI
                if environment.cli > 0.65:
                    self.last_action = ActionType.LITIGATE
                    return ActionType.LITIGATE
                else:
                    self.last_action = ActionType.RESIST
                    return ActionType.RESIST

        # CLI en escalada + baja validez percibida → litigio como herramienta
        if environment.cli > 0.75 and self.norm_validity_belief < 0.45:
            self.last_action = ActionType.LITIGATE
            return ActionType.LITIGATE

        # Coalición útil cuando hay suficientes simpatizantes
        if environment.coalition_signal.get("legislador_opositor", 0) < -0.30:
            self.last_action = ActionType.COALESCE
            return ActionType.COALESCE

        return super().decide_action(environment)
