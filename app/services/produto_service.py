from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models.produto import Produto


class ProdutoService:

    @staticmethod
    def criar(produto_dto):

        if not produto_dto.codigo:
            raise ValueError(
                "O código do produto é obrigatório."
            )

        if not produto_dto.nome:
            raise ValueError(
                "O nome do produto é obrigatório."
            )

        if produto_dto.tipo not in [
            "fisico",
            "digital",
            "servico"
        ]:
            raise ValueError(
                "Tipo inválido. Utilize: fisico, digital ou servico."
            )

        if produto_dto.preco is None:
            raise ValueError(
                "Preço inválido. Informe um valor numérico "
                "maior ou igual a zero."
            )

        produto_existente = Produto.query.filter_by(
            codigo=produto_dto.codigo
        ).first()

        if produto_existente:
            raise ValueError(
                "Já existe um produto com esse código."
            )

        produto = Produto(
            codigo=produto_dto.codigo,
            nome=produto_dto.nome,
            preco=produto_dto.preco,
            tipo=produto_dto.tipo
        )

        if produto_dto.tipo == "fisico":

            if (
                produto_dto.estoque is None or
                produto_dto.estoque < 0
            ):
                raise ValueError(
                    "Estoque inválido para produto físico."
                )

            if produto_dto.frete is None:
                raise ValueError(
                    "Valor de frete inválido."
                )

            produto.estoque = produto_dto.estoque
            produto.frete = produto_dto.frete

        elif produto_dto.tipo == "digital":

            produto.estoque = None
            produto.frete = Decimal("0.00")

        elif produto_dto.tipo == "servico":

            if (
                produto_dto.prazo_execucao is None or
                produto_dto.prazo_execucao < 0
            ):
                raise ValueError(
                    "Prazo de execução inválido para o serviço."
                )

            produto.prazo_execucao = (
                produto_dto.prazo_execucao
            )

            produto.frete = Decimal("0.00")

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
    def atualizar_estoque(produto_id, quantidade):

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

        if produto.tipo != "fisico":
            raise ValueError(
                "Somente produtos físicos possuem estoque."
            )

        if quantidade is None:
            raise ValueError(
                "A quantidade informada é inválida."
            )

        novo_estoque = produto.estoque + quantidade

        if novo_estoque < 0:
            raise ValueError(
                "Operação inválida. O estoque não pode ficar negativo. "
                f"Estoque atual: {produto.estoque}."
            )

        produto.estoque = novo_estoque

        db.session.commit()

        return produto
