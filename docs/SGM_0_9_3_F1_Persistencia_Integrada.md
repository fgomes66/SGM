# SGM 0.9.3-F1 — Persistência Integrada

A release consolida o fluxo Processo → Contrato → Eventos → Cálculo →
Memória.

Após cada operação válida, o estado completo do caso é salvo
automaticamente no arquivo JSON do processo.

## Regras de fluxo

- contrato exige processo ativo;
- eventos exigem processo e contrato;
- cálculo exige processo e contrato;
- memória exige ao menos um cálculo;
- exclusões também são persistidas automaticamente.

A memória continua sendo derivada dos resultados persistidos, sem
recalcular valores.
