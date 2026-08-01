# ADR-023 — Integração única dos exportadores

## Status

Aceita.

## Decisão

Um único serviço coordenará renderização e gravação dos formatos finais,
reutilizando os exportadores PDF e DOCX já homologados.

## Motivo

Isso evita duplicação, mantém uma única fonte de conteúdo e fornece uma
API simples para a futura interface gráfica.
