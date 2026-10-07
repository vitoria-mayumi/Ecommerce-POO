from dataclasses import dataclass
from typing import Any, List

from utils.validacoes import converter_inteiro


@dataclass
#Os dados ficam organizados dentro de objetos(Encapsulamento)
class ItemPedidoDTO:
    produto_id: int
    quantidade: int

    @classmethod
    #Esconde a complexidade da conversão do JSON(Abstração)
    def from_dict(cls, dados):
        return cls(
            produto_id=converter_inteiro(
                dados.get("produto_id")
            ),
            quantidade=converter_inteiro(
                dados.get("quantidade")
            )
        )


@dataclass
#Um objeto é formado por outros objetos(Composição)
class PedidoDTO:
    cliente_id: int
    itens: List[ItemPedidoDTO]

    @classmethod
    def from_dict(cls, dados):
        itens = dados.get("itens", [])

        if isinstance(itens, list):
            itens = [
                ItemPedidoDTO.from_dict(item)
                for item in itens
                if isinstance(item, dict)
            ]

        return cls(
            cliente_id=converter_inteiro(
                dados.get("cliente_id")
            ),
            itens=itens
        )