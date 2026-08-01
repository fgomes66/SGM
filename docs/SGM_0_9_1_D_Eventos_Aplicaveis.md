# SGM 0.9.1-D — Eventos Contratuais Aplicáveis

## Componentes

- `EventoContratualAplicavel`
- `EstadoContratual`
- `LinhaTempoAplicada`
- `AplicadorEventosContratuais`

## Eventos suportados

- admissão;
- reajuste;
- promoção;
- alteração de jornada;
- alteração de divisor;
- afastamento;
- retorno;
- rescisão.

## Regras

- os efeitos começam na competência do evento;
- competências anteriores permanecem intactas;
- salário, divisor e jornada propagam-se prospectivamente;
- competências inativas não geram planos;
- não são permitidos eventos após a rescisão;
- os planos ativos são gerados automaticamente a partir do modelo.

## Limite da fase

A versão ainda não executa e consolida automaticamente todos os planos
produzidos. Essa integração final será realizada na 0.9.1-E.
