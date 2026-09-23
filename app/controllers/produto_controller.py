from flask import Blueprint, request

from dtos.produto_dto import ProdutoDTO
from services.produto_service import ProdutoService
from utils.respostas import resposta_erro, resposta_sucesso


produto_controller = Blueprint(
    "produto_controller",
    __name__
)


@produto_controller.route(
    "/produtos",
    methods=["POST"]
)
def adicionar_produto():

    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    try:
        dto = ProdutoDTO.from_dict(dados)

        produto = ProdutoService.criar(dto)

        return resposta_sucesso(
            "Produto cadastrado com sucesso.",
            produto.to_dict(),
            201
        )

    except ValueError as erro:

        status = (
            409
            if "Já existe" in str(erro)
            else 400
        )

        return resposta_erro(
            str(erro),
            status
        )


@produto_controller.route(
    "/produtos",
    methods=["GET"]
)
def listar_produtos():

    produtos = ProdutoService.listar()

    if not produtos:
        return resposta_sucesso(
            "O catálogo está vazio.",
            []
        )

    return resposta_sucesso(
        "Catálogo encontrado.",
        [
            produto.to_dict()
            for produto in produtos
        ]
    )


@produto_controller.route(
    "/produtos/busca",
    methods=["GET"]
)
def buscar_produto():

    nome = request.args.get(
        "nome",
        ""
    ).strip()

    if not nome:
        return resposta_erro(
            "Informe o nome ou parte do nome "
            "para realizar a busca."
        )

    produtos = ProdutoService.buscar_por_nome(nome)

    if not produtos:
        return resposta_sucesso(
            "Nenhum produto encontrado.",
            []
        )

    return resposta_sucesso(
        "Produtos encontrados.",
        [
            produto.to_dict()
            for produto in produtos
        ]
    )


@produto_controller.route(
    "/produtos/<int:produto_id>/estoque",
    methods=["PATCH"]
)
def atualizar_estoque(produto_id):

    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    from utils.validacoes import converter_inteiro

    quantidade = converter_inteiro(
        dados.get("quantidade")
    )

    try:

        produto = ProdutoService.atualizar_estoque(
            produto_id,
            quantidade
        )

        return resposta_sucesso(
            "Estoque atualizado com sucesso.",
            produto.to_dict()
        )

    except LookupError as erro:

        return resposta_erro(
            str(erro),
            404
        )

    except ValueError as erro:

        return resposta_erro(
            str(erro)
        )
