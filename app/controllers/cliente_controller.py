from flask import Blueprint, request

from dtos.cliente_dto import ClienteDTO
from services.cliente_service import ClienteService
from utils.respostas import resposta_erro, resposta_sucesso


cliente_controller = Blueprint(
    "cliente_controller",
    __name__
)


@cliente_controller.route(
    "/clientes",
    methods=["POST"]
)
def cadastrar_cliente():

    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    try:

        dto = ClienteDTO.from_dict(dados)

        cliente = ClienteService.criar(dto)

        return resposta_sucesso(
            "Cliente cadastrado com sucesso.",
            cliente.to_dict(),
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


@cliente_controller.route(
    "/clientes",
    methods=["GET"]
)
def listar_clientes():

    clientes = ClienteService.listar()

    if not clientes:
        return resposta_sucesso(
            "Não existem clientes cadastrados.",
            []
        )

    return resposta_sucesso(
        "Clientes encontrados.",
        [
            cliente.to_dict()
            for cliente in clientes
        ]
    )
