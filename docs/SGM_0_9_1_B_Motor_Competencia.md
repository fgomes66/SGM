# SGM 0.9.1-B — Motor por Competência

## Objetivo

Executar a liquidação integrada 0.9.0 dentro de uma competência mensal
explicitamente identificada.

## Componentes

- `PlanoCompetencia`
- `ResultadoCompetencia`
- `MotorCompetencia`

## Fluxo

```text
competência
  → plano financeiro da competência
  → motor integrado 0.9.0
  → subtotal mensal
  → valor final mensal
  → memória individual
```

## Garantias

- a competência do plano deve coincidir com a base remuneratória;
- cada execução é independente;
- resultados anteriores não são alterados por competências posteriores;
- a memória identifica competência, referência e versão do motor;
- nenhuma consolidação entre meses é feita nesta fase.

## Próxima fase

A 0.9.1-C consolidará múltiplos `ResultadoCompetencia`.
