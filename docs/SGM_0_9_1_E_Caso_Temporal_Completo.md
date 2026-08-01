# SGM 0.9.1-E — Caso Temporal Completo

## Objetivo

Integrar todas as fases da série 0.9.1:

```text
período e eventos
  → estados contratuais
  → planos ativos
  → cálculo por competência
  → consolidação temporal
  → memória cronológica única
```

## Componentes

- `PlanoCasoTemporal`
- `ResultadoCasoTemporal`
- `MotorCasoTemporal`

## Garantias

- eventos são aplicados prospectivamente;
- competências inativas não são calculadas;
- cada plano ativo produz exatamente um resultado;
- os resultados são consolidados em ordem cronológica;
- a memória mostra estados, eventos, competências e totais.

## Resultado arquitetural

A série 0.9.1 passa a oferecer um fluxo temporal ponta a ponta, desde o
contrato até a liquidação consolidada.
