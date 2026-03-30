# Marco Teórico — SNMS

## 1. El problema que resuelve SNMS

Los simuladores de normas previos (incluyendo el repo 816-agentes) tratan
a los agentes como autómatas con parámetros numéricos. Un juez de la CSJN
y un ciudadano desinformado tienen exactamente el mismo tipo de mecánica
interna — sólo difieren en los valores de CRI, capital y prior bayesiano.

SNMS parte de una pregunta diferente: **¿qué pasa si los agentes no sólo
tienen distintos parámetros, sino distintos modos de procesar la información
normativa?** La hipótesis es que los efectos emergentes (bloqueo, litigio
estratégico, deriva funcional) son cualitativamente diferentes cuando los
agentes tienen perfiles cognitivo-afectivos-doctrinales distintos.

---

## 2. Exaptación y función actual (Gould & Vrba 1982)

Stephen Jay Gould y Elisabeth Vrba introdujeron el término **exaptación**
para referirse a rasgos que fueron seleccionados por una función pero que
ejercen actualmente una función diferente. Distinguen:

- **Aptación**: rasgo seleccionado para su función actual (diseñado para lo que hace)
- **Exaptación**: rasgo seleccionado para otra función pero cooptado para la actual
- **Efecto espandrel**: rasgo que es subproducto arquitectónico, sin selección directa

La conexión con Nietzsche es explícita en Gould: *"La utilidad de algo no es
su origen"* (Genealogía de la Moral). Una norma jurídica puede haber sido
diseñada para reducir conflicto laboral y estar sirviendo actualmente como
herramienta de extracción de rentas. SNMS mide esa distancia mediante el
**Functional Drift Index (FDI)**.

### 2.1 FDI: Functional Drift Index

```
FDI = |fitness_actual_esperado - fitness_origen_declarado| / 2
      + 0.30 × (nivel_selección_cambia ? 1 : 0)
```

Un FDI > 0.40 indica que la norma es funcionalmente una exaptación:
sigue en el sistema (no fue eliminada) pero hace algo distinto de lo
que pretendía.

---

## 3. Selección multinivel (Wilson & Sober 1994; Okasha 2006)

El debate selección-individual vs. selección-de-grupo se resuelve en
biología evolutiva admitiendo que **ambas operan simultáneamente** en
niveles distintos. Wilson y Sober formalizaron la **selección multinivel**:

```
ΔZ̄_total = (Selección entre grupos) + (Selección dentro de grupos)
```

En SNMS, los tres niveles son:

| Nivel | Unidad | Fitness |
|-------|--------|---------|
| L1 | Agente individual | Capital institucional del agente |
| L2 | Coalición/grupo | Capital promedio de la coalición |
| L3 | Ecosistema | Estabilidad institucional (CLI proxy) |

El **Multilevel Selection Ratio (MSR)** = L3_fitness / L1_fitness indica:
- MSR > 1.2: norma mutualista (bien común genuino)
- MSR < 0.8: norma parasitaria (algunos actores se benefician a expensas del sistema)

---

## 4. Enjutas de San Marcos (spandrels)

El paper fundacional de Gould & Lewontin (1979), "The Spandrels of San Marco
and the Panglossian Paradigm", argumenta que muchos rasgos biológicos no son
adaptaciones sino subproductos arquitectónicos — como las enjutas triangulares
que resultan de colocar una cúpula sobre arcos circulares.

En derecho, los **spandrels normativos** son efectos secundarios de una norma
que adquieren función propia. Ejemplos:

1. **Informalidad laboral** como spandrel de la sobreprotección laboral formal
2. **Doctrina judicial** como spandrel de ambigüedad textual intencional
3. **Coaliciones improbables** como spandrel de normas amenazantes

SNMS detecta estos spandrels mediante el `SpandrelDetector`, que observa
patrones persistentes (> 5 rondas) con contribución al fitness significativa.

---

## 5. Mentes tipo: la capa cognitiva

### 5.1 TribeV2 como proxy de carga cognitiva

TribeV2 (Meta, 2025) es un modelo fundacional que predice respuestas cerebrales
(fMRI) ante estímulos multimodales. En SNMS, usamos TribeV2 de forma indirecta:
el **encoding cortical** del texto de una norma (su representación vectorial
en el espacio de respuestas cerebrales) sirve como proxy de su **complejidad
cognitiva percibida** por cada arquetipo.

La idea: una norma con alta activación en áreas de carga cognitiva elevada
es más difícil de procesar para arquétipos con bajo `processing_load`.
El `tribe_bridge.py` mapea el encoding → ajuste del `norm_processing_score`.

### 5.2 Council of High Intelligence como plantilla deliberativa

Para decisiones bajo alta ambigüedad normativa, el agente puede "deliberar"
usando la estructura del Council. El `ArchetypeDeliberation` en `council_bridge/`
invoca la perspectiva del miembro primario del arquetipo:

- `JuezCSJN` → delibera con Aristotle (categoriza la norma) + Aurelius (evalúa
  si comprometer principios es aceptable)
- `DirigenteGremial` → delibera con Musashi (¿es el momento del golpe?) +
  Machiavelli (¿qué quiere realmente el otro lado?)

Este mecanismo sólo se activa para decisiones de alta stakes (litigio o defección),
no para compliance rutinario.

---

## 6. Relación con EPT y EGT multinivel

### EPT (Extended Phenotype Theory aplicada al derecho)

Las normas jurídicas son **fenotipos extendidos** de las disposiciones normativas
previas a su codificación. SNMS extiende esta idea: las **mentes tipo** de los
agentes son el "genotipo" del sistema — la norma es el fenotipo extendido que
cada arquetipo construye o resiste.

### EGT Multinivel

Los experimentos SNMS son juegos evolutivos jugados simultáneamente en tres
niveles. El equilibrio evolutivo estable (ESS) no es único: puede haber ESS
en L1 que no son ESS en L3 (trampa institucional) o vice-versa.

La novedad respecto a 816-agentes: el ESS cambia cualitativamente cuando
los agentes tienen mentes tipo, porque las mentes introducen **heterogeneidad
en el procesamiento** que no captura ninguna distribución paramétrica.

---

## Referencias

- Gould, S.J. & Vrba, E.S. (1982). Exaptation — a missing term in the science
  of form. *Paleobiology*, 8(1), 4-15.
- Gould, S.J. & Lewontin, R.C. (1979). The spandrels of San Marco and the
  Panglossian paradigm: a critique of the adaptationist programme.
  *Proceedings of the Royal Society B*, 205(1161), 581-598.
- Wilson, D.S. & Sober, E. (1994). Reintroducing group selection to the
  human behavioral sciences. *Behavioral and Brain Sciences*, 17(4), 585-608.
- Okasha, S. (2006). *Evolution and the Levels of Selection*. Oxford UP.
- Dawkins, R. (1982). *The Extended Phenotype*. Freeman.
- Lerer, I.A. (2026). Simulating Institutional Dynamics: A Multi-Agent Framework
  for Predicting Legal Reform Outcomes Using Extended Phenotype Theory. Zenodo.
- Meta AI Research (2025). TRIBE v2: A Foundation Model of Vision, Audition,
  and Language for In-Silico Neuroscience.
