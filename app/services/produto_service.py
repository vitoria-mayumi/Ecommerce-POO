"""
CAMADA DE SERVIÇO do catálogo.

Com a hierarquia polimórfica de `Produto`, o serviço deixa de usar
cadeias de `if tipo == ...` para decidir comportamento. Ele apenas:

  1. escolhe a CLASSE concreta correta (uma única fábrica);
  2. deixa cada subclasse validar e calcular o que lhe compete
     (encapsulamento + polimorfismo).

Isso aplica o princípio Aberto/Fechado: para suportar um novo tipo
de produto, cria-se uma nova subclasse — o serviço quase não muda.
"""

from sqlalchemy import func

from extensions import db
from models.produto import Produto


class ProdutoService:

    @staticmethod
    def criar(produto_dto):
        """Orquestra a criação: garante unicidade de código, delega a
        construção do tipo certo à fábrica polimórfica de `Produto` e
        persiste. Nenhuma regra específica de tipo vive aqui."""

        produto_existente = Produto.query.filter_by(
            codigo=produto_dto.codigo
        ).first()

        if produto_existente:
            raise ValueError(
                "Já existe um produto com esse código."
            )

        produto = Produto.criar(produto_dto)

        db.session.add(produto)
        db.session.commit()

        return produto

    @staticmethod
    def listar():

        return Produto.query.order_by(
            Produto.nome
        ).all()

    @staticmethod
    def buscar_por_nome(nome):

        return Produto.query.filter(
            func.lower(Produto.nome).like(
                f"%{nome.lower()}%"
            )
        ).all()

    @staticmethod
    def atualizar_estoque(produto_id, estoque_dto):

        if produto_id <= 0:
            raise ValueError(
                "Índice de produto inválido."
            )

        produto = db.session.get(
            Produto,
            produto_id
        )

        if produto is None:
            raise LookupError(
                "Produto não encontrado."
            )

        if not produto.pode_ter_estoque():
            raise ValueError(
                "Somente produtos físicos possuem estoque."
            )

        if estoque_dto.quantidade is None:
            raise ValueError(
                "A quantidade informada é inválida."
            )

        produto.ajustar_estoque(estoque_dto.quantidade)

        db.session.commit()

        return produto
