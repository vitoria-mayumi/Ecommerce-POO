from sqlalchemy import func

from extensions import db
from models.produto import Produto


class ProdutoService:

    @staticmethod
    def criar(produto_dto):

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
