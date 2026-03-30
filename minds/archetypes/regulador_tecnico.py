"""
minds/archetypes/regulador_tecnico.py — Perfil mental del ReguladorTécnico.

Calibrado sobre el técnico de entes reguladores argentinos (AFIP, INDEC, BCRA,
Ministerio de Trabajo):
- CRI base 0.70: resistencia moderada-alta — defiende el marco regulatorio existente
- Processing_load muy alto: máximo del sistema — analiza normas a nivel técnico-jurídico
- Coalition_loyalty bajo: el regulador técnico tiene autonomía relativa respecto a política
- Feynman + Aristotle: empirismo técnico + taxonomía formal de la norma

Council mapping: Feynman (si no puedes calcularlo, no lo implementes)
+ Aristotle (categorizar correctamente antes de regular)

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


REGULADOR_TECNICO_MIND = MindProfile(
    archetype_id="regulador_tecnico",
    archetype_name="ReguladorTécnico",
    cognitive=CognitiveDimension(
        selective_attention=0.60,   # Moderado: atiende principalmente a la coherencia técnica
        processing_load=0.92,       # Muy alto: máxima capacidad de procesamiento normativo
        working_memory=0.88,        # Muy alto: puede sostener múltiples marcos regulatorios
        anchoring_bias=0.65,        # Moderado-alto: primer análisis técnico es muy influyente
    ),
    affective=AffectiveDimension(
        risk_aversion=0.68,         # Alto: el regulador teme la inconsistencia sistémica
        optimism_bias=0.35,         # Bajo: el técnico es cauteloso sobre los efectos de cualquier reforma
        emotional_viscosity=0.58,   # Moderado: cambia si hay evidencia técnica, no por presión política
        loss_framing_sensitivity=0.50,  # Moderado: procesa tanto pérdidas como ganancias técnicas
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.55,    # Moderado: tiene doctrina regulatoria pero la somete a evidencia
        bayesian_plasticity=0.62,   # Moderado-alto: actualiza bien ante cambios técnicos
        coalition_loyalty=0.20,     # Bajo: el técnico tiene relativa independencia política
        precedent_weight=0.72,      # Alto: la coherencia sistémica requiere respetar el marco previo
    ),
    council_ref=CouncilReference(
        primary="feynman",          # Si no puedes medirlo, no lo afirmes en una regulación
        secondary="aristotle",      # Categoriza primero, regula después
        weight_primary=0.58,
    ),
    description=(
        "El regulador técnico tiene el mayor processing_load del sistema (0.92): "
        "es el único actor que puede leer la norma en su complejidad técnica completa. "
        "Feynmanianamente rechaza las regulaciones que no pueden ser operacionalizadas; "
        "Aristótelicamente clasifica antes de regular. Su baja coalition_loyalty (0.20) "
        "lo hace relativamente autónomo respecto a la presión política, pero su "
        "risk_aversion alto lo hace conservador: prefiere el statu quo técnico a la "
        "incertidumbre de una reforma mal especificada. Es quien detecta primero "
        "las inconsistencias de la norma — y también quien tiene menos incentivos "
        "para publicarlas."
    ),
)
