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


"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from decimal import Decimal, InvalidOperation
from datetime import datetime
import re

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# MODELOS
# ============================================================

class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

    # Campos específicos
    estoque = db.Column(db.Integer, nullable=True)
    frete = db.Column(db.Numeric(10, 2), nullable=True)
    prazo_execucao = db.Column(db.Integer, nullable=True)

    itens_pedido = db.relationship(
        "ItemPedido",
        back_populates="produto",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "preco": float(self.preco),
            "tipo": self.tipo,
            "estoque": self.estoque,
            "frete": float(self.frete) if self.frete is not None else 0,
            "prazo_execucao_dias": self.prazo_execucao
        }


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    pedidos = db.relationship(
        "Pedido",
        back_populates="cliente",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "endereco": self.endereco,
            "email": self.email
        }


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )
    data_criacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    cliente = db.relationship(
        "Cliente",
        back_populates="pedidos"
    )

    itens = db.relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy=True
    )

    def calcular_total(self):
        return sum(
            (item.subtotal or Decimal("0.00")) +
            (item.frete_total or Decimal("0.00"))
            for item in self.itens
        )

    def to_dict(self):
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "data_criacao": self.data_criacao.isoformat(),
            "itens": [item.to_dict() for item in self.itens],
            "total": float(self.calcular_total())
        }


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.Integer, primary_key=True)

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey("pedidos.id"),
        nullable=False
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False
    )

    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    frete_total = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    pedido = db.relationship(
        "Pedido",
        back_populates="itens"
    )

    produto = db.relationship(
        "Produto",
        back_populates="itens_pedido"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "produto": self.produto.nome,
            "quantidade": self.quantidade,
            "preco_unitario": float(self.preco_unitario),
            "subtotal": float(self.subtotal),
            "frete": float(self.frete_total),
            "total_item": float(
                self.subtotal + self.frete_total
            )
        }


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def resposta_erro(mensagem, status=400):
    return jsonify({
        "sucesso": False,
        "mensagem": mensagem
    }), status


def resposta_sucesso(mensagem, dados=None, status=200):
    resposta = {
        "sucesso": True,
        "mensagem": mensagem
    }

    if dados is not None:
        resposta["dados"] = dados

    return jsonify(resposta), status


def validar_email(email):
    if not email:
        return False

    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(padrao, email) is not None


def converter_preco(valor):
    try:
        if valor is None or valor == "":
            raise ValueError

        preco = Decimal(str(valor))

        if preco < 0:
            raise ValueError

        return preco

    except (InvalidOperation, ValueError):
        return None


def converter_inteiro(valor):
    try:
        if valor is None or valor == "":
            return None

        numero = int(valor)

        return numero

    except (ValueError, TypeError):
        return None


# ============================================================
# 1. ADICIONAR PRODUTO
# ============================================================

@app.route("/produtos", methods=["POST"])
def adicionar_produto():
    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    codigo = str(dados.get("codigo", "")).strip()
    nome = str(dados.get("nome", "")).strip()
    tipo = str(dados.get("tipo", "")).strip().lower()

    if not codigo:
        return resposta_erro(
            "O código do produto é obrigatório."
        )

    if not nome:
        return resposta_erro(
            "O nome do produto é obrigatório."
        )

    if tipo not in ["fisico", "digital", "servico"]:
        return resposta_erro(
            "Tipo inválido. Utilize: fisico, digital ou servico."
        )

    preco = converter_preco(dados.get("preco"))

    if preco is None:
        return resposta_erro(
            "Preço inválido. Informe um valor numérico maior ou igual a zero."
        )

    produto_existente = Produto.query.filter_by(
        codigo=codigo
    ).first()

    if produto_existente:
        return resposta_erro(
            "Já existe um produto com esse código.",
            409
        )

    produto = Produto(
        codigo=codigo,
        nome=nome,
        preco=preco,
        tipo=tipo
    )

    # Produto físico
    if tipo == "fisico":
        estoque = converter_inteiro(
            dados.get("estoque")
        )

        if estoque is None or estoque < 0:
            return resposta_erro(
                "Estoque inválido para produto físico."
            )

        frete = converter_preco(
            dados.get("frete", 0)
        )

        if frete is None:
            return resposta_erro(
                "Valor de frete inválido."
            )

        produto.estoque = estoque
        produto.frete = frete

    # Produto digital
    elif tipo == "digital":
        produto.estoque = None
        produto.frete = Decimal("0.00")

    # Serviço
    elif tipo == "servico":
        prazo = converter_inteiro(
            dados.get("prazo_execucao")
        )

        if prazo is None or prazo < 0:
            return resposta_erro(
                "Prazo de execução inválido para o serviço."
            )

        produto.prazo_execucao = prazo
        produto.frete = Decimal("0.00")

    db.session.add(produto)
    db.session.commit()

    return resposta_sucesso(
        "Produto cadastrado com sucesso.",
        produto.to_dict(),
        201
    )


