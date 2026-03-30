"""
engine/hbu.py — Heteronomous Bayesian Update (HBU) en batch.

El HBU es el mecanismo central por el cual los agentes actualizan sus
creencias sobre la validez de una norma observando el comportamiento
agregado del sistema.

"Heteronomous" porque el update proviene de señales externas (compliance
rate, intensidad de sanciones) en lugar de razonamiento propio del agente.
Deriva directamente del mecanismo HBU del repo 816-agentes-EPT.

Diferencia con el HBU individual (en base_agent.py):
- El HBU individual actualiza un agente a la vez con parámetros dados
- Este módulo orquesta el batch update: observa el entorno completo,
  calcula los parámetros de señal y llama a cada agente

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseSyntheticAgent
    from engine.environment import LegalEnvironment


def hbu_batch_update(
    agents: list["BaseSyntheticAgent"],
    environment: "LegalEnvironment",
    norm_complexity: float = 0.72,
) -> dict[str, float]:
    """Ejecuta el Heteronomous Bayesian Update para todos los agentes.

    Observa el estado del entorno y genera las señales de compliance y
    sanción que luego se pasan a cada agente para su update individual.

    El efecto es heterónomo: el agente no razona autónomamente sobre la
    norma, sino que actualiza sus creencias observando qué hacen los demás
    y qué respuesta institucional se genera.

    Args:
        agents: Lista de todos los agentes activos.
        environment: Estado del entorno en la ronda actual.
        norm_complexity: Complejidad de la norma activa [0,1].
            Las normas complejas reducen la señal de sanción percibida.

    Returns:
        Diccionario {agent_id: nueva_creencia} con las creencias actualizadas.
    """
    # Calcular la señal de compliance observada
    # Agentes que cumplen son los que están en ActionType.COMPLY o NEGOTIATE
    from agents.base_agent import ActionType

    complying_agents = [
        a for a in agents
        if a.last_action in (ActionType.COMPLY, ActionType.NEGOTIATE)
    ]
    observed_compliance = len(complying_agents) / len(agents) if agents else 0.5

    # Sincronizar con lo que el entorno registró
    # (el entorno tiene una estimación propia; tomamos el promedio)
    blended_compliance = (observed_compliance + environment.norm_compliance_rate) / 2.0

    # Señal de sanción: alta intensidad de sanciones → la norma tiene dientes → más válida
    # Pero la complejidad de la norma atenúa la legibilidad de la señal
    sanction_readability = 1.0 - norm_complexity * 0.30
    observed_sanction = environment.sanction_intensity * sanction_readability

    # Ejecutar el update individual para cada agente
    new_beliefs: dict[str, float] = {}
    for agent in agents:
        agent.hbu_update(
            observed_compliance=blended_compliance,
            observed_sanction=observed_sanction,
        )
        new_beliefs[agent.agent_id] = agent.norm_validity_belief

    # Actualizar la tasa de compliance del entorno con el valor observado
    environment.norm_compliance_rate = (
        0.7 * environment.norm_compliance_rate
        + 0.3 * observed_compliance
    )

    return new_beliefs


def compute_belief_distribution(
    agents: list["BaseSyntheticAgent"],
) -> dict:
    """Calcula la distribución de creencias sobre validez normativa.

    Útil para análisis post-simulación y para detectar polarización.

    Args:
        agents: Lista de agentes.

    Returns:
        Diccionario con estadísticas de la distribución.
    """
    if not agents:
        return {"mean": 0.5, "std": 0.0, "min": 0.5, "max": 0.5, "n_valid": 0}

    beliefs = [a.norm_validity_belief for a in agents]
    n = len(beliefs)
    mean_b = sum(beliefs) / n
    variance = sum((b - mean_b) ** 2 for b in beliefs) / n
    std_b = variance ** 0.5

    return {
        "mean": round(mean_b, 4),
        "std": round(std_b, 4),
        "min": round(min(beliefs), 4),
        "max": round(max(beliefs), 4),
        "n_valid": sum(1 for b in beliefs if b >= 0.5),
        "n_agents": n,
        "polarization_index": round(min(1.0, variance * 4), 4),
    }
