# SGM 0.9.2-E1 — Modelo do Relatório Técnico

## Componentes

- `TipoRelatorio`
- `OrgaoJulgador`
- `IdentificacaoProcesso`
- `ParametrosRelatorio`
- `MetadadosRelatorio`
- `RelatorioTecnico`

## Regras

- órgão julgador e número CNJ obrigatórios;
- magistrado e demais profissionais opcionais;
- hash SHA-256 validado;
- data de emissão com fuso horário;
- quantidades compatíveis com os documentos de origem;
- referências uniformes;
- objetos imutáveis;
- nenhuma regra de cálculo ou exportação.
