from flask import Blueprint, request

from dtos.pedido_dto import PedidoDTO
from services.pedido_service import PedidoService
from utils.respostas import resposta_erro, resposta_sucesso


pedido_controller = Blueprint(
    "pedido_controller",
    __name__
)


@pedido_controller.route(
    "/pedidos",
    methods=["POST"]
)
def criar_pedido():

    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    try:

        dto = PedidoDTO.from_dict(dados)

        pedido = PedidoService.criar(dto)

        return resposta_sucesso(
            "Pedido criado com sucesso.",
            pedido.to_dict(),
            201
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


@pedido_controller.route(
    "/clientes/<int:cliente_id>/pedidos",
    methods=["GET"]
)
def listar_pedidos_cliente(cliente_id):

    try:

        pedidos = PedidoService.listar_por_cliente(
            cliente_id
        )

        if not pedidos:
            return resposta_sucesso(
                "O cliente ainda não possui pedidos.",
                []
            )

        return resposta_sucesso(
            "Pedidos encontrados.",
            [
                pedido.to_dict()
                for pedido in pedidos
            ]
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
