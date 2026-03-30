"""
minds/archetypes/ciudadano_informado.py — Perfil mental del CiudadanoInformado.

Calibrado sobre el ciudadano con acceso a información y opinión formada
(quintil superior de engagement cívico, según CEDEC/Latinobarómetro):
- CRI base 0.30: muy baja resistencia — el ciudadano adapta su comportamiento
- Selective_attention bajo: procesa información de múltiples fuentes
- Bayesian_plasticity alto: genuinamente receptivo a nueva información
- Watts + Lao Tzu: observa el sistema desde afuera con curiosidad, no con combate

Council mapping: Watts (observación de sistemas complejos sin apego a resultado)
+ Lao Tzu (wu wei — actuar desde la comprensión del sistema, no contra él)

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


CIUDADANO_INFORMADO_MIND = MindProfile(
    archetype_id="ciudadano_informado",
    archetype_name="CiudadanoInformado",
    cognitive=CognitiveDimension(
        selective_attention=0.22,   # Muy bajo: atiende a múltiples fuentes, no filtra ideológicamente
        processing_load=0.48,       # Moderado: entiende la norma a nivel general, no técnico-jurídico
        working_memory=0.45,        # Puede sostener 2-3 argumentos centrales
        anchoring_bias=0.35,        # Bajo-moderado: puede cambiar de marco si se le presentan bien
    ),
    affective=AffectiveDimension(
        risk_aversion=0.60,         # Moderado-alto: el ciudadano teme cambios en la relación laboral
        optimism_bias=0.42,         # Moderado: esperanza moderada en que la reforma mejore algo
        emotional_viscosity=0.40,   # Relativamente ágil: cambia opinión más rápido que las élites
        loss_framing_sensitivity=0.70,  # Alto: muy sensible al "te van a sacar derechos"
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.30,    # Bajo: opinión pública es más volátil que la élite
        bayesian_plasticity=0.78,   # Alta: genuinamente receptivo — el más actualizable del sistema
        coalition_loyalty=0.25,     # Bajo: el ciudadano no tiene disciplina de bloque
        precedent_weight=0.28,      # Bajo: no conoce los precedentes jurídicos en detalle
    ),
    council_ref=CouncilReference(
        primary="watts",            # Observa el sistema como fenómeno, no como amenaza personal
        secondary="lao_tzu",        # No forzar: fluir con el sistema cuando posible
        weight_primary=0.55,
    ),
    description=(
        "El ciudadano informado es el agente con mayor bayesian_plasticity del sistema (0.78) "
        "y el menor CRI base (0.30). Su comportamiento es el más sensible a las señales "
        "del entorno: si observa compliance generalizado, se suma; si observa resistencia, "
        "se retira. Watts le da la capacidad de observar el sistema con desapego relativo; "
        "Lao Tzu le enseña que la resistencia activa tiene costos que no puede pagar. "
        "Con 500 agentes de este tipo, la distribución de creencias de la ciudadanía "
        "actúa como termómetro del CLI: cuando el ciudadano deja de creer en la norma, "
        "el L3 colapsa."
    ),
)
