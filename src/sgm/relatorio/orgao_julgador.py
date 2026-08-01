from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrgaoJulgador:
    tribunal: str
    regiao_trt: int
    vara: str
    municipio: str
    uf: str

    def __post_init__(self) -> None:
        tribunal = self.tribunal.strip()
        vara = self.vara.strip()
        municipio = self.municipio.strip()
        uf = self.uf.strip().upper()

        object.__setattr__(self, "tribunal", tribunal)
        object.__setattr__(self, "vara", vara)
        object.__setattr__(self, "municipio", municipio)
        object.__setattr__(self, "uf", uf)

        if not tribunal:
            raise ValueError("O tribunal é obrigatório.")

        if not isinstance(self.regiao_trt, int):
            raise TypeError("A região do TRT deve ser inteira.")

        if self.regiao_trt < 1 or self.regiao_trt > 24:
            raise ValueError(
                "A região do TRT deve estar entre 1 e 24."
            )

        if not vara:
            raise ValueError("A Vara do Trabalho é obrigatória.")

        if not municipio:
            raise ValueError(
                "O município do órgão julgador é obrigatório."
            )

        if len(uf) != 2 or not uf.isalpha():
            raise ValueError(
                "A UF deve possuir exatamente duas letras."
            )

    @property
    def descricao_completa(self) -> str:
        return (
            f"{self.tribunal} da {self.regiao_trt}ª Região — "
            f"{self.vara} — {self.municipio}/{self.uf}"
        )
