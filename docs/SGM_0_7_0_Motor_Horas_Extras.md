# SGM 0.7.0 — Motor de Horas Extras

## Finalidade

Apurar quantitativamente horas normais e horas extras sem calcular valores
monetários.

## Entradas

- registros diários de tempo trabalhado;
- limite diário;
- limite semanal;
- adicional previsto;
- ativação ou desativação de cada critério.

## Saídas

- horas normais;
- extras pelo limite diário;
- extras pelo limite semanal;
- extras semanais sem duplicar as já reconhecidas diariamente;
- total de horas extras;
- memória técnica da apuração.

## Regra contra duplicidade

O excedente semanal é reduzido pelas horas extras já reconhecidas pelo
critério diário.

Exemplo:

```text
Total semanal: 45h
Extras diárias já reconhecidas: 5h
Excedente semanal bruto: 1h
Extras semanais adicionais: 0h
Total de extras: 5h
```

## Limites desta versão

Ainda não estão incluídos:

- pagamento em dinheiro;
- adicional noturno;
- domingos e feriados;
- compensação e banco de horas;
- tolerância de marcação;
- escalas 12x36;
- critérios convencionais por dia;
- jornadas atravessando a meia-noite.

## Próxima evolução

A próxima versão deverá converter a quantidade de horas extras em valor,
utilizando salário, divisor, adicional e memória matemática versionada.
