from flask import Blueprint, request

from dtos.cliente_dto import ClienteDTO
from services.cliente_service import ClienteService
from utils.respostas import resposta_erro, resposta_sucesso


# =====================================================================
# PILAR: ABSTRAÇÃO (separação em camadas)
# ---------------------------------------------------------------------
# O controller cuida APENAS do HTTP (entrada/saída). Ele não conhece
# regras de negócio nem acesso ao banco — delega isso ao DTO (validação
# de dados) e ao Service (regras + persistência). Cada camada expõe uma
# interface simples e esconde seus detalhes internos.
#
# PILAR: ENCAPSULAMENTO (entre camadas)
# ---------------------------------------------------------------------
# As responsabilidades ficam encapsuladas: o controller não acessa a
# model diretamente nem monta queries; usa somente os métodos públicos
# de ClienteDTO e ClienteService.
# =====================================================================
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

        # ABSTRAÇÃO: o controller só pede "crie um DTO a partir destes
        # dados" e "crie um cliente com este DTO". Como a validação,
        # normalização e persistência acontecem está escondido nas
        # camadas DTO/Service.
        dto = ClienteDTO.from_dict(dados)

        cliente = ClienteService.criar(dto)

        # POLIMORFISMO: cliente.to_dict() segue o contrato de
        # EntidadeBase; o controller o chama sem conhecer o tipo
        # concreto por trás.
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

    # POLIMORFISMO: cada item responde ao mesmo to_dict() de forma
    # uniforme, independente de detalhes internos da entidade.
    return resposta_sucesso(
        "Clientes encontrados.",
        [
            cliente.to_dict()
            for cliente in clientes
        ]
    )
