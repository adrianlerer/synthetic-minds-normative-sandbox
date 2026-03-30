# Synthetic Minds Normative Sandbox (SNMS)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)]()

> **"La función actual no requiere haber sido la función original."**
> — S.J. Gould & E.S. Vrba (1982), reformulando a Nietzsche

## Qué es

SNMS integra tres líneas de desarrollo previas para crear un sandbox normativo de segunda generación:

| Capa | Origen | Rol en SNMS |
|------|--------|-------------|
| **Población sintética** | [816-agentes-EPT](https://github.com/adrianlerer/816-agentes-institucionales-argentinos-EPT) | Agentes con CRI, HBU, capital institucional |
| **Mentes arquetípicas** | [TribeV2](https://github.com/adrianlerer/tribev2) (Meta) + [Council](https://github.com/adrianlerer/council-of-high-intelligence) | Perfil cognitivo-afectivo de cada arquetipo |
| **Motor sandbox** | [OpenSandbox](https://github.com/adrianlerer/OpenSandbox) | Ejecución aislada, reproducible y escalable |

**Contribución central:** los agentes ya no son sólo parámetros numéricos (CRI, capital, HBU). Ahora cada arquetipo institucional porta una *mente tipo* — un perfil de respuesta ante estímulos normativos que incluye dimensiones cognitivas (atención selectiva, carga de procesamiento), afectivas (aversión al riesgo, sesgo optimista) y doctrinales (anclaje ideológico, plasticidad bayesiana).

---

## Marco teórico

### 1. Exaptación y función actual (Gould & Vrba 1982)

Las normas jurídicas rara vez ejercen la función para la que fueron diseñadas. SNMS opera bajo la distinción:

- **Función original** (`origin_function`): propósito declarado en la exposición de motivos
- **Función actual** (`current_function`): efecto observado en la simulación tras N rondas

El motor registra la distancia entre ambas (`functional_drift_index`) como métrica evolutiva clave.

### 2. Selección multinivel (Wilson & Sober 1994; Okasha 2006)

Los experimentos corren simultáneamente en tres niveles de selección:

```
Nivel 3: Poblacional  — Fitness de la norma en el ecosistema institucional
Nivel 2: Grupal       — Fitness de coaliciones (CGT, CSJN, CAME, etc.)
Nivel 1: Individual   — Fitness del agente (CRI, capital, creencias)
```

Una norma puede ser estable en L3 pero deletérea en L1 (trampa institucional), o viceversa (free-rider doctrinal).

### 3. Enjutas de San Marcos (spandrels) normativos

SNMS detecta automáticamente efectos no planificados de una norma que, con el tiempo, adquieren función propia:

```python
class NormativeSpandrel:
    """Efecto secundario de una norma que se vuelve funcionalmente autónomo."""
    origin_norm: str          # norma que lo generó
    emergence_round: int      # ronda en que apareció
    acquired_function: str    # función que tomó
    fitness_contribution: float
```

### 4. Mentes tipo (Synthetic Minds)

Cada arquetipo lleva un `MindProfile` calibrado sobre dos fuentes:

- **TribeV2 (Meta)**: predicción de respuestas corticales ante estímulos multimodales → proxy de carga cognitiva y atención selectiva ante el texto normativo
- **Council of High Intelligence**: plantilla deliberativa de figura histórica → sesgos epistémicos, estilo inferencial, resistencia al cambio

---

## Arquetipos incluidos (v0.1)

| Arquetipo | Base empírica | Mente tipo | CRI base |
|-----------|--------------|------------|----------|
| `JuezCSJN` | 5 ministros históricos | Aristotle + Aurelius | 0.82 |
| `LegisladorOficialista` | Mayoría parlamentaria típica | Machiavelli + Sun Tzu | 0.61 |
| `LegisladorOpositor` | Minoría parlamentaria | Socrates + Feynman | 0.55 |
| `DirigenteGremial` | CGT/CTA histórica | Musashi + Machiavelli | 0.88 |
| `EmpresarioRegulado` | CAME/UIA típica | Torvalds + Ada | 0.45 |
| `CiudadanoInformado` | Encuestas CEDEC/Latinobarómetro | Watts + Lao Tzu | 0.30 |
| `ReguladorTécnico` | Entes reguladores argentinos | Feynman + Aristotle | 0.70 |
| `JuristaDoctrinario` | Academia jurídica argentina | Aristotle + Socrates | 0.91 |

---

## Arquitectura

```
snms/
├── minds/                    # Perfiles cognitivos arquetípicos
│   ├── base_mind.py          # MindProfile: cognición + afecto + doctrina
│   ├── archetypes/           # Un archivo por arquetipo
│   │   ├── juez_csjn.py
│   │   ├── legislador_oficialista.py
│   │   └── ...
│   └── tribe_bridge.py       # Interfaz con TribeV2 (encoding cortical → CL proxy)
│
├── agents/                   # Agentes con mente integrada (hereda de 816-agentes)
│   ├── base_agent.py         # BaseSyntheticAgent: CRI + HBU + MindProfile
│   ├── judge.py
│   ├── legislator.py
│   ├── union_leader.py
│   ├── firm.py
│   ├── citizen.py
│   └── regulator.py
│
├── norms/                    # Representación formal de normas
│   ├── norm.py               # Norm: texto, origin_function, current_function
│   ├── norm_library/         # Normas reales y sintéticas para experimentos
│   │   ├── reforma_laboral_arg.yaml
│   │   ├── ley_bases_2024.yaml
│   │   └── synthetic_template.yaml
│   └── functional_drift.py   # FunctionalDriftTracker: origin vs current
│
├── engine/                   # Motor de simulación multinivel
│   ├── simulation.py         # Loop principal (rounds × agents × levels)
│   ├── multilevel.py         # SelectionEngine: L1/L2/L3 simultáneos
│   ├── spandrel_detector.py  # Detección automática de efectos spandrel
│   ├── hbu.py                # Heteronomous Bayesian Updating (from 816-agentes)
│   ├── environment.py        # LegalEnvironment: estado del ecosistema
│   └── metrics.py            # CLI, FDI, SEM (Spandrel Emergence Metric)
│
├── council_bridge/           # Interfaz con council-of-high-intelligence
│   ├── deliberation.py       # ArchetypeDeliberation: consulta al council
│   └── mind_mapper.py        # Mapeo council-member → arquetipo
│
├── sandbox/                  # Integración con OpenSandbox
│   ├── runner.py             # SandboxRunner: ejecución aislada
│   └── experiment.py         # ExperimentConfig: parámetros del experimento
│
├── experiments/              # Configuraciones de experimentos predefinidos
│   ├── base_experiment.yaml
│   ├── reforma_laboral_2025.yaml
│   └── fiscal_lock_in.yaml
│
├── analysis/                 # Análisis post-simulación
│   ├── evolutionary_report.py
│   ├── exaptation_map.py     # Visualización de deriva funcional
│   └── multilevel_heatmap.py
│
├── tests/
├── docs/
│   ├── THEORY.md
│   ├── METHODOLOGY.md
│   └── EXPERIMENTS.md
├── requirements.txt
├── run.py
└── README.md
```

---

## Métricas clave

| Métrica | Sigla | Descripción |
|---------|-------|-------------|
| Constitutional Lock-in Index | CLI | Rigidez estructural del sistema (heredado de 816-agentes) |
| Functional Drift Index | FDI | Distancia entre función original y actual de la norma |
| Spandrel Emergence Metric | SEM | Velocidad y frecuencia de aparición de efectos no planificados |
| Multilevel Selection Ratio | MSR | Proporción fitness L3/L1 (indica si la norma es parasitaria o mutualista) |
| Mind Coherence Score | MCS | Consistencia entre perfil cognitivo del arquetipo y su comportamiento observado |

---

## Instalación

```bash
git clone https://github.com/adrianlerer/synthetic-minds-normative-sandbox
cd synthetic-minds-normative-sandbox
pip install -r requirements.txt
```

Para usar la integración con TribeV2 (opcional, requiere GPU):
```bash
pip install -e ".[tribev2]"
huggingface-cli login  # requiere token con acceso a facebook/tribev2
```

---

## Uso rápido

```python
from snms.sandbox import SandboxRunner
from snms.experiments import load_experiment

# Cargar experimento predefinido
exp = load_experiment("experiments/reforma_laboral_2025.yaml")

# Ejecutar en sandbox
runner = SandboxRunner(experiment=exp)
results = runner.run(rounds=100, seeds=5)

# Analizar
print(results.summary())
print(f"FDI final: {results.functional_drift_index:.3f}")
print(f"Spandrels emergidos: {len(results.spandrels)}")
for sp in results.spandrels:
    print(f"  → {sp.origin_norm} → {sp.acquired_function} (ronda {sp.emergence_round})")
```

---

## Relación con repos anteriores

```
816-agentes-EPT          →  agents/ + engine/hbu.py + engine/metrics.py (CLI)
council-of-high-intelligence → minds/archetypes/ + council_bridge/
OpenSandbox              →  sandbox/runner.py
TribeV2 (Meta, forked)   →  minds/tribe_bridge.py
autoresearch             →  análisis y generación automática de hipótesis
lerer-research-program   →  marco teórico (papers fundacionales)
```

---

## Paper asociado

> Lerer, I. A. (2026). *Synthetic Minds in Normative Sandboxes: Exaptation,
> Spandrels, and Multilevel Selection in Agent-Based Legal Simulation.*
> [en preparación]

---

## Licencia

AGPL-3.0 — Ver [LICENSE](LICENSE)

Los pesos de TribeV2 están bajo [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Meta AI Research).
