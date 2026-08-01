# SGM 0.5.1 — Finalidades, Cenários e Premissas

## Finalidade

Permitir que o SGM diferencie claramente:

- cálculo estimativo da petição inicial;
- simulação de negociação;
- cálculo para acordo;
- liquidação de sentença;
- impugnação de cálculos;
- atualização da execução.

## Regra estrutural

### Plano estimativo

Origem:

```text
Fatos alegados
↓
Evidências disponíveis
↓
Premissas profissionais
↓
Cenário estimativo revisado
↓
Plano de cálculo
```

### Plano judicial

Origem:

```text
Título executivo
↓
Comando judicial
↓
Critério jurídico homologado
↓
Plano de cálculo
```

## Ressalva obrigatória futura

As memórias estimativas deverão declarar:

> Cálculo estimativo elaborado antes da formação do título executivo, com
> base nos fatos alegados, documentos disponíveis e premissas declaradas.
> Os valores poderão sofrer alteração conforme defesa, prova produzida e
> decisão judicial.

## Próxima integração

Na próxima atualização, o `PlanoCalculo` será vinculado formalmente ao
`ContextoPlanoCalculo`, impedindo mistura silenciosa entre estimativa da
inicial e liquidação de sentença.
