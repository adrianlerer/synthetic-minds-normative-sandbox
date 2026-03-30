"""
agents/base_agent.py — BaseSyntheticAgent: agente 816 + MindProfile.

Extiende el BaseLegalAgent del repo 816-agentes-institucionales-argentinos-EPT
con la capa de mente tipo (MindProfile). La integración es por composición:
el agente tiene una mente, no es una mente.

La mente modula pero no reemplaza los mecanismos CRI/HBU:
- CRI efectivo = CRI_base × mind.effective_cri_modifier()
- HBU: la plasticidad bayesiana de la mente amplifica o amortigua el update
- Decisión final: sigue siendo del agente, pero el MindProfile sesga la utilidad

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import random
from enum import Enum
from minds.base_mind import MindProfile


class ActionType(Enum):
    """Acciones disponibles para agentes institucionales."""
    COMPLY = "comply"               # Cumplir la norma
    RESIST = "resist"               # Resistir pasivamente
    LITIGATE = "litigate"           # Accionar judicialmente
    LOBBY = "lobby"                 # Lobbying legislativo
    NEGOTIATE = "negotiate"         # Negociación directa
    DEFECT = "defect"               # Defección de coalición
    COALESCE = "coalesce"           # Unirse a coalición


ACTION_COSTS = {
    ActionType.COMPLY: 0.05,
    ActionType.RESIST: 0.10,
    ActionType.LITIGATE: 0.25,
    ActionType.LOBBY: 0.20,
    ActionType.NEGOTIATE: 0.15,
    ActionType.DEFECT: 0.30,
    ActionType.COALESCE: 0.12,
}


class BaseSyntheticAgent:
    """Agente institucional sintético con mente tipo integrada.

    Combina la mecánica CRI/HBU del repo 816-agentes con un MindProfile
    que modula el CRI efectivo, la sensibilidad bayesiana y la utilidad
    percibida de cada acción.

    Attributes:
        agent_id: Identificador único.
        archetype_id: Tipo de arquetipo (e.g., "juez_csjn").
        cri_base: CRI base sin modulación de mente [0,1].
        institutional_capital: Capital institucional [0,1].
        norm_validity_belief: Creencia bayesiana sobre validez de normas [0,1].
        mind: MindProfile del arquetipo.
        available_actions: Lista de acciones disponibles.
        rng: Generador aleatorio con seed controlada.
        last_action: Última acción tomada.
        fitness_last_delta: Cambio de fitness en la última ronda.
        doctrinal_memory: Historial de posiciones doctrinales.
    """

    def __init__(
        self,
        agent_id: str,
        archetype_id: str,
        cri_base: float,
        institutional_capital: float,
        mind: MindProfile,
        available_actions: list[ActionType],
        rng: random.Random,
    ):
        self.agent_id = agent_id
        self.archetype_id = archetype_id
        self.cri_base = max(0.0, min(1.0, cri_base))
        self.institutional_capital = max(0.0, min(1.0, institutional_capital))
        self.norm_validity_belief = 0.70    # prior inicial
        self.mind = mind
        self.available_actions = available_actions
        self.rng = rng

        # Estado
        self.last_action: ActionType = ActionType.COMPLY
        self.fitness_last_delta: float = 0.0
        self.doctrinal_memory: list[str] = []
        self.n_supporters: int = 0
        self.fitness_history: list[float] = []

    @property
    def cri(self) -> float:
        """CRI efectivo: base modulado por la mente tipo."""
        return max(0.0, min(1.0, self.cri_base * self.mind.effective_cri_modifier()))

    def perceived_utility(self, action: ActionType, environment) -> float:
        """Calcula la utilidad percibida de una acción, modulada por la mente.

        La mente afecta la utilidad percibida de tres formas:
        1. Aversión al riesgo: penaliza acciones costosas
        2. Sesgo optimista: infla la utilidad esperada de la acción preferida
        3. Señal coalicional: agrega utilidad si la coalición prefiere esa acción

        Args:
            action: Acción a evaluar.
            environment: Estado del entorno.

        Returns:
            Utilidad percibida [float, puede ser negativa].
        """
        base_cost = ACTION_COSTS.get(action, 0.20)
        base_utility = self.norm_validity_belief - base_cost * self.cri

        # Modulación por aversión al riesgo
        risk_penalty = self.mind.affective.risk_aversion * base_cost * 0.5
        base_utility -= risk_penalty

        # Sesgo optimista si la acción es COMPLY (default safe)
        if action == ActionType.COMPLY:
            base_utility += self.mind.affective.optimism_bias * 0.10

        # Peso de señal coalicional
        coalition_weight = self.mind.coalition_signal_weight(self.rng)
        coalition_signal = getattr(environment, 'coalition_signal', {}).get(
            self.archetype_id, 0.0
        )
        base_utility += coalition_weight * coalition_signal * 0.15

        # Loss framing: si la norma amenaza capital, amplifica la resistencia
        if action in (ActionType.RESIST, ActionType.LITIGATE):
            threat = max(0, 0.5 - self.institutional_capital)
            base_utility += self.mind.affective.loss_framing_sensitivity * threat * 0.20

        return base_utility

    def decide_action(self, environment) -> ActionType:
        """Decide la acción óptima según utilidad percibida.

        Implementación base: maximiza utilidad percibida con ruido
        proporcional a la baja capacidad de procesamiento.

        Las subclases pueden sobreescribir para lógica arquetípica específica.

        Args:
            environment: LegalEnvironment con el estado actual.

        Returns:
            ActionType seleccionada.
        """
        utilities = {}
        for action in self.available_actions:
            u = self.perceived_utility(action, environment)
            # Añadir ruido inversamente proporcional al processing_load de la mente
            noise_scale = (1.0 - self.mind.cognitive.processing_load) * 0.10
            noise = self.rng.gauss(0, noise_scale)
            utilities[action] = u + noise

        best_action = max(utilities, key=utilities.get)
        self.last_action = best_action
        return best_action

    def hbu_update(self, observed_compliance: float, observed_sanction: float) -> None:
        """Heteronomous Bayesian Update de la creencia de validez normativa.

        Hereda la lógica del repo 816-agentes, modulada por la plasticidad
        bayesiana de la mente tipo.

        Args:
            observed_compliance: Tasa de cumplimiento observada [0,1].
            observed_sanction: Intensidad de sanción observada [0,1].
        """
        # Update base
        likelihood_valid = (observed_compliance * 0.7 + observed_sanction * 0.3)
        likelihood_invalid = 1 - likelihood_valid

        prior = self.norm_validity_belief
        posterior_num = likelihood_valid * prior
        posterior_den = posterior_num + likelihood_invalid * (1 - prior)
        raw_posterior = posterior_num / posterior_den if posterior_den > 0 else prior

        # La plasticidad bayesiana de la mente amplifica o amortigua el update
        plasticity = self.mind.doctrinal.bayesian_plasticity
        # Alta plasticidad → acepta el update; baja plasticidad → se queda en el prior
        effective_update = prior + plasticity * (raw_posterior - prior)

        # El CRI add inercia adicional
        final_belief = (
            effective_update * (1 - self.cri * 0.3)
            + prior * (self.cri * 0.3)
        )
        self.norm_validity_belief = max(0.0, min(1.0, final_belief))

    def update_fitness(self, delta: float) -> None:
        """Actualiza el capital institucional y registra el delta.

        Args:
            delta: Cambio de capital [-1, 1].
        """
        self.fitness_last_delta = delta
        self.institutional_capital = max(0.0, min(1.0, self.institutional_capital + delta))
        self.fitness_history.append(self.institutional_capital)