# ============================================================
# 2. LISTAR CATÁLOGO
# ============================================================

@app.route("/produtos", methods=["GET"])
def listar_produtos():
    produtos = Produto.query.order_by(
        Produto.nome
    ).all()

    if not produtos:
        return resposta_sucesso(
            "O catálogo está vazio.",
            []
        )

    return resposta_sucesso(
        "Catálogo encontrado.",
        [produto.to_dict() for produto in produtos]
    )


# ============================================================
# 3. BUSCAR PRODUTO POR NOME
# ============================================================

@app.route("/produtos/busca", methods=["GET"])
def buscar_produto():
    nome = request.args.get("nome", "").strip()

    if not nome:
        return resposta_erro(
            "Informe o nome ou parte do nome para realizar a busca."
        )

    # lower() garante busca case-insensitive
    produtos = Produto.query.filter(
        func.lower(Produto.nome).like(
            f"%{nome.lower()}%"
        )
    ).all()

    if not produtos:
        return resposta_sucesso(
            "Nenhum produto encontrado.",
            []
        )

    return resposta_sucesso(
        "Produtos encontrados.",
        [produto.to_dict() for produto in produtos]
    )


# ============================================================
# 4. CADASTRAR CLIENTE
# ============================================================

@app.route("/clientes", methods=["POST"])
def cadastrar_cliente():
    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    nome = str(dados.get("nome", "")).strip()
    endereco = str(dados.get("endereco", "")).strip()
    email = str(dados.get("email", "")).strip().lower()

    if not nome:
        return resposta_erro(
            "O nome do cliente é obrigatório."
        )

    if not endereco:
        return resposta_erro(
            "O endereço é obrigatório."
        )

    if not email:
        return resposta_erro(
            "O email é obrigatório."
        )

    if not validar_email(email):
        return resposta_erro(
            "Informe um email válido."
        )

    cliente_existente = Cliente.query.filter(
        func.lower(Cliente.email) == email
    ).first()

    if cliente_existente:
        return resposta_erro(
            "Já existe um cliente cadastrado com esse email.",
            409
        )

    cliente = Cliente(
        nome=nome,
        endereco=endereco,
        email=email
    )

    db.session.add(cliente)
    db.session.commit()

    return resposta_sucesso(
        "Cliente cadastrado com sucesso.",
        cliente.to_dict(),
        201
    )


# ============================================================
# 5. LISTAR CLIENTES
# ============================================================

@app.route("/clientes", methods=["GET"])
def listar_clientes():
    clientes = Cliente.query.order_by(
        Cliente.nome
    ).all()

    if not clientes:
        return resposta_sucesso(
            "Não existem clientes cadastrados.",
            []
        )

    return resposta_sucesso(
        "Clientes encontrados.",
        [cliente.to_dict() for cliente in clientes]
    )


# ============================================================
# 6. CRIAR PEDIDO
# ============================================================

