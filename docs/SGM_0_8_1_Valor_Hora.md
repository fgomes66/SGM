# SGM 0.8.1 — Serviço de Valor da Hora

## Objetivo

Calcular o valor da hora a partir de uma base de cálculo rastreável e
de um divisor de jornada juridicamente fundamentado.

## Fórmula

```text
FM-VH-001
Valor da hora = base de cálculo ÷ divisor da jornada
```

## Objetos

- `TipoBaseCalculo`
- `BaseDeCalculo`
- `DivisorJornada`
- `ValorHora`
- `ServicoValorHora`

## Princípios preservados

- nenhum uso de `float`;
- matemática executada pelo Core Financeiro;
- serviço de domínio apenas orquestra;
- imutabilidade;
- precisão `Decimal`;
- histórico financeiro preservado;
- origem documental e critério jurídico vinculáveis;
- memória técnica resumida.

## Limite desta versão

O valor da hora não é arredondado para centavos. O sistema preserva a
precisão interna e deixa o arredondamento para o momento definido pela
fórmula financeira da verba.
