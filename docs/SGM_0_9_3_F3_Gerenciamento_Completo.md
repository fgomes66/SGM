# SGM 0.9.3-F3 — Gerenciamento Completo de Processos

A release corrige definitivamente a inicialização do menu Arquivo e
mantém uma barra visível de acesso rápido.

## Operações disponíveis

- Novo processo;
- Abrir processo;
- Salvar;
- Salvar como;
- Fechar processo;
- Sair.

## Prevenção de regressão

O teste da criação do menu agora executa efetivamente o método com objetos
simulados do Tkinter. Assim, referências inexistentes como `_menu_self`
não podem mais passar apenas por testes de inspeção textual.
