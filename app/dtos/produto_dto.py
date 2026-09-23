from dataclasses import dataclass
from typing import Any, Optional

from utils.validacoes import converter_inteiro, converter_preco


@dataclass
class ProdutoDTO:
    codigo: str
    nome: str
    tipo: str
    preco: Any
    estoque: Optional[int] = None
    frete: Any = 0
    prazo_execucao: Optional[int] = None

    @classmethod
    def from_dict(cls, dados):
        return cls(
            codigo=str(dados.get("codigo", "")).strip(),
            nome=str(dados.get("nome", "")).strip(),
            tipo=str(dados.get("tipo", "")).strip().lower(),
            preco=converter_preco(dados.get("preco")),
            estoque=converter_inteiro(dados.get("estoque")),
            frete=converter_preco(dados.get("frete", 0)),
            prazo_execucao=converter_inteiro(
                dados.get("prazo_execucao")
            )
        )
