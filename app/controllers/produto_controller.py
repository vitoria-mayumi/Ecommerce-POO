"""
CONTROLLER (Controlador) do módulo de produtos.

Esta é a "porta de entrada" do sistema para o mundo externo. Quando
alguém faz uma requisição HTTP (ex.: pelo navegador, por um app ou por
uma ferramenta como o Postman), é aqui que o pedido chega primeiro.

A responsabilidade do controller é apenas INTERMEDIAR:
  1. receber a requisição e ler os dados enviados;
  2. repassar o trabalho pesado para o ProdutoService (a regra de negócio);
  3. devolver uma resposta HTTP adequada (sucesso ou erro).

Repare que NÃO existe nenhuma lógica de "se o produto é físico/digital"
aqui. Isso é proposital: toda a complexidade dos tipos de produto está
encapsulada nas classes de modelo e no service. O controller conversa
apenas com a abstração (ProdutoService), sem conhecer os tipos concretos.
Isso mantém cada camada com uma responsabilidade só (separação de
responsabilidades).
"""

from flask import Blueprint, request

from dtos.produto_dto import ProdutoDTO
from services.produto_service import ProdutoService
from utils.respostas import resposta_erro, resposta_sucesso


# Blueprint = agrupador de rotas. Reúne todas as rotas de "produto"
# em um só lugar, que depois é registrado na aplicação principal.
produto_controller = Blueprint(
    "produto_controller",
    __name__
)


# ----------------------------------------------------------------------
# ROTA 1 — ADICIONAR PRODUTO
# Responde a requisições POST em /produtos (POST = criar algo novo).
# ----------------------------------------------------------------------
@produto_controller.route(
    "/produtos",
    methods=["POST"]
)
def adicionar_produto():

    # Lê o corpo da requisição como JSON. silent=True evita quebrar
    # se o conteúdo não for um JSON válido (retorna None nesse caso).
    dados = request.get_json(silent=True)

    # Se não veio nada, avisa o cliente com uma mensagem de erro.
    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    try:
        # 1) Organiza os dados brutos no "formulário padronizado" (DTO).
        dto = ProdutoDTO.from_dict(dados)

        # 2) Entrega ao service, que cria o tipo certo de produto
        #    (físico, digital ou serviço) e valida tudo.
        produto = ProdutoService.criar(dto)

        # 3) Deu certo: devolve o produto criado com o código HTTP 201
        #    (201 = "Created", padrão para "recurso criado com sucesso").
        return resposta_sucesso(
            "Produto cadastrado com sucesso.",
            produto.to_dict(),
            201
        )

    # Se o service recusar os dados, ele lança um ValueError com a
    # mensagem explicando o motivo. Aqui transformamos isso em resposta.
    except ValueError as erro:

        # Caso especial: código já existente é um "conflito" (HTTP 409).
        # Os demais erros de validação são "requisição inválida" (400).
        status = (
            409
            if "Já existe" in str(erro)
            else 400
        )

        return resposta_erro(
            str(erro),
            status
        )


# ----------------------------------------------------------------------
# ROTA 2 — LISTAR CATÁLOGO
# Responde a requisições GET em /produtos (GET = buscar/consultar).
# ----------------------------------------------------------------------
@produto_controller.route(
    "/produtos",
    methods=["GET"]
)
def listar_produtos():

    # Pede ao service a lista completa de produtos.
    produtos = ProdutoService.listar()

    # Catálogo vazio: ainda é sucesso, só devolvemos uma lista vazia.
    if not produtos:
        return resposta_sucesso(
            "O catálogo está vazio.",
            []
        )

    # Converte cada produto para dicionário (to_dict) e devolve a lista.
    # POLIMORFISMO: cada tipo de produto gera seu próprio to_dict, mas o
    # controller trata todos da mesma forma, sem saber o tipo de cada um.
    return resposta_sucesso(
        "Catálogo encontrado.",
        [
            produto.to_dict()
            for produto in produtos
        ]
    )


# ----------------------------------------------------------------------
# ROTA 3 — BUSCAR PRODUTO POR NOME
# GET em /produtos/busca?nome=... (o "?nome=" é o parâmetro de busca).
# ----------------------------------------------------------------------
@produto_controller.route(
    "/produtos/busca",
    methods=["GET"]
)
def buscar_produto():

    # Lê o parâmetro "nome" da URL. Se não vier, usa "" e remove espaços.
    nome = request.args.get(
        "nome",
        ""
    ).strip()

    # Sem termo de busca não há o que procurar: avisa o cliente.
    if not nome:
        return resposta_erro(
            "Informe o nome ou parte do nome "
            "para realizar a busca."
        )

    # Pede ao service os produtos cujo nome contém o termo informado.
    produtos = ProdutoService.buscar_por_nome(nome)

    # Nenhum resultado: ainda é sucesso, apenas lista vazia.
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


# ----------------------------------------------------------------------
# ROTA 4 — ATUALIZAR ESTOQUE
# PATCH em /produtos/<id>/estoque (PATCH = atualizar parte de um recurso).
# O <int:produto_id> captura o número do produto direto da URL.
# ----------------------------------------------------------------------
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

    # Importa aqui dentro apenas o utilitário necessário para converter
    # a quantidade enviada em um número inteiro de forma segura.
    from utils.validacoes import converter_inteiro

    quantidade = converter_inteiro(
        dados.get("quantidade")
    )

    try:

        # O service verifica se o produto existe, se ele pode ter estoque
        # (apenas produtos físicos podem) e aplica a variação com segurança.
        produto = ProdutoService.atualizar_estoque(
            produto_id,
            quantidade
        )

        return resposta_sucesso(
            "Estoque atualizado com sucesso.",
            produto.to_dict()
        )

    # LookupError = produto não encontrado -> HTTP 404 ("Not Found").
    except LookupError as erro:

        return resposta_erro(
            str(erro),
            404
        )

    # ValueError = dados/operação inválidos -> HTTP 400 (padrão).
    except ValueError as erro:

        return resposta_erro(
            str(erro)
        )
