"""
minds/archetypes/dirigente_gremial.py — Perfil mental del DirigenteGremial.

Calibrado sobre patrones históricos de la cúpula sindical argentina (CGT/CTA):
- CRI base 0.88: muy alta resistencia al cambio normativo laboral
- Loss_framing_sensitivity alto: maximiza la percepción de amenaza ("pérdida de derechos")
- Coalition_loyalty 0.92: la más alta del sistema — opera como agente de la corporación
- Musashi: guerrero de alta precisión táctica; Machiavelli: sabe cuándo negociar y cuándo resistir

Council mapping: Musashi (disciplina, precisión táctica, win conditions claras)
+ Machiavelli (uso estratégico del poder, alianzas temporales cuando conviene)

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


DIRIGENTE_GREMIAL_MIND = MindProfile(
    archetype_id="dirigente_gremial",
    archetype_name="DirigenteGremial",
    cognitive=CognitiveDimension(
        selective_attention=0.82,   # Alta: filtra agresivamente — solo ve amenazas y oportunidades
        processing_load=0.60,       # Moderado: no es jurista pero conoce bien el código laboral
        working_memory=0.55,        # Trabaja con pocos marcos conceptuales pero muy consolidados
        anchoring_bias=0.85,        # Muy alto: "los derechos adquiridos son inderogables"
    ),
    affective=AffectiveDimension(
        risk_aversion=0.35,         # Bajo: dispuesto a acciones de alto costo (huelgas, litigio)
        optimism_bias=0.30,         # Bajo: pesimista sobre intenciones reales de la norma
        emotional_viscosity=0.88,   # Muy alta: una vez en posición de combate, muy difícil cambiar
        loss_framing_sensitivity=0.90,  # Muy alto: opera casi exclusivamente con framing de pérdida
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.85,    # Muy alto: "derecho laboral = conquista histórica irrenunciable"
        bayesian_plasticity=0.15,   # Muy baja: el update real requiere cambio generacional
        coalition_loyalty=0.92,     # Máxima: opera como brazo ejecutor de la señal de la central
        precedent_weight=0.78,      # Alto: cada convenio histórico es precedente a defender
    ),
    council_ref=CouncilReference(
        primary="musashi",          # El guerrero que elige sus batallas con precisión letal
        secondary="machiavelli",    # La alianza como instrumento, no como fin
        weight_primary=0.58,
    ),
    description=(
        "El dirigente gremial es el actor con mayor coalición_loyalty del sistema. "
        "Opera como relay de la señal sindical: su función actual (preservar la corporación) "
        "ha derivado de la función original (mejorar condiciones laborales). "
        "Musashi le da la disciplina para elegir cuándo litigar y cuándo negociar; "
        "Machiavelli le enseña que toda negociación es táctica, nunca estratégica. "
        "Su CRI 0.88 combinado con loss_framing 0.90 genera el spandrel más característico: "
        "el litigio sistemático como negociación informal — el spandrel más documentado "
        "de la legislación laboral argentina 1990-2024."
    ),
)
