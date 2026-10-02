"""
SUBCLASSE CONCRETA -> Pilares: Herança + Polimorfismo.

`ProdutoDigital` representa itens entregues eletronicamente
(e-books, licenças, downloads). Não tem estoque físico e nunca
cobra frete -> implementa o contrato de forma diferente do físico.
"""

from decimal import Decimal

from models.produto import Produto


class ProdutoDigital(Produto):

    __mapper_args__ = {
        "polymorphic_identity": "digital"
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("tipo", "digital")
        super().__init__(*args, **kwargs)
        # Produto digital: sem estoque, frete sempre zero.
        self.estoque = None
        self.frete = Decimal("0.00")

    # -------- POLIMORFISMO: mesmo contrato, comportamento próprio -----
    def calcular_frete(self, quantidade: int) -> Decimal:
        return Decimal("0.00")

    def pode_ter_estoque(self) -> bool:
        return False

    def descricao_tipo(self) -> str:
        return "Produto digital (entrega eletrônica, sem frete)"
