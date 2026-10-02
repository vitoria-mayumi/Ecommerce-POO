# As subclasses PRECISAM ser importadas aqui para que o SQLAlchemy
# registre suas `polymorphic_identity` no mapper do Single Table
# Inheritance. Sem isso, o ORM não saberia reconstruir cada linha
# da tabela `produtos` na classe correta.

from models.produto import (
    Produto,
    ProdutoFisico,
    ProdutoDigital,
    ProdutoServico,
)
from models.cliente import Cliente
from models.pedido import Pedido
from models.item_pedido import ItemPedido

__all__ = [
    "Produto",
    "ProdutoFisico",
    "ProdutoDigital",
    "ProdutoServico",
    "Cliente",
    "Pedido",
    "ItemPedido"
]
