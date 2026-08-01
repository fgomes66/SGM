# SGM 0.6.0 — Fundação do Motor Jornada

## Finalidade

Representar e apurar tempo de trabalho diário sem calcular valores financeiros.

## Unidade interna

O SGM utiliza minutos inteiros como unidade interna.

Exemplo:

```text
08h15min = 495 minutos
```

A conversão para horas decimais ou texto ocorre apenas na apresentação.

## Componentes

- `Tempo`
- `Horario`
- `Intervalo`
- `PeriodoTrabalho`
- `ResultadoJornada`
- `CalculadoraJornada`

## Escopo desta versão

Incluído:

- períodos dentro do mesmo dia;
- um ou vários intervalos;
- cálculo bruto;
- cálculo total dos intervalos;
- cálculo líquido;
- validação de intervalos;
- advertências básicas.

Não incluído:

- travessia da meia-noite;
- hora noturna reduzida;
- escalas;
- feriados;
- banco de horas;
- tolerância legal;
- horas extras;
- cálculos monetários.

## Princípio

O Motor Jornada apura tempo. O futuro Motor de Horas Extras aplicará os
limites jurídicos e converterá os excedentes em quantidade remunerável.
