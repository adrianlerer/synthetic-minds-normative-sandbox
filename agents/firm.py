"""
agents/firm.py — FirmAgent: empresa regulada (PYME/MiPyME argentina).

El agente con menor CRI (0.45) y mayor pragmatismo del sistema.
Opera según cálculo de costo/beneficio regulatorio, no según ideología.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.empresario_regulado import EMPRESARIO_REGULADO_MIND


class FirmAgent(BaseSyntheticAgent):
    """Agente Empresa Regulada.

    Características diferenciales:
    - CRI 0.45: baja resistencia, alta adaptabilidad
    - Bayesian_plasticity 0.75: actualiza rápido ante cambios de entorno
    - Preferencia por COMPLY cuando la norma es favorable, LOBBY cuando no
    - Sin LITIGATE ni RESIST como preferencias primarias
    """

    def __init__(
        self,
        agent_id: str,
        cri_base: float = 0.45,
        institutional_capital: float = 0.55,
        rng: random.Random | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            archetype_id="empresario_regulado",
            cri_base=cri_base,
            institutional_capital=institutional_capital,
            mind=EMPRESARIO_REGULADO_MIND,
            available_actions=[
                ActionType.COMPLY,
                ActionType.LOBBY,
                ActionType.NEGOTIATE,
                ActionType.COALESCE,
            ],
            rng=rng or random.Random(),
        )

    def decide_action(self, environment) -> ActionType:
        """Empresa: decide según cálculo de costo/beneficio regulatorio.

        Lógica:
        - Alta norma_validity_belief + CLI bajo → COMPLY (la norma vale, el sistema está estable)
        - CLI alto + baja validez → LOBBY (cambiar la norma por vías formales)
        - Norma percibida como beneficiosa (optimism_bias) → COMPLY
        - Señal empresarial positiva → COALESCE para ganar masa crítica
        """
        # Norma percibida como oportunidad + sistema estable → cumplir
        if self.norm_validity_belief > 0.65 and environment.cli < 0.60:
            self.last_action = ActionType.COMPLY
            return ActionType.COMPLY

        # CLI alto = incertidumbre sistémica → presionar por cambios via lobby
        if environment.cli > 0.75:
            self.last_action = ActionType.LOBBY
            return ActionType.LOBBY

        # Señal positiva de cámara empresaria → coalición
        coalition_signal = environment.coalition_signal.get("empresario_regulado", 0.0)
        if coalition_signal > 0.30:
            self.last_action = ActionType.COALESCE
            return ActionType.COALESCE

        return super().decide_action(environment)
