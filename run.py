"""
run.py — Punto de entrada principal para SNMS.

Uso:
    python run.py
    python run.py --experiment experiments/reforma_laboral_2025.yaml
    python run.py --rounds 50 --seeds 3

SNMS — Synthetic Minds Normative Sandbox
Lerer (2026) | AGPL-3.0
"""

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="SNMS — Synthetic Minds Normative Sandbox"
    )
    parser.add_argument(
        "--experiment",
        default="experiments/reforma_laboral_2025.yaml",
        help="Ruta al archivo YAML de configuración del experimento",
    )
    parser.add_argument("--rounds", type=int, default=None, help="Override de rondas")
    parser.add_argument("--seeds", type=int, default=None, help="Override de cantidad de seeds")
    parser.add_argument("--output", default="results/", help="Directorio de salida")
    parser.add_argument("--verbose", action="store_true", help="Output detallado")
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("SNMS — Synthetic Minds Normative Sandbox")
    print("Lerer (2026)")
    print("=" * 60)
    print(f"Experimento: {args.experiment}")

    # Verificar que el archivo de experimento existe
    exp_path = Path(args.experiment)
    if not exp_path.exists():
        print(f"ERROR: No se encontró {args.experiment}", file=sys.stderr)
        print("Experimentos disponibles:")
        for yaml_file in Path("experiments").glob("*.yaml"):
            print(f"  {yaml_file}")
        sys.exit(1)

    # TODO: Implementar SandboxRunner cuando estén listos todos los módulos
    # Por ahora: validar estructura y mostrar configuración
    import yaml
    with open(exp_path) as f:
        config = yaml.safe_load(f)

    print(f"\nNorma: {config['norm']['name']}")
    print(f"Rondas: {args.rounds or config['simulation']['rounds']}")
    print(f"Seeds: {args.seeds or len(config['simulation']['seeds'])}")

    total_agents = sum(v['count'] for v in config['agents'].values())
    print(f"Agentes totales: {total_agents}")

    print("\nHipótesis a testear:")
    for hid, h in config['hypotheses'].items():
        print(f"  [{hid}] {h['label']}: {h['prediction']}")

    print("\n[SNMS] Módulos requeridos para ejecutar la simulación:")
    modules = [
        "minds/base_mind.py                 ✓ implementado",
        "minds/archetypes/juez_csjn.py      ✓ implementado",
        "agents/base_agent.py               ✓ implementado",
        "norms/norm.py                      ✓ implementado",
        "engine/multilevel.py               ✓ implementado",
        "engine/spandrel_detector.py        ✓ implementado",
        "engine/simulation.py               ⏳ pendiente",
        "engine/environment.py              ⏳ pendiente",
        "engine/hbu.py                      ⏳ pendiente (migrar de 816-agentes)",
        "sandbox/runner.py                  ⏳ pendiente",
        "council_bridge/deliberation.py     ⏳ pendiente",
        "minds/tribe_bridge.py              ⏳ pendiente (requiere GPU)",
    ]
    for m in modules:
        print(f"  {m}")

    print("\n[SNMS] v0.1 — esqueleto inicial creado. Ver docs/THEORY.md para el marco teórico.")


if __name__ == "__main__":
    main()
