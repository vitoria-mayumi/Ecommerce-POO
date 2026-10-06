"""
DTO = Data Transfer Object (Objeto de Transferência de Dados).

Pense neste arquivo como um "formulário padronizado". Quando alguém
envia os dados de um produto para o sistema (em formato JSON, que é
texto solto vindo de fora), não dá para confiar que esses dados vêm
limpos: podem ter espaços sobrando, letras maiúsculas, números escritos
como texto, campos faltando, etc.

O `ProdutoDTO` é o objeto que recebe esses dados brutos, organiza em
campos com nomes claros e já aplica uma primeira limpeza/conversão.
Assim, o resto do sistema (service, models) recebe dados previsíveis,
em vez de um amontoado de texto cru.

É também um exemplo de ENCAPSULAMENTO: a regra de "como transformar o
JSON externo em dados utilizáveis" fica concentrada aqui, num lugar só.
"""

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
