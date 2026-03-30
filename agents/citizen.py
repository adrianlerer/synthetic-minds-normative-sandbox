"""
agents/citizen.py — CitizenAgent: ciudadano informado.

El agente más numeroso (500) y con mayor bayesian_plasticity (0.78) del sistema.
Su comportamiento agregado determina el fitness L3 del ecosistema.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.ciudadano_informado import CIUDADANO_INFORMADO_MIND


class CitizenAgent(BaseSyntheticAgent):
    """Agente Ciudadano Informado.

    Características diferenciales:
    - CRI 0.30: mínimo del sistema, máxima adaptabilidad
    - Bayesian_plasticity 0.78: el más actualizable
    - Solo 3 acciones: COMPLY, RESIST, DEFECT
    - Muy sensible al comportamiento agregado de los demás
    """

    def __init__(
        self,
        agent_id: str,
        cri_base: float = 0.30,
        institutional_capital: float = 0.20,
        rng: random.Random | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            archetype_id="ciudadano_informado",
            cri_base=cri_base,
            institutional_capital=institutional_capital,
            mind=CIUDADANO_INFORMADO_MIND,
            available_actions=[
                ActionType.COMPLY,
                ActionType.RESIST,
                ActionType.DEFECT,
            ],
            rng=rng or random.Random(),
        )

    def decide_action(self, environment) -> ActionType:
        """Ciudadano: sigue la mayoría observada (conformismo adaptativo).

        Lógica:
        - Alta compliance_rate observada → COMPLY (los demás cumplen, yo cumplo)
        - Baja compliance_rate + CLI alto → RESIST (sistema en crisis, resistir)
        - CLI extremadamente alto → DEFECT (deserción ante colapso sistémico)
        - Resto: utilidad percibida base (pero con alta plasticidad bayesiana)
        """
        # Comportamiento mayoritario observable
        if environment.norm_compliance_rate > 0.65:
            # La mayoría cumple → efecto manada hacia cumplimiento
            if self.rng.random() < 0.70:
                self.last_action = ActionType.COMPLY
                return ActionType.COMPLY

        # Colapso de compliance + alta tensión → deserción
        if environment.cli > 0.88 and environment.norm_compliance_rate < 0.35:
            self.last_action = ActionType.DEFECT
            return ActionType.DEFECT

        # Resistencia difusa cuando el sistema está muy tenso
        if environment.cli > 0.75 and self.norm_validity_belief < 0.40:
            if self.rng.random() < 0.55:
                self.last_action = ActionType.RESIST
                return ActionType.RESIST

        return super().decide_action(environment)