@app.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    cliente_id = converter_inteiro(
        dados.get("cliente_id")
    )

    if cliente_id is None or cliente_id <= 0:
        return resposta_erro(
            "Índice do cliente inválido."
        )

    cliente = db.session.get(Cliente, cliente_id)

    if cliente is None:
        return resposta_erro(
            "Cliente não encontrado."
        )

    itens = dados.get("itens")

    if not isinstance(itens, list) or len(itens) == 0:
        return resposta_erro(
            "A lista de itens do pedido não pode estar vazia."
        )

    # --------------------------------------------------------
    # Primeira etapa: validar todo o pedido antes de gravar
    # --------------------------------------------------------

    itens_validados = []

    for item in itens:
        if not isinstance(item, dict):
            return resposta_erro(
                "Cada item do pedido deve ser um objeto válido."
            )

        produto_id = converter_inteiro(
            item.get("produto_id")
        )

        quantidade = converter_inteiro(
            item.get("quantidade")
        )

        if produto_id is None or produto_id <= 0:
            return resposta_erro(
                "ID de produto inválido."
            )

        if quantidade is None or quantidade <= 0:
            return resposta_erro(
                "A quantidade deve ser um número inteiro maior que zero."
            )

        produto = db.session.get(Produto, produto_id)

        if produto is None:
            return resposta_erro(
                f"Produto {produto_id} não encontrado."
            )

        # Controle de estoque
        if produto.tipo == "fisico":
            if produto.estoque < quantidade:
                return resposta_erro(
                    f"Estoque insuficiente para o produto "
                    f"'{produto.nome}'. "
                    f"Disponível: {produto.estoque}; "
                    f"solicitado: {quantidade}."
                )

        preco = Decimal(produto.preco)
        subtotal = preco * quantidade

        if produto.tipo == "fisico":
            frete_total = Decimal(
                produto.frete or 0
            )
        else:
            frete_total = Decimal("0.00")

        itens_validados.append({
            "produto": produto,
            "quantidade": quantidade,
            "preco": preco,
            "subtotal": subtotal,
            "frete": frete_total
        })

    # --------------------------------------------------------
    # Segunda etapa: criar pedido
    # --------------------------------------------------------

    pedido = Pedido(cliente=cliente)

    db.session.add(pedido)

    for item in itens_validados:
        produto = item["produto"]
        quantidade = item["quantidade"]

        novo_item = ItemPedido(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=item["preco"],
            subtotal=item["subtotal"],
            frete_total=item["frete"]
        )

        db.session.add(novo_item)

        # Baixa de estoque somente para produtos físicos
        if produto.tipo == "fisico":
            produto.estoque -= quantidade

    db.session.commit()

    return resposta_sucesso(
        "Pedido criado com sucesso.",
        pedido.to_dict(),
        201
    )


# ============================================================
# 7. LISTAR PEDIDOS DE UM CLIENTE
# ============================================================

@app.route("/clientes/<int:cliente_id>/pedidos", methods=["GET"])
def listar_pedidos_cliente(cliente_id):
    if cliente_id <= 0:
        return resposta_erro(
            "Índice de cliente inválido."
        )

    cliente = db.session.get(Cliente, cliente_id)

    if cliente is None:
        return resposta_erro(
            "Cliente não encontrado."
        )

    pedidos = Pedido.query.filter_by(
        cliente_id=cliente_id
    ).order_by(
        Pedido.data_criacao.desc()
    ).all()

    if not pedidos:
        return resposta_sucesso(
            "O cliente ainda não possui pedidos.",
            []
        )

    return resposta_sucesso(
        "Pedidos encontrados.",
        [pedido.to_dict() for pedido in pedidos]
    )


# ============================================================
# 8. ATUALIZAR ESTOQUE
# ============================================================

