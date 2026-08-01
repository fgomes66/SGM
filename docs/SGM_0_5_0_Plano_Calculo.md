# SGM 0.5.0 — Plano de Cálculo

## Finalidade

O Plano de Cálculo é a camada operacional situada entre o critério jurídico
homologado e o futuro motor matemático.

## Cadeia implementada

```text
Comando Judicial
↓
Critério Jurídico Homologado
↓
Item do Plano de Cálculo
↓
Plano em Revisão
↓
Plano Homologado
↓
Plano Apto para Execução
```

## Regras centrais

1. Item somente entra no plano com critério jurídico homologado.
2. O item precisa apontar para o mesmo critério validado.
3. Códigos de itens não podem se repetir.
4. Plano vazio não pode seguir para revisão.
5. Somente plano em revisão pode ser homologado.
6. Plano homologado não pode ser editado.
7. A homologação gera hash SHA-256 de integridade.
8. O futuro motor matemático somente poderá executar plano homologado e íntegro.

## Nota de interoperabilidade

O Plano de Cálculo servirá como representação intermediária para futuras
saídas, incluindo memória SGM, planilhas, relatórios e exportação compatível
com o formato `.PJC`, condicionada à validação técnica no PJe-Calc Cidadão.
