from flask import Blueprint

from services.relatorio_service import RelatorioService
from utils.respostas import resposta_sucesso


relatorio_controller = Blueprint(
    "relatorio_controller",
    __name__
)


@relatorio_controller.route(
    "/relatorios/vendas",
    methods=["GET"]
)
def relatorio_vendas():

    dados = RelatorioService.vendas()

    if not dados.get("produtos_mais_vendidos"):
        return resposta_sucesso(
            "Não existem produtos cadastrados.",
            dados
        )

    return resposta_sucesso(
        "Relatório gerado com sucesso.",
        dados
    )
