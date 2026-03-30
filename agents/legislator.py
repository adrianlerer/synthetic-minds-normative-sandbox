"""
agents/legislator.py — LegislatorAgent: legislador (oficialista u opositor).

Hereda de BaseSyntheticAgent. Acepta un parámetro `is_ruling_party` para
distinguir oficialismo de oposición, importando el MindProfile correspondiente.

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from agents.base_agent import BaseSyntheticAgent, ActionType
from minds.archetypes.legislador_oficialista import LEGISLADOR_OFICIALISTA_MIND
from minds.archetypes.legislador_opositor import LEGISLADOR_OPOSITOR_MIND


class LegislatorAgent(BaseSyntheticAgent):
    """Agente Legislador (oficialista u opositor).

    Características diferenciales:
    - Oficialista: prefiere LOBBY y COALESCE, rara vez LITIGATE
    - Opositor: prefiere RESIST y LITIGATE, con mayor plasticidad bayesiana
    - Ambos: muy sensibles a la señal coalicional de su bloque
    """

    def __init__(
        self,
        agent_id: str,
        is_ruling_party: bool = True,
        cri_base: float | None = None,
        institutional_capital: float = 0.65,
        rng: random.Random | None = None,
    ):
        self.is_ruling_party = is_ruling_party

        if is_ruling_party:
            mind = LEGISLADOR_OFICIALISTA_MIND
            archetype_id = "legislador_oficialista"
            default_cri = 0.61
            available_actions = [
                ActionType.COMPLY,
                ActionType.LOBBY,
                ActionType.COALESCE,
                ActionType.NEGOTIATE,
            ]
        else:
            mind = LEGISLADOR_OPOSITOR_MIND
            archetype_id = "legislador_opositor"
            default_cri = 0.55
            available_actions = [
                ActionType.RESIST,
                ActionType.LITIGATE,
                ActionType.LOBBY,
                ActionType.NEGOTIATE,
                ActionType.DEFECT,
            ]

        super().__init__(
            agent_id=agent_id,
            archetype_id=archetype_id,
            cri_base=cri_base if cri_base is not None else default_cri,
            institutional_capital=institutional_capital,
            mind=mind,
            available_actions=available_actions,
            rng=rng or random.Random(),
        )

    def decide_action(self, environment) -> ActionType:
        """Legislador: muy sensible a la señal coalicional de su bloque.

        Si la señal del bloque es fuerte (|signal| > 0.60), sigue al bloque
        con alta probabilidad (coalition_loyalty).
        """
        coalition_signal = environment.coalition_signal.get(self.archetype_id, 0.0)

        # Señal de bloque fuerte + alta lealtad → seguir al bloque
        if abs(coalition_signal) > 0.60:
            loyalty = self.mind.doctrinal.coalition_loyalty
            if self.rng.random() < loyalty:
                if coalition_signal > 0:
                    # Bloque a favor → LOBBY o COMPLY según posición
                    action = ActionType.LOBBY if ActionType.LOBBY in self.available_actions else ActionType.COMPLY
                else:
                    # Bloque en contra → RESIST o LITIGATE
                    action = ActionType.RESIST if ActionType.RESIST in self.available_actions else ActionType.LOBBY
                self.last_action = action
                return action

        return super().decide_action(environment)
