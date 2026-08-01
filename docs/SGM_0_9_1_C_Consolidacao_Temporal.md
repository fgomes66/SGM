# SGM 0.9.1-C — Consolidação Temporal

## Objetivo

Reunir resultados mensais independentes em uma única memória temporal.

## Componentes

- `ResultadoConsolidado`
- `ConsolidadorCompetencias`

## Regras

- exige ao menos uma competência;
- rejeita competências duplicadas;
- ordena os resultados cronologicamente;
- exige moeda uniforme;
- soma subtotais e valores finais separadamente;
- preserva os objetos mensais originais;
- produz memória consolidada por competência.

## Limite da fase

A consolidação não gera automaticamente os planos mensais e não aplica
eventos contratuais. Esses recursos serão desenvolvidos na 0.9.1-D.
