# SGM 0.9.0 — Liquidação Integrada

## Objetivo

Executar um fluxo completo e reproduzível usando os motores homologados
entre as versões 0.8.1 e 0.8.9.

## Fluxo

```text
base remuneratória
  → valor da hora
  → horas extras
  → DSR
  → bases de incidência
  → FGTS
  → férias e terço
  → 13º
  → aviso-prévio
  → subtotal
  → correção
  → juros
  → memória de cálculo
```

## Componentes

- `ModoLiquidacao`
- `ConfiguracaoIncidencia`
- `PlanoLiquidacaoIntegrada`
- `VerbaLiquidada`
- `MemoriaCalculo`
- `LiquidacaoTrabalhista`
- `MotorLiquidacaoTrabalhista`

## Escopo

A versão integra uma liquidação simples de diferenças de horas extras e
reflexos. Cada incidência deve ser configurada individualmente para
horas extras e DSR em cada base.

## Limites

Ainda não há:

- interface gráfica;
- leitura automática de petição ou sentença;
- competências múltiplas;
- tabelas oficiais de índices;
- descontos previdenciários e fiscais;
- custas e honorários;
- exportação Word, PDF, Excel ou PJe-Calc;
- persistência em banco de dados.
