from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from sgm.desktop.persistencia.registro_processo import (
    RegistroProcesso,
)
from sgm.desktop.persistencia.serializador_processo import (
    SerializadorProcesso,
)


def _normalizar_nome(referencia: str) -> str:
    permitido = []
    for caractere in referencia.strip():
        if caractere.isalnum() or caractere in ("-", "_"):
            permitido.append(caractere)
        elif caractere.isspace():
            permitido.append("_")
    nome = "".join(permitido).strip("_")
    if not nome:
        raise ValueError(
            "A referência não produz um nome de arquivo válido."
        )
    return nome


class RepositorioProcessosJSON:
    def __init__(self, pasta: Path) -> None:
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.arquivo_indice = self.pasta / "ultimo_processo.json"

    def caminho_para(self, referencia: str) -> Path:
        return self.pasta / (
            f"{_normalizar_nome(referencia)}_processo.json"
        )


    def existe(self, referencia: str) -> bool:
        return self.caminho_para(referencia).exists()

    def salvar(
        self,
        registro: RegistroProcesso,
    ) -> Path:
        destino = self.caminho_para(registro.referencia)
        dados = SerializadorProcesso.para_dict(registro)
        conteudo = json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        self._gravar_atomico(destino, conteudo)
        self._gravar_atomico(
            self.arquivo_indice,
            json.dumps(
                {"referencia": registro.referencia},
                ensure_ascii=False,
                indent=2,
            ),
        )
        return destino

    def carregar(
        self,
        referencia: str,
    ) -> RegistroProcesso:
        caminho = self.caminho_para(referencia)
        if not caminho.exists():
            raise FileNotFoundError(
                f"Processo não encontrado: {referencia}"
            )
        dados = json.loads(
            caminho.read_text(encoding="utf-8")
        )
        return SerializadorProcesso.de_dict(dados)

    def carregar_ultimo(
        self,
    ) -> RegistroProcesso | None:
        if not self.arquivo_indice.exists():
            return None

        indice = json.loads(
            self.arquivo_indice.read_text(encoding="utf-8")
        )
        referencia = indice.get("referencia")
        if not referencia:
            return None

        try:
            return self.carregar(referencia)
        except FileNotFoundError:
            return None

    def listar_referencias(self) -> tuple[str, ...]:
        referencias = []
        for arquivo in sorted(
            self.pasta.glob("*_processo.json")
        ):
            if arquivo == self.arquivo_indice:
                continue
            try:
                dados = json.loads(
                    arquivo.read_text(encoding="utf-8")
                )
                referencia = dados.get("referencia")
                if referencia:
                    referencias.append(referencia)
            except (OSError, json.JSONDecodeError):
                continue
        return tuple(referencias)

    @staticmethod
    def _gravar_atomico(
        destino: Path,
        conteudo: str,
    ) -> None:
        destino.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        temporario = None

        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=destino.parent,
                prefix=f".{destino.stem}_",
                suffix=".tmp",
                delete=False,
            ) as arquivo:
                temporario = Path(arquivo.name)
                arquivo.write(conteudo)
                arquivo.flush()
                os.fsync(arquivo.fileno())

            os.replace(temporario, destino)
        finally:
            if temporario and temporario.exists():
                temporario.unlink()
