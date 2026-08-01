# SGM 0.9.2-D — Exportadores Profissionais

## Componentes

- `FormatoExportacao`
- `DocumentoExportavel`
- `ExportadorPDF`
- `ExportadorDOCX`
- `ExportadorXLSX`
- `ExportadorCSV`
- `ServicoExportacao`

## Características

- não depende de bibliotecas externas;
- cria diretórios automaticamente;
- rejeita sobrescrita por padrão;
- permite sobrescrita explícita;
- usa uma interface comum;
- preserva integralmente o conteúdo do domínio.

## Formatos

- PDF mínimo válido;
- DOCX Open XML;
- XLSX Open XML com quatro planilhas;
- CSV UTF-8 com BOM e separador ponto e vírgula.
