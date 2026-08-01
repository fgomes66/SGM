# SGM 0.8.0 — Core Financeiro

## Finalidade

Transformar valores monetários em objetos imutáveis, rastreáveis,
serializáveis e auditáveis.

## Componentes

- `OrigemFinanceira`
- `TipoOperacaoFinanceira`
- `OperacaoFinanceira`
- `ValorMonetario`

## Regras

1. `float` é proibido.
2. Todo valor utiliza `Decimal`.
3. Toda operação retorna novo objeto.
4. O objeto original permanece imutável.
5. Toda operação gera registro no histórico.
6. A origem financeira permanece vinculada.
7. Operações entre moedas diferentes são bloqueadas.
8. O arredondamento monetário é explícito e usa `ROUND_HALF_UP`.
9. Aplicar percentual e acrescer percentual são operações distintas.
10. Serialização e desserialização preservam o DNA financeiro.

## Exemplo

```python
salario = ValorMonetario.criar("3000.00", origem)
valor_hora = salario.dividir(Decimal("220"))
hora_extra = valor_hora.acrescer_percentual(Decimal("0.50"))
total = hora_extra.multiplicar(Decimal("180")).arredondar_centavos()
```

Resultado:

```text
R$ 3.681,82
```

O histórico preserva criação, divisão, acréscimo, multiplicação e
arredondamento.
