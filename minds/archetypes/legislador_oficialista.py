"""
minds/archetypes/legislador_oficialista.py — Perfil mental del LegisladorOficialista.

Calibrado sobre patrones históricos del bloque oficialista parlamentario argentino:
- CRI base 0.61: resistencia moderada-alta, pero con margen de negociación
- Optimism_bias alto: sobreestima los efectos positivos de la reforma
- Coalition_loyalty 0.80: muy leal a la señal del bloque (line voting)
- Anchoring_bias alto: el primer encuadre de su bloque es difícil de mover

Council mapping: Machiavelli (estrategia del poder, realpolitik parlamentario)
+ Sun Tzu (posicionamiento estratégico, evitar el enfrentamiento innecesario)

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


LEGISLADOR_OFICIALISTA_MIND = MindProfile(
    archetype_id="legislador_oficialista",
    archetype_name="LegisladorOficialista",
    cognitive=CognitiveDimension(
        selective_attention=0.72,   # Filtra selectivamente: ve lo que confirma la agenda oficial
        processing_load=0.55,       # Capacidad técnica media: depende de asesores
        working_memory=0.50,        # Puede sostener algunos argumentos simultáneos
        anchoring_bias=0.75,        # El framing inicial del bloque es muy difícil de cambiar
    ),
    affective=AffectiveDimension(
        risk_aversion=0.40,         # Apetito por el riesgo moderado: en el poder, puede avanzar
        optimism_bias=0.80,         # Sobreestima fuertemente los efectos positivos de la norma
        emotional_viscosity=0.65,   # Moderadamente lento en cambiar posición pública
        loss_framing_sensitivity=0.50,  # Sensibilidad media: framing de "ganancia" domina
    ),
    doctrinal=DoctrinalDimension(
        ideological_anchor=0.68,    # Anclaje ideológico moderado-alto (agenda de coalición)
        bayesian_plasticity=0.38,   # Baja plasticidad real: update solo si hay presión electoral
        coalition_loyalty=0.80,     # Alta lealtad: vota con el bloque salvo casos extremos
        precedent_weight=0.40,      # Baja: la norma anterior interesa poco si hay nueva agenda
    ),
    council_ref=CouncilReference(
        primary="machiavelli",      # El poder como fin y como medio simultáneamente
        secondary="sun_tzu",        # No pelear batallas innecesarias; posicionarse para ganar
        weight_primary=0.65,
    ),
    description=(
        "El legislador oficialista opera como nodo de transmisión de la señal coalicional "
        "más que como deliberador autónomo. Su sesgo optimista sobre la reforma que impulsa "
        "es funcionalmente adaptativo: necesita creer en ella para defenderla públicamente. "
        "Machiavellianamente, entiende que la norma es un instrumento de acumulación de "
        "poder; Sun Tzustamente, sabe cuándo no enfrentar al JuezCSJN frontalmente. "
        "Su CRI 0.61 deja margen de negociación que aprovecha cuando el bloque lo autoriza."
    ),
)
