"""
DTO de ajuste de estoque.

Mesma ideia do `ProdutoDTO`: concentra a conversão/limpeza dos dados
brutos vindos do JSON num único lugar. Antes, a CONVERSÃO de
`quantidade` (texto -> inteiro) acontecia dentro da controller, o que
misturava "entrada HTTP" com "interpretação do dado" — responsabilidade
que não é da camada de apresentação.

Agora a controller apenas repassa o corpo cru; este DTO padroniza o
dado e o service aplica a regra de negócio.
"""

from dataclasses import dataclass
from typing import Any, Optional

from utils.validacoes import converter_inteiro


@dataclass
class EstoqueDTO:
    quantidade: Optional[int] = None

    @classmethod
    def from_dict(cls, dados: Any) -> "EstoqueDTO":
        dados = dados or {}
        return cls(
            quantidade=converter_inteiro(dados.get("quantidade"))
        )
