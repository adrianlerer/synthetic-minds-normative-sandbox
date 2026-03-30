"""
analysis/evolutionary_report.py — Generador de informe evolutivo post-simulación.

Produce un resumen legible en consola con todos los resultados clave:
- CLI por ronda (tabla simple)
- FDI final y en rondas clave
- Spandrels encontrados (detalles)
- MSR clasificación final (mutualista/parasitaria/etc.)
- Hipótesis confirmadas/rechazadas

Interfaz:
    from analysis.evolutionary_report import generate_report
    generate_report(aggregated_results)

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sandbox.runner import AggregatedResults
    from engine.simulation import SimulationResults


def _bar(value: float, width: int = 20, char_full: str = "█", char_empty: str = "░") -> str:
    """Genera una barra de progreso ASCII."""
    filled = int(round(value * width))
    filled = max(0, min(width, filled))
    return char_full * filled + char_empty * (width - filled)


def _msr_classification(msr: float) -> str:
    """Clasifica el tipo de norma según el MSR."""
    if msr > 1.20:
        return "MUTUALISTA    (L3↑, L1↑)"
    elif 0.80 <= msr <= 1.20:
        return "NEUTRAL       (L3≈L1)"
    elif 0.50 <= msr < 0.80:
        return "PARASITARIA   (L1↑, L3↓)"
    elif msr >= 0:
        return "DELÉTEREA     (L1↓, L3↓)"
    else:
        return "ALTRUISTA     (L3↑, L1↓)"


def generate_report(results, compact: bool = False) -> None:
    """Genera e imprime el informe evolutivo completo.

    Acepta tanto AggregatedResults (múltiples seeds) como SimulationResults
    (resultado individual de una seed).

    Args:
        results: AggregatedResults o SimulationResults.
        compact: Si True, omite la tabla detallada de CLI por ronda.
    """
    # Detectar tipo de resultados
    from sandbox.runner import AggregatedResults
    from engine.simulation import SimulationResults

    is_aggregated = isinstance(results, AggregatedResults)

    print()
    print("=" * 65)
    print("  INFORME EVOLUTIVO SNMS — Análisis de Selección Multinivel")
    print("  Lerer (2026) | AGPL-3.0")
    print("=" * 65)

    if is_aggregated:
        print(f"  Experimento:  {results.experiment_id}")
        print(f"  Seeds:        {results.n_seeds} | Rondas: {results.rounds_run}")
        print(f"  Seeds usadas: {results.seeds_used}")
    else:
        print(f"  Experimento:  {results.experiment_id}")
        print(f"  Seed:         {results.seed} | Rondas: {results.rounds_run}")

    print()

    # ── CLI por ronda (tabla simplificada) ──
    if not compact:
        print("  CLI POR RONDA")
        print("  " + "─" * 55)
        if is_aggregated:
            cli_series = results.cli_by_round_mean
        else:
            cli_series = [rm.cli for rm in results.round_metrics]

        # Mostrar cada 5 rondas (o cada ronda si hay pocas)
        step = max(1, len(cli_series) // 20)
        for i, cli_val in enumerate(cli_series):
            if i % step == 0 or i == len(cli_series) - 1:
                ronda = i + 1
                bar = _bar(cli_val)
                print(f"  Ronda {ronda:3d} │ {bar} │ {cli_val:.3f}")
        print()

    # ── Métricas finales ──
    print("  MÉTRICAS FINALES")
    print("  " + "─" * 55)

    if is_aggregated:
        cli_m, cli_s = results.cli_mean, results.cli_std
        fdi_m, fdi_s = results.fdi_mean, results.fdi_std
        msr_m, msr_s = results.msr_mean, results.msr_std
        sp_m = results.n_spandrels_mean
    else:
        last = results.round_metrics[-1] if results.round_metrics else None
        cli_m = results.final_cli
        cli_s = 0.0
        fdi_m = results.final_fdi
        fdi_s = 0.0
        msr_m = results.final_msr
        msr_s = 0.0
        sp_m = float(len(results.spandrels))

    print(f"  CLI final:       {cli_m:.3f} (±{cli_s:.3f})  {_bar(cli_m, 15)}")
    print(f"  FDI final:       {fdi_m:.3f} (±{fdi_s:.3f})  {_bar(fdi_m, 15)}")
    print(f"  MSR final:       {msr_m:.3f} (±{msr_s:.3f})")
    print(f"  Spandrels:       {sp_m:.1f}")
    print()

    # ── Clasificación MSR ──
    classification = _msr_classification(msr_m)
    print(f"  CLASIFICACIÓN DE LA NORMA: {classification}")
    print()

    # ── Spandrels ──
    if is_aggregated:
        # Tomar spandrels del primer resultado para mostrar ejemplos
        all_spandrels = results.individual_results[0].spandrels if results.individual_results else []
    else:
        all_spandrels = results.spandrels

    if all_spandrels:
        print("  SPANDRELS DETECTADOS")
        print("  " + "─" * 55)
        for sp in all_spandrels:
            tipo = "PARASITARIO" if sp.is_parasitic else "BENEFICIOSO"
            print(f"  [{sp.spandrel_id}] {sp.description[:50]}")
            print(f"           Norma origen:  {sp.origin_norm_id}")
            print(f"           Emergió:       ronda {sp.emergence_round}")
            print(f"           FC:            {sp.fitness_contribution:+.3f}")
            print(f"           Tipo:          {tipo}")
            if sp.affected_archetypes:
                print(f"           Arquetipos:    {', '.join(sp.affected_archetypes[:3])}")
            print()
    else:
        print("  SPANDRELS: ninguno detectado en esta simulación.")
        print()

    # ── Hipótesis ──
    print("  HIPÓTESIS")
    print("  " + "─" * 55)

    if is_aggregated:
        hypotheses = results.hypotheses_consolidated
    else:
        hypotheses = results.hypotheses_tested

    all_confirmed = True
    for hid, h in hypotheses.items():
        if is_aggregated:
            confirmed = h.get("confirmed", False)
            val = h.get("value_mean")
            std = h.get("value_std", 0.0)
            n_conf = h.get("n_confirmed", 0)
            n_total = h.get("n_seeds", 1)
            status_str = f"{'CONFIRMADA' if confirmed else 'RECHAZADA'} ({n_conf}/{n_total} seeds)"
        else:
            confirmed = h.get("confirmed", False)
            val = h.get("value")
            std = 0.0
            status_str = "CONFIRMADA" if confirmed else "RECHAZADA"

        if not confirmed:
            all_confirmed = False

        icon = "✓" if confirmed else "✗"
        pred = h.get("prediction", "")[:45]
        label = h.get("label", hid)

        val_str = f"{val:.3f}" if val is not None else "N/A"
        print(f"  [{hid}] {icon} {label}")
        print(f"        Predicción: {pred}")
        print(f"        Valor:      {val_str}  →  {status_str}")
        print()

    # ── Conclusión ──
    print("  " + "─" * 55)
    if all_confirmed:
        print("  CONCLUSIÓN: Todas las hipótesis confirmadas.")
        print("  El marco teórico SNMS/EPT/EGT es consistente con los resultados.")
    else:
        confirmed_count = sum(
            1 for h in hypotheses.values()
            if h.get("confirmed", False)
        )
        total = len(hypotheses)
        print(f"  CONCLUSIÓN: {confirmed_count}/{total} hipótesis confirmadas.")
        print("  Ver paper para interpretación de hipótesis rechazadas.")
    print("=" * 65)
    print()


def generate_cli_table(results, n_rows: int = 20) -> str:
    """Genera una tabla de texto con CLI por ronda para insertar en paper.

    Args:
        results: AggregatedResults o SimulationResults.
        n_rows: Número máximo de filas a mostrar.

    Returns:
        String con la tabla en formato texto.
    """
    from sandbox.runner import AggregatedResults

    is_agg = isinstance(results, AggregatedResults)

    if is_agg:
        cli_series = results.cli_by_round_mean
        header = f"Tabla: CLI por ronda — media de {results.n_seeds} seeds\n"
    else:
        cli_series = [rm.cli for rm in results.round_metrics]
        header = f"Tabla: CLI por ronda — seed {results.seed}\n"

    lines = [header, "Ronda | CLI   | Bar"]
    step = max(1, len(cli_series) // n_rows)
    for i, val in enumerate(cli_series):
        if i % step == 0 or i == len(cli_series) - 1:
            ronda = i + 1
            bar = "█" * int(val * 15)
            lines.append(f"{ronda:5d} | {val:.3f} | {bar}")
    return "\n".join(lines)