@app.route("/produtos/<int:produto_id>/estoque", methods=["PATCH"])
def atualizar_estoque(produto_id):
    if produto_id <= 0:
        return resposta_erro(
            "Índice de produto inválido."
        )

    dados = request.get_json(silent=True)

    if not dados:
        return resposta_erro(
            "Nenhum dado foi informado."
        )

    produto = db.session.get(Produto, produto_id)

    if produto is None:
        return resposta_erro(
            "Produto não encontrado."
        )

    if produto.tipo != "fisico":
        return resposta_erro(
            "Somente produtos físicos possuem estoque."
        )

    quantidade = converter_inteiro(
        dados.get("quantidade")
    )

    if quantidade is None:
        return resposta_erro(
            "A quantidade informada é inválida."
        )

    novo_estoque = produto.estoque + quantidade

    if novo_estoque < 0:
        return resposta_erro(
            f"Operação inválida. O estoque não pode ficar negativo. "
            f"Estoque atual: {produto.estoque}."
        )

    produto.estoque = novo_estoque

    db.session.commit()

    return resposta_sucesso(
        "Estoque atualizado com sucesso.",
        produto.to_dict()
    )


# ============================================================
# 9. RELATÓRIO
# ============================================================

@app.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    produtos = Produto.query.all()

    if not produtos:
        return resposta_sucesso(
            "Não existem produtos cadastrados.",
            {
                "produtos_mais_vendidos": [],
                "faturamento_total": 0
            }
        )

    resultado = []

    for produto in produtos:
        quantidade_vendida = db.session.query(
            func.coalesce(
                func.sum(ItemPedido.quantidade),
                0
            )
        ).filter(
            ItemPedido.produto_id == produto.id
        ).scalar()

        faturamento = db.session.query(
            func.coalesce(
                func.sum(ItemPedido.subtotal),
                0
            )
        ).filter(
            ItemPedido.produto_id == produto.id
        ).scalar()

        resultado.append({
            "produto_id": produto.id,
            "codigo": produto.codigo,
            "nome": produto.nome,
            "quantidade_vendida": int(
                quantidade_vendida or 0
            ),
            "faturamento": float(
                faturamento or 0
            )
        })

    resultado.sort(
        key=lambda item: item["quantidade_vendida"],
        reverse=True
    )

    faturamento_total = db.session.query(
        func.coalesce(
            func.sum(ItemPedido.subtotal),
            0
        )
    ).scalar()

    # Inclui frete no faturamento consolidado
    frete_total = db.session.query(
        func.coalesce(
            func.sum(ItemPedido.frete_total),
            0
        )
    ).scalar()

    faturamento_consolidado = (
        Decimal(str(faturamento_total or 0)) +
        Decimal(str(frete_total or 0))
    )

    return resposta_sucesso(
        "Relatório gerado com sucesso.",
        {
            "produtos_mais_vendidos": resultado,
            "faturamento_produtos": float(
                faturamento_total or 0
            ),
            "faturamento_frete": float(
                frete_total or 0
            ),
            "faturamento_total": float(
                faturamento_consolidado
            )
        }
    )


# ============================================================
# ROTA INICIAL / "SAIR"
# ============================================================

@app.route("/", methods=["GET"])
def inicio():
    return resposta_sucesso(
        "API de catálogo e pedidos funcionando.",
        {
            "mensagem": (
                "A API é HTTP e não necessita de uma operação "
                "'sair'. Para encerrá-la, pare o processo do servidor."
            ),
            "rotas": {
                "POST /produtos": "Adicionar produto",
                "GET /produtos": "Listar catálogo",
                "GET /produtos/busca?nome=...": "Buscar produto",
                "POST /clientes": "Cadastrar cliente",
                "GET /clientes": "Listar clientes",
                "POST /pedidos": "Criar pedido",
                "GET /clientes/<id>/pedidos": "Listar pedidos",
                "PATCH /produtos/<id>/estoque": "Atualizar estoque",
                "GET /relatorios/vendas": "Relatório de vendas"
            }
        }
    )


# ============================================================
# INICIALIZAÇÃO
# ============================================================

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
"""