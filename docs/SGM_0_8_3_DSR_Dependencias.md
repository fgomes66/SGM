# SGM 0.8.3 — Reflexo em DSR e Dependências

## Fórmula parametrizada

```text
FM-DSR-001

Reflexo em DSR =
    valor da verba-base
    ÷ dias úteis
    × dias de repouso
```

A release não presume quais dias devem ser considerados. O usuário ou
o plano de cálculo deverá fornecer os parâmetros respaldados pelo caso.

## Grafo de dependências

A dependência inicial registrada é:

```text
HORA_EXTRA → DSR
```

O grafo:

- é imutável;
- rejeita ciclos;
- calcula a ordem topológica;
- informa predecessoras;
- informa dependentes diretos;
- informa impactos transitivos.

## Componentes

- `CodigoVerba`
- `DependenciaVerba`
- `GrafoDependenciasVerbas`
- `ParametrosDSR`
- `ReflexoDSR`
- `ServicoReflexoDSR`
