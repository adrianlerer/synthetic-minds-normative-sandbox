"""
engine/spandrel_detector.py — Detector automático de spandrels normativos.

Un spandrel normativo es un efecto lateral de una norma que, tras N rondas,
adquiere función propia y se vuelve funcionalmente autónomo — a veces más
relevante que la norma original.

Algoritmo de detección:
1. En cada ronda, el detector observa patrones de comportamiento que no
   están en el diseño de ninguna norma activa
2. Si un patrón persiste > PERSISTENCE_THRESHOLD rondas, se clasifica
   como candidato a spandrel
3. Si el candidato tiene fitness_contribution significativo (|FC| > 0.15),
   se registra como spandrel confirmado en la norma origen más probable

Ejemplos de spandrels detectables:
- Emergencia de litigio estratégico como norma informal de negociación
  (spandrel de una ley laboral protectoria)
- Surgimiento de doctrina judicial como efecto de una reforma constitucional
  que intentaba hacer otra cosa
- Formación de coaliciones improbables como respuesta a una norma que
  afectaba a sus adversarios históricos

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from agents.base_agent import BaseSyntheticAgent
    from norms.norm import Norm, NormativeSpandrel

# Umbrales de detección
PERSISTENCE_THRESHOLD = 5       # Rondas que debe persistir un patrón
FITNESS_SIGNIFICANCE = 0.15     # |FC| mínimo para confirmar spandrel
COALITION_FORMATION_DELTA = 0.2 # Cambio en lealtad coalicional que dispara detección


@dataclass
class SpandrelCandidate:
    """Candidato a spandrel: patrón persistente no planificado.

    Atributos:
        pattern_id: Identificador del patrón detectado
        first_seen_round: Primera vez que se detectó
        last_seen_round: Última ronda en que fue observado
        persistence: Cantidad de rondas consecutivas observado
        description: Descripción del patrón
        fitness_contribution: Estimación del FC [-1, 1]
        candidate_origin_norm: Norma más probable de haber generado el patrón
    """
    pattern_id: str
    first_seen_round: int
    last_seen_round: int
    persistence: int = 1
    description: str = ""
    fitness_contribution: float = 0.0
    candidate_origin_norm: str = ""
    affected_archetypes: list[str] = field(default_factory=list)

    @property
    def is_confirmed(self) -> bool:
        """True si el candidato cumple ambos umbrales de confirmación."""
        return (
            self.persistence >= PERSISTENCE_THRESHOLD
            and abs(self.fitness_contribution) >= FITNESS_SIGNIFICANCE
        )


class SpandrelDetector:
    """Detecta emergencia de spandrels normativos en la simulación.

    Opera en paralelo con el motor principal: observa patrones de
    comportamiento que ninguna norma diseñó explícitamente.
    """

    def __init__(self, rng: random.Random):
        """Inicializa el detector.

        Args:
            rng: Generador aleatorio con seed controlada.
        """
        self.rng = rng
        self.candidates: dict[str, SpandrelCandidate] = {}
        self.confirmed_spandrels: list["NormativeSpandrel"] = []
        self._spandrel_counter = 0

    def scan_round(
        self,
        round_number: int,
        agents: list["BaseSyntheticAgent"],
        active_norms: list["Norm"],
    ) -> list["NormativeSpandrel"]:
        """Escanea la ronda en busca de nuevos spandrels.

        Detecta tres tipos de patrones:
        1. Coaliciones improbables (arquetipos típicamente opuestos alineándose)
        2. Litigio estratégico sistemático (no reactivo)
        3. Normas informales emergentes (comportamiento sin base legal explícita)

        Args:
            round_number: Número de ronda actual.
            agents: Lista de todos los agentes.
            active_norms: Normas activas en esta ronda.

        Returns:
            Lista de spandrels confirmados en esta ronda (puede estar vacía).
        """
        new_spandrels = []

        # Patrón 1: Detección de coaliciones improbables
        new_spandrels.extend(
            self._detect_improbable_coalitions(round_number, agents, active_norms)
        )

        # Patrón 2: Detección de litigio estratégico sistemático
        new_spandrels.extend(
            self._detect_strategic_litigation(round_number, agents, active_norms)
        )

        # Actualizar candidatos y promover confirmados
        new_spandrels.extend(self._promote_confirmed_candidates(round_number))

        return new_spandrels

    def _detect_improbable_coalitions(
        self,
        round_number: int,
        agents: list["BaseSyntheticAgent"],
        active_norms: list["Norm"],
    ) -> list:
        """Detecta formación de coaliciones entre arquetipos típicamente opuestos."""
        # Heurística: si dos agentes con ideological_anchor muy distinto
        # tienen correlation alta en sus últimas acciones, es señal
        # de coalición improbable (posible spandrel de una norma adversaria)

        high_anchor = [a for a in agents if hasattr(a, 'mind') and
                       a.mind.doctrinal.ideological_anchor > 0.70]
        low_anchor = [a for a in agents if hasattr(a, 'mind') and
                      a.mind.doctrinal.ideological_anchor < 0.35]

        if len(high_anchor) > 3 and len(low_anchor) > 3:
            # Verificar si sus creencias de validez normativa convergen
            ha_beliefs = [a.norm_validity_belief for a in high_anchor]
            la_beliefs = [a.norm_validity_belief for a in low_anchor]
            ha_mean = sum(ha_beliefs) / len(ha_beliefs)
            la_mean = sum(la_beliefs) / len(la_beliefs)

            if abs(ha_mean - la_mean) < 0.10:  # convergencia improbable
                pattern_id = "improbable_coalition_convergence"
                self._update_candidate(
                    pattern_id=pattern_id,
                    round_number=round_number,
                    description="Convergencia de creencias entre arquetipos de alto y bajo anclaje ideológico",
                    fitness_contribution=0.18,  # generalmente beneficioso para L3
                    candidate_origin_norm=active_norms[0].norm_id if active_norms else "unknown",
                    affected_archetypes=[a.archetype_id for a in high_anchor[:2] + low_anchor[:2]
                                         if hasattr(a, 'archetype_id')],
                )
        return []

    def _detect_strategic_litigation(
        self,
        round_number: int,
        agents: list["BaseSyntheticAgent"],
        active_norms: list["Norm"],
    ) -> list:
        """Detecta litigio estratégico sistemático como norma informal emergente."""
        from agents.base_agent import ActionType

        # Si más del 40% de los agentes con acciones legales disponibles
        # eligen LITIGATE de forma consistente, podría ser spandrel
        litigating_agents = [
            a for a in agents
            if hasattr(a, 'last_action') and a.last_action == ActionType.LITIGATE
        ]

        if len(agents) > 0 and len(litigating_agents) / len(agents) > 0.40:
            pattern_id = "systematic_strategic_litigation"
            self._update_candidate(
                pattern_id=pattern_id,
                round_number=round_number,
                description="Litigio sistemático como mecanismo informal de negociación normativa",
                fitness_contribution=-0.20,  # parasitario: costoso para L3
                candidate_origin_norm=active_norms[0].norm_id if active_norms else "unknown",
                affected_archetypes=["juez_csjn", "legislador_oficialista"],
            )
        return []

    def _update_candidate(
        self,
        pattern_id: str,
        round_number: int,
        description: str,
        fitness_contribution: float,
        candidate_origin_norm: str,
        affected_archetypes: list[str],
    ) -> None:
        """Actualiza o crea un candidato a spandrel."""
        if pattern_id in self.candidates:
            c = self.candidates[pattern_id]
            c.last_seen_round = round_number
            c.persistence += 1
            # Media móvil del FC
            c.fitness_contribution = 0.7 * c.fitness_contribution + 0.3 * fitness_contribution
        else:
            self.candidates[pattern_id] = SpandrelCandidate(
                pattern_id=pattern_id,
                first_seen_round=round_number,
                last_seen_round=round_number,
                description=description,
                fitness_contribution=fitness_contribution,
                candidate_origin_norm=candidate_origin_norm,
                affected_archetypes=affected_archetypes,
            )

    def _promote_confirmed_candidates(self, round_number: int) -> list["NormativeSpandrel"]:
        """Promueve candidatos que superan los umbrales a spandrels confirmados."""
        from norms.norm import NormativeSpandrel

        new_confirmed = []
        to_remove = []

        for pid, candidate in self.candidates.items():
            if candidate.is_confirmed:
                self._spandrel_counter += 1
                spandrel = NormativeSpandrel(
                    spandrel_id=f"sp_{self._spandrel_counter:04d}",
                    origin_norm_id=candidate.candidate_origin_norm,
                    emergence_round=candidate.first_seen_round,
                    description=candidate.description,
                    acquired_function=f"función_autónoma_{pid}",
                    fitness_contribution=candidate.fitness_contribution,
                    affected_archetypes=candidate.affected_archetypes,
                    is_parasitic=candidate.fitness_contribution < 0,
                )
                new_confirmed.append(spandrel)
                self.confirmed_spandrels.append(spandrel)
                to_remove.append(pid)

        for pid in to_remove:
            del self.candidates[pid]

        return new_confirmed
