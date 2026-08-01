# SGM 0.9.1-A — Modelo Temporal

## Objetivo

Representar competências mensais, períodos contratuais e eventos que
alteram o contrato ao longo do tempo.

## Componentes

- `CompetenciaCalculo`
- `PeriodoContratual`
- `TipoEventoContratual`
- `EventoContratual`
- `LinhaTempoContratual`

## Regras

- competências usam o formato `AAAA-MM`;
- períodos são inclusivos;
- eventos devem estar dentro do período;
- a linha do tempo ordena eventos cronologicamente;
- todos os objetos são imutáveis;
- adicionar evento produz uma nova linha do tempo.

## Limite da fase

O modelo ainda não altera salário, jornada ou divisor. Ele apenas
representa e valida a cronologia. A aplicação financeira dos eventos
será implementada nas fases seguintes.
