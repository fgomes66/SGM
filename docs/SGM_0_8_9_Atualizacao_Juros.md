# SGM 0.8.9 — Atualização Monetária e Juros

## Fórmulas

```text
FM-COR-001
valor corrigido = valor original × fator de correção
```

```text
FM-JUR-001
valor com juros = base dos juros × fator de juros
```

```text
FM-AJ-001
correção monetária → juros
```

## Componentes

- `TipoAtualizacao`
- `FatorAtualizacao`
- `ResultadoAtualizacao`
- `ResultadoAtualizacaoJuros`
- `ServicoAtualizacao`

## Princípios

- correção e juros são etapas independentes;
- fatores são externos e parametrizados;
- cada fator registra período, fonte e fundamento;
- nenhum índice oficial é embutido;
- o plano de cálculo define a ordem e os critérios.

## Limites

A release não importa séries históricas, não calcula fatores diários ou
mensais e não decide qual índice ou taxa é juridicamente aplicável.
