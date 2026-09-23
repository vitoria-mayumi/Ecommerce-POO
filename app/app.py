from flask import Flask

from extensions import db

from models import (
    Produto,
    Cliente,
    Pedido,
    ItemPedido
)

from controllers import (
    produto_controller,
    cliente_controller,
    pedido_controller,
    relatorio_controller
)

from utils.respostas import resposta_sucesso


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///database.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(produto_controller)
    app.register_blueprint(cliente_controller)
    app.register_blueprint(pedido_controller)
    app.register_blueprint(relatorio_controller)

    @app.route("/", methods=["GET"])
    def inicio():

        return resposta_sucesso(
            "API de catálogo e pedidos funcionando.",
            {
                "mensagem": (
                    "A API é HTTP e não necessita de uma "
                    "operação 'sair'. Para encerrá-la, "
                    "pare o processo do servidor."
                ),
                "rotas": {
                    "POST /produtos":
                        "Adicionar produto",

                    "GET /produtos":
                        "Listar catálogo",

                    "GET /produtos/busca?nome=...":
                        "Buscar produto",

                    "POST /clientes":
                        "Cadastrar cliente",

                    "GET /clientes":
                        "Listar clientes",

                    "POST /pedidos":
                        "Criar pedido",

                    "GET /clientes/<id>/pedidos":
                        "Listar pedidos",

                    "PATCH /produtos/<id>/estoque":
                        "Atualizar estoque",

                    "GET /relatorios/vendas":
                        "Relatório de vendas"
                }
            }
        )

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )