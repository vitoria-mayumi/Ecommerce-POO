"""
SUBCLASSE CONCRETA -> Pilares: Herança + Polimorfismo.

`ProdutoDigital` representa itens entregues eletronicamente
(e-books, licenças, downloads). Não tem estoque físico e nunca
cobra frete -> implementa o contrato de forma diferente do físico.

Não sobrescreve os ganchos `_validar_estoque`/`_validar_frete`, então
herda o comportamento da base: qualquer tentativa de atribuir estoque
ou frete a um produto digital é recusada.
"""

from decimal import Decimal

from models.produto import Produto


class ProdutoDigital(Produto):

    __mapper_args__ = {
        "polymorphic_identity": "digital"
    }

    @classmethod
    def from_dto(cls, dto) -> "ProdutoDigital":
        return cls._montar_base(dto)

    def calcular_frete(self, quantidade: int) -> Decimal:
        return Decimal("0.00")

    def pode_ter_estoque(self) -> bool:
        return False

    def descricao_tipo(self) -> str:
        return "Produto digital (entrega eletrônica, sem frete)"
