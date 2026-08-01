# SGM 0.8.5 — Motor do FGTS

## Fórmula

```text
FM-FGTS-001

FGTS = base de incidência do FGTS × alíquota parametrizada
```

## Componentes

- `AliquotaFGTS`
- `FGTSApurado`
- `ServicoFGTS`

## Regras

- a base deve ser do tipo `FGTS`;
- a alíquota deve ser `Decimal` entre 0 e 1;
- nenhuma alíquota é presumida pelo serviço;
- o total é arredondado para centavos apenas ao final;
- a memória preserva as parcelas incluídas e excluídas da base.

## Limite desta release

A versão calcula o depósito de FGTS sobre uma base composta. A multa
rescisória não integra esta entrega e será modelada separadamente para
evitar mistura entre obrigações distintas.
