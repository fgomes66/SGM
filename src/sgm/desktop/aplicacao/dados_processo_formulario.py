from __future__ import annotations

from dataclasses import dataclass

from sgm.relatorio import IdentificacaoProcesso, OrgaoJulgador


@dataclass(frozen=True, slots=True)
class DadosProcessoFormulario:
    tribunal: str = "Tribunal Regional do Trabalho"
    regiao_trt: str = "1"
    vara: str = ""
    municipio: str = ""
    uf: str = ""
    numero_processo: str = ""
    classe_processual: str = "Reclamação Trabalhista"
    reclamante: str = ""
    reclamada: str = ""
    magistrado: str = ""
    perito: str = ""
    assistente_reclamante: str = ""
    assistente_reclamada: str = ""
    advogado_reclamante: str = ""
    advogado_reclamada: str = ""

    def __post_init__(self) -> None:
        for campo in self.__dataclass_fields__:
            valor = getattr(self, campo)
            if isinstance(valor, str):
                object.__setattr__(self, campo, valor.strip())

    def validar(self) -> tuple[str, ...]:
        erros: list[str] = []

        if not self.tribunal:
            erros.append("Informe o tribunal.")

        try:
            regiao = int(self.regiao_trt)
        except ValueError:
            erros.append("A região do TRT deve ser numérica.")
        else:
            if regiao < 1 or regiao > 24:
                erros.append("A região do TRT deve estar entre 1 e 24.")

        if not self.vara:
            erros.append("Informe a Vara do Trabalho.")
        if not self.municipio:
            erros.append("Informe o município.")
        if len(self.uf) != 2 or not self.uf.isalpha():
            erros.append("A UF deve possuir duas letras.")
        if not self.numero_processo:
            erros.append("Informe o número do processo.")
        if not self.classe_processual:
            erros.append("Informe a classe processual.")
        if not self.reclamante:
            erros.append("Informe o reclamante.")
        if not self.reclamada:
            erros.append("Informe a reclamada.")

        if not erros:
            try:
                self.criar_identificacao()
            except (TypeError, ValueError) as erro:
                erros.append(str(erro))

        return tuple(erros)

    def criar_identificacao(self) -> IdentificacaoProcesso:
        orgao = OrgaoJulgador(
            tribunal=self.tribunal,
            regiao_trt=int(self.regiao_trt),
            vara=self.vara,
            municipio=self.municipio,
            uf=self.uf,
        )
        return IdentificacaoProcesso(
            orgao_julgador=orgao,
            numero_processo=self.numero_processo,
            classe_processual=self.classe_processual,
            reclamante=self.reclamante,
            reclamada=self.reclamada,
            magistrado=self.magistrado or None,
            perito=self.perito or None,
            assistente_reclamante=(
                self.assistente_reclamante or None
            ),
            assistente_reclamada=(
                self.assistente_reclamada or None
            ),
            advogado_reclamante=(
                self.advogado_reclamante or None
            ),
            advogado_reclamada=(
                self.advogado_reclamada or None
            ),
        )
