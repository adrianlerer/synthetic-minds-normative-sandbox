"""
minds/archetypes/juez_csjn.py — Perfil mental del JuezCSJN.

Calibrado sobre patrones históricos de la Corte Suprema argentina:
- Alta resistencia al cambio doctrinal (CRI base 0.82)
- Anclaje fuerte en precedentes (stare decisis informal)
- Procesamiento formal elevado pero selectividad atencional hacia
  argumentos de legitimidad procedimental más que sustantiva
- Lealtad coalicional moderada (la CSJN es corporación pero no bloque político)

Council mapping: Aristotle (estructura, categorías) + Aurelius (moral grounding,
resistencia estoica al cambio externo)

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


JUEZ_CSJN_MIND = MindProfile(
    archetype_id="juez_csjn",
    archetype_name="JuezCSJN",
    cognitive=CognitiveDimension(
        selective_attention=0.78,   # Filtra fuertemente: ve lo que encaja en doctrina previa
        processing_load=0.85,       # Alta capacidad técnico-jurídica
        working_memory=0.80,        # Puede sostener múltiples precedentes
        anchoring_bias=0.82,        # Primer encuadre doctrinario es muy difícil de mover
    ),
    affective=AffectiveDimension(
        risk_aversion=0.75,         # Evita declarar inconstitucionalidad si puede
        optimism_bias=0.30,         # Pesimista sobre reformas: "ya lo hemos visto antes"
        emotional_viscosity=0.80,   # Muy lento en cambiar posición una vez formada
        loss_framing_sensitivity=0.65,  # Sensible al framing de "pérdida institucional"
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.85,    # Fuerte anclaje en doctrina constitucionalista clásica
        bayesian_plasticity=0.25,   # Muy baja: actualiza sólo ante cambios constitucionales
        coalition_loyalty=0.55,     # Moderada: acuerdos de Corte vs. votos individuales
        precedent_weight=0.90,      # El precedente es casi determinante
    ),
    council_ref=CouncilReference(
        primary="aristotle",        # Categoriza, clasifica, busca la genus de cada norma
        secondary="aurelius",       # Estoicismo institucional: resiste presiones externas
        weight_primary=0.65,
    ),
    description=(
        "El juez de la CSJN es un actor de altísima resistencia doctrinal. "
        "Su mente tipo prioriza la categorización formal (¿qué tipo de norma es esta?) "
        "sobre el análisis de consecuencias. Opera bajo el principio de que la "
        "estabilidad institucional vale más que la corrección sustantiva de una reforma. "
        "Dawkinsianamente: su CRI elevado es la estrategia evolucionariamente estable "
        "de un actor cuya función actual (veto player constitucional) diverge cada vez "
        "más de su función original (control de constitucionalidad puntual)."
    ),
)
