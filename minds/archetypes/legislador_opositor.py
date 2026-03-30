"""
minds/archetypes/legislador_opositor.py — Perfil mental del LegisladorOpositor.

Calibrado sobre patrones históricos del bloque opositor parlamentario argentino:
- CRI base 0.55: resistencia moderada, pero alta capacidad de update (bayesian_plasticity)
- Bayesian_plasticity alto: actualiza genuinamente ante evidencia nueva (inusual)
- Coalition_loyalty moderada: la oposición tiene fracturas internas frecuentes
- Skeptical: bajo optimism_bias, alto processing_load — analiza más, confía menos

Council mapping: Socrates (interrogación socrática, cuestionamiento de premisas)
+ Feynman (empirismo riguroso, rechazo de argumentos sin evidencia)

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


LEGISLADOR_OPOSITOR_MIND = MindProfile(
    archetype_id="legislador_opositor",
    archetype_name="LegisladorOpositor",
    cognitive=CognitiveDimension(
        selective_attention=0.45,   # Más abierto a información diversa (no solo confirmatoria)
        processing_load=0.68,       # Procesamiento alto: analiza normas con más cuidado
        working_memory=0.65,        # Puede sostener múltiples dimensiones del debate
        anchoring_bias=0.40,        # Bajo anclaje: dispuesto a cambiar marco si hay razones
    ),
    affective=AffectiveDimension(
        risk_aversion=0.55,         # Moderado: en oposición el riesgo es asimétrico
        optimism_bias=0.20,         # Bajo: escéptico sobre efectos positivos de la norma oficial
        emotional_viscosity=0.45,   # Rápido en cambiar posición afectiva ante nueva evidencia
        loss_framing_sensitivity=0.65,  # Alto: muy sensible al framing de "lo que se pierde"
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.50,    # Moderado: tiene principios pero los somete a debate
        bayesian_plasticity=0.72,   # Alta: genuinamente capaz de actualizar creencias
        coalition_loyalty=0.48,     # Moderado-bajo: la oposición no tiene disciplina de bloque
        precedent_weight=0.58,      # Moderado: usa precedentes pero no como única fuente
    ),
    council_ref=CouncilReference(
        primary="socrates",         # Interrogación permanente de las premisas
        secondary="feynman",        # Si no puedes medirlo, no lo afirmes
        weight_primary=0.60,
    ),
    description=(
        "El legislador opositor tiene el perfil cognitivo más abierto del sistema: "
        "su bayesian_plasticity alta y su bajo anclaje lo hacen capaz de update genuino. "
        "Paradójicamente, esta apertura lo hace políticamente volátil: puede fracturar "
        "la coalición opositora cuando la evidencia lo convence. Socráticamentepregunta "
        "todo; Feynmanianamente rechaza los argumentos de autoridad. Su bajo optimism_bias "
        "funciona como radar de falsas promesas normativas — y como generador de narrativas "
        "de riesgo que amplifican el FDI de la norma impugnada."
    ),
)
