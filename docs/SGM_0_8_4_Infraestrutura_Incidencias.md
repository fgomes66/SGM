# SGM 0.8.4 — Infraestrutura de Incidências

## Objetivo

Compor bases de cálculo posteriores sem esconder decisões jurídicas.

## Princípio central

Nenhuma verba incide automaticamente. Cada parcela recebe uma regra
específica para uma base de destino.

Exemplo:

```text
Hora extra
  ├── regra para FGTS
  ├── regra para férias
  ├── regra para 13º
  └── regra para INSS
```

As regras podem divergir porque cada base possui fundamento próprio.

## Componentes

- `TipoBaseIncidencia`
- `RegraIncidencia`
- `ParcelaIncidencia`
- `ComposicaoBaseIncidencia`
- `ServicoComposicaoBase`

## Fórmula técnica

```text
FM-BASE-INC-001

base = soma das parcelas expressamente incluídas
```

Parcelas excluídas continuam preservadas na memória, com o respectivo
fundamento.
