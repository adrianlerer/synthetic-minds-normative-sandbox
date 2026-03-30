# Metodología — SNMS

## Diseño experimental

### Condición de control
Replicar el experimento 816-agentes **sin** MindProfiles. Permite aislar
el efecto de agregar mentes tipo sobre los resultados emergentes.

### Condición experimental
Mismo experimento con MindProfiles activados. Comparar:
- CLI con/sin mentes
- FDI: sólo medible con SNMS (inexistente en 816-agentes)
- Spandrels: sólo detectables con SNMS
- MSR: sólo medible con SNMS

## Pipeline de ejecución

```
1. Cargar configuración del experimento (YAML)
2. Instanciar agentes con MindProfiles
3. Crear norma con función original declarada
4. Loop de simulación:
   a. Cada agente decide_action() (modulado por mente)
   b. Aplicar acciones al LegalEnvironment
   c. HBU update (modulado por plasticidad bayesiana)
   d. SpandrelDetector.scan_round()
   e. MultilevelSelectionEngine.compute_snapshot()
   f. Actualizar current_function de la norma
   g. Registrar métricas
5. Post-análisis: FDI, MSR, spandrels, CLI
```

## Calibración de MindProfiles

Los MindProfiles son calibrados empíricamente sobre:
- Encuestas CEDEC/Latinobarómetro (ciudadanos)
- Análisis de votos CSJN 1983-2024 (jueces)
- Registros de negociaciones colectivas MTSS (dirigentes)
- Comportamiento de lobbying UIA/CAME (empresas)

La calibración es iterativa: si el modelo sin mentes tipo reproduce
el CLI≈0.89 del 816-agentes, el modelo con mentes debe hacerlo también
(validación interna) antes de agregar predicciones novedosas.
