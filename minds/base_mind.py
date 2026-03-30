"""
minds/base_mind.py — MindProfile: perfil cognitivo-afectivo-doctrinal de un arquetipo.

Cada agente institucional porta un MindProfile que modula su comportamiento
más allá de los parámetros numéricos (CRI, capital, HBU). La mente tipo
captura cómo el arquetipo procesa la información normativa:
- Dimensión cognitiva: atención selectiva, carga de procesamiento, memoria de trabajo
- Dimensión afectiva: aversión al riesgo, sesgo optimista/pesimista, viscosidad emocional
- Dimensión doctrinal: anclaje ideológico, plasticidad bayesiana, lealtad coalicional

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class CognitiveDimension:
    """Dimensión cognitiva del perfil mental.

    Attributes:
        selective_attention: Qué tan selectivamente filtra la información [0,1].
            Alto = procesa sólo lo que confirma su marco previo.
        processing_load: Capacidad de procesar normas complejas [0,1].
            Alto = puede manejar alta complejidad normativa.
        working_memory: Cuántas variables normativas puede sostener [0,1].
            Afecta la capacidad de anticipar efectos de segundo orden.
        anchoring_bias: Tendencia a anclar en la primera interpretación [0,1].
    """
    selective_attention: float = 0.5
    processing_load: float = 0.5
    working_memory: float = 0.5
    anchoring_bias: float = 0.5

    def __post_init__(self):
        for attr in ['selective_attention', 'processing_load', 'working_memory', 'anchoring_bias']:
            val = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, val)))


@dataclass
class AffectiveDimension:
    """Dimensión afectiva del perfil mental.

    Attributes:
        risk_aversion: Aversión al riesgo normativo [0,1].
            Alto = evita normas inciertas aunque potencialmente beneficiosas.
        optimism_bias: Sesgo optimista sobre efectos de la norma [0,1].
            Alto = sobreestima beneficios esperados.
        emotional_viscosity: Velocidad de actualización ante información
            contradictoria [0,1]. Alto = lento en cambiar posición afectiva.
        loss_framing_sensitivity: Sensibilidad al framing de pérdidas vs ganancias [0,1].
    """
    risk_aversion: float = 0.5
    optimism_bias: float = 0.5
    emotional_viscosity: float = 0.5
    loss_framing_sensitivity: float = 0.5

    def __post_init__(self):
        for attr in ['risk_aversion', 'optimism_bias', 'emotional_viscosity', 'loss_framing_sensitivity']:
            val = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, val)))


@dataclass
class DoctrinalDimension:
    """Dimensión doctrinal del perfil mental.

    Attributes:
        ideological_anchor: Fuerza del anclaje ideológico [0,1].
            Alto = muy resistente a cambiar posición doctrinaria.
        bayesian_plasticity: Capacidad de actualización bayesiana real [0,1].
            Complementario (pero no opuesto) al CRI del agente base.
        coalition_loyalty: Peso de la señal grupal vs. el análisis individual [0,1].
            Alto = sigue a la coalición por encima del propio análisis.
        precedent_weight: Cuánto pesan los precedentes sobre la nueva norma [0,1].
    """
    ideological_anchor: float = 0.5
    bayesian_plasticity: float = 0.5
    coalition_loyalty: float = 0.5
    precedent_weight: float = 0.5

    def __post_init__(self):
        for attr in ['ideological_anchor', 'bayesian_plasticity', 'coalition_loyalty', 'precedent_weight']:
            val = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, val)))


@dataclass
class CouncilReference:
    """Referencia al miembro del Council que inspira este arquetipo.

    Permite consultar el council-of-high-intelligence para deliberaciones
    complejas en las que el agente necesita razonar sobre normas ambiguas.
    """
    primary: str    # Miembro principal (e.g., "aristotle", "machiavelli")
    secondary: str  # Miembro secundario (modulador)
    weight_primary: float = 0.7  # Peso relativo del miembro principal


@dataclass
class MindProfile:
    """Perfil mental completo de un arquetipo institucional.

    Integra las tres dimensiones (cognitiva, afectiva, doctrinal) con
    una referencia al Council y metadatos del arquetipo.

    Args:
        archetype_id: Identificador único del arquetipo.
        archetype_name: Nombre descriptivo (e.g., "JuezCSJN").
        cognitive: Dimensión cognitiva.
        affective: Dimensión afectiva.
        doctrinal: Dimensión doctrinal.
        council_ref: Referencia al Council (para deliberaciones complejas).
        tribe_encoding: Vector de encoding cortical de TribeV2 (opcional).
            Si está presente, sobreescribe parcialmente cognitive.
        description: Descripción en lenguaje natural del perfil.
    """
    archetype_id: str
    archetype_name: str
    cognitive: CognitiveDimension = field(default_factory=CognitiveDimension)
    affective: AffectiveDimension = field(default_factory=AffectiveDimension)
    doctrinal: DoctrinalDimension = field(default_factory=DoctrinalDimension)
    council_ref: Optional[CouncilReference] = None
    tribe_encoding: Optional[list[float]] = None
    description: str = ""

    def effective_cri_modifier(self) -> float:
        """Retorna un modificador multiplicativo del CRI base del agente.

        El CRI base (del agente 816) se modifica por la mente tipo:
        - Alta viscosidad emocional y alto anclaje ideológico → multiplican el CRI
        - Alta plasticidad bayesiana → reduce el CRI efectivo

        Returns:
            Modificador en el rango [0.5, 1.5].
        """
        modifier = 1.0
        modifier += 0.25 * self.affective.emotional_viscosity
        modifier += 0.20 * self.doctrinal.ideological_anchor
        modifier -= 0.20 * self.doctrinal.bayesian_plasticity
        modifier += 0.10 * self.cognitive.anchoring_bias
        return max(0.5, min(1.5, modifier))

    def norm_processing_score(self, norm_complexity: float) -> float:
        """Evalúa qué tan bien este arquetipo puede procesar una norma dada.

        Args:
            norm_complexity: Complejidad de la norma [0,1].

        Returns:
            Score de procesamiento [0,1]. Bajo = procesa mal la norma.
        """
        base = self.cognitive.processing_load
        # Las normas complejas abruman a los de baja memoria de trabajo
        memory_penalty = max(0, norm_complexity - self.cognitive.working_memory) * 0.5
        # El sesgo de atención selectiva filtra información compleja
        attention_filter = self.cognitive.selective_attention * norm_complexity * 0.3
        return max(0.0, min(1.0, base - memory_penalty - attention_filter))

    def coalition_signal_weight(self, rng: random.Random) -> float:
        """Peso efectivo de la señal coalicional en la decisión.

        Args:
            rng: Generador aleatorio (para varianza situacional).

        Returns:
            Peso [0,1] que se aplicará a la señal del grupo.
        """
        base = self.doctrinal.coalition_loyalty
        noise = rng.gauss(0, 0.05)
        return max(0.0, min(1.0, base + noise))

    def to_dict(self) -> dict:
        """Serializa el perfil a diccionario."""
        return {
            "archetype_id": self.archetype_id,
            "archetype_name": self.archetype_name,
            "cognitive": {
                "selective_attention": self.cognitive.selective_attention,
                "processing_load": self.cognitive.processing_load,
                "working_memory": self.cognitive.working_memory,
                "anchoring_bias": self.cognitive.anchoring_bias,
            },
            "affective": {
                "risk_aversion": self.affective.risk_aversion,
                "optimism_bias": self.affective.optimism_bias,
                "emotional_viscosity": self.affective.emotional_viscosity,
                "loss_framing_sensitivity": self.affective.loss_framing_sensitivity,
            },
            "doctrinal": {
                "ideological_anchor": self.doctrinal.ideological_anchor,
                "bayesian_plasticity": self.doctrinal.bayesian_plasticity,
                "coalition_loyalty": self.doctrinal.coalition_loyalty,
                "precedent_weight": self.doctrinal.precedent_weight,
            },
            "council_primary": self.council_ref.primary if self.council_ref else None,
            "council_secondary": self.council_ref.secondary if self.council_ref else None,
            "description": self.description,
        }
