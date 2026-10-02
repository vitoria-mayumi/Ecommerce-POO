# O pacote `produto` reexporta a hierarquia de Single Table Inheritance.
#
# A ordem importa: `Produto` (classe base) precisa ser importada ANTES
# das subclasses, pois cada subclasse faz `from models.produto import
# Produto`. Se as subclasses viessem primeiro, haveria importação
# circular (o __init__ ainda não teria o nome `Produto` definido).

from models.produto.produto import Produto
from models.produto.produto_fisico import ProdutoFisico
from models.produto.produto_digital import ProdutoDigital
from models.produto.produto_servico import ProdutoServico

__all__ = [
    "Produto",
    "ProdutoFisico",
    "ProdutoDigital",
    "ProdutoServico",
]
