# SGM 0.9.3-B — Cadastro do Processo

## Campos obrigatórios

- tribunal;
- região do TRT;
- Vara do Trabalho;
- município;
- UF;
- número CNJ;
- classe processual;
- reclamante;
- reclamada.

## Campos opcionais

- magistrado;
- perito ou calculista;
- assistentes técnicos;
- advogados.

O formulário cria diretamente `OrgaoJulgador` e
`IdentificacaoProcesso`, preservando as validações do domínio.
