"""
minds/archetypes/jurista_doctrinario.py — Perfil mental del JuristaDoctrinario.

Calibrado sobre el jurista académico argentino de la tradición iuspositivista
y neoconstitucionalista (facultades de derecho público):
- CRI base 0.91: la más alta del sistema — máxima resistencia doctrinal
- Precedent_weight máximo: el precedente ES la norma para este arquetipo
- Ideological_anchor máximo: posición doctrinal = identidad profesional
- Aristotle + Socrates: categorización formal + interrogación de premisas (pero para confirmar)

Council mapping: Aristotle (el derecho como sistema de categorías formales)
+ Socrates (interrogar pero para confirmar la doctrina previa, no para cambiarla)

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from minds.base_mind import (
    MindProfile,
    CognitiveDimension,
    AffectiveDimension,
    DoctrinalDimension,
    CouncilReference,
)


JURISTA_DOCTRINARIO_MIND = MindProfile(
    archetype_id="jurista_doctrinario",
    archetype_name="JuristaDoctrinario",
    cognitive=CognitiveDimension(
        selective_attention=0.88,   # Muy alto: sólo procesa lo que encaja en la doctrina canónica
        processing_load=0.90,       # Muy alto: domina los tecnicismos jurídicos al máximo nivel
        working_memory=0.85,        # Puede sostener complejos sistemas de precedentes simultáneos
        anchoring_bias=0.92,        # Casi máximo: el primer encuadre doctrinario es prácticamente inmovible
    ),
    affective=AffectiveDimension(
        risk_aversion=0.80,         # Muy alto: evita comprometer la coherencia del sistema doctrinal
        optimism_bias=0.20,         # Bajo: escéptico sobre el valor de las reformas
        emotional_viscosity=0.90,   # Casi máxima: la doctrina es identidad, no solo creencia
        loss_framing_sensitivity=0.85,  # Muy alto: toda reforma es pérdida de coherencia sistémica
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.95,    # Máximo: la doctrina es sagrada
        bayesian_plasticity=0.10,   # Mínima del sistema: casi incapaz de update real
        coalition_loyalty=0.45,     # Moderado: lealtad a la "escuela", no a un partido
        precedent_weight=0.98,      # Prácticamente máximo: el precedente es vinculante por naturaleza
    ),
    council_ref=CouncilReference(
        primary="aristotle",        # El derecho es un sistema de categorías que deben ser correctas
        secondary="socrates",       # Interrogar para confirmar, no para cuestionar
        weight_primary=0.70,
    ),
    description=(
        "El jurista doctrinario tiene los valores más extremos del sistema: "
        "CRI 0.91, ideological_anchor 0.95, precedent_weight 0.98, bayesian_plasticity 0.10. "
        "Es el veto player doctrinal del ecosistema: su función actual (preservar la coherencia "
        "del corpus iuris) ha suplantado completamente a su función original (asesorar sobre "
        "el derecho vigente). Aristótelicamente, clasifica cada reforma en géneros y especies "
        "para mostrar que viola la taxonomía consagrada; Socráticamentepregunta, pero para "
        "llegar a la respuesta que ya tenía antes de preguntar. "
        "Tiene el FDI más alto del sistema: su función actual es exactamente la opuesta "
        "a la que declara tener."
    ),
)
