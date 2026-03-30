"""
minds/archetypes/empresario_regulado.py — Perfil mental del EmpresarioRegulado.

Calibrado sobre el empresario PYME/MiPyME argentino típico (CAME/UIA):
- CRI base 0.45: baja resistencia — el empresario CUMPLE si el costo de cumplir < costo de no cumplir
- Risk_aversion bajo: dispuesto a experimentar con nuevas formas organizacionales
- Processing_load alto: necesita entender las normas para adaptarse rápido (survival imperative)
- Ada Lovelace: primera en ver el potencial oculto de los sistemas formales

Council mapping: Torvalds (pragmatismo técnico, soluciones que funcionan sobre ideología)
+ Ada Lovelace (ver el potencial de los sistemas; primeros en adoptar cuando vale la pena)

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


EMPRESARIO_REGULADO_MIND = MindProfile(
    archetype_id="empresario_regulado",
    archetype_name="EmpresarioRegulado",
    cognitive=CognitiveDimension(
        selective_attention=0.35,   # Bajo: atiende a señales de mercado más que ideológicas
        processing_load=0.78,       # Alto: necesita procesar normas para calcular compliance cost
        working_memory=0.70,        # Puede sostener múltiples variables regulatorias simultáneas
        anchoring_bias=0.30,        # Bajo: cambia de posición si cambia el costo/beneficio
    ),
    affective=AffectiveDimension(
        risk_aversion=0.28,         # Bajo: el empresario argentino está habituado a entornos inciertos
        optimism_bias=0.55,         # Moderado: optimista sobre oportunidades de la flexibilización
        emotional_viscosity=0.35,   # Bajo: cambia de posición rápido cuando cambia el incentivo
        loss_framing_sensitivity=0.60,  # Moderado: sensible al costo regulatorio como pérdida
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.30,    # Muy bajo: pragmático, no ideológico
        bayesian_plasticity=0.75,   # Alto: actualiza bien ante cambios de entorno
        coalition_loyalty=0.38,     # Bajo-moderado: se suma a coaliciones si le conviene
        precedent_weight=0.35,      # Bajo: mira hacia adelante, no hacia el precedente
    ),
    council_ref=CouncilReference(
        primary="torvalds",         # Si funciona, úsalo; si no, cámbialo
        secondary="ada",            # Primero en ver el potencial real del sistema
        weight_primary=0.62,
    ),
    description=(
        "El empresario regulado es el agente con mayor plasticidad cognitiva del sistema: "
        "su bajo CRI (0.45) y alta plasticidad bayesiana lo hacen sensible a los incentivos "
        "reales de la norma. Torvaldsianamente, no le importa la ideología: si la reforma "
        "laboral reduce costos de contratación, la apoya; si genera incertidumbre jurídica, "
        "resiste. Ada Lovelace representa su capacidad de ver el potencial oculto de los "
        "marcos regulatorios. Es el agente más likely de generar compliance genuino "
        "cuando la norma es técnicamente clara y económicamente racional."
    ),
)
