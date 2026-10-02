"""
CAMADA DE SERVIÇO do catálogo.

Com a hierarquia polimórfica de `Produto`, o serviço deixa de usar
cadeias de `if tipo == ...` para decidir comportamento. Ele apenas:

  1. escolhe a CLASSE concreta correta (uma única fábrica);
  2. deixa cada subclasse validar e calcular o que lhe compete
     (encapsulamento + polimorfismo).

Isso aplica o princípio Aberto/Fechado: para suportar um novo tipo
de produto, cria-se uma nova subclasse — o serviço quase não muda.
"""

from sqlalchemy import func

from extensions import db
from models.produto import Produto
from models.produto.produto_fisico import ProdutoFisico
from models.produto.produto_digital import ProdutoDigital
from models.produto.produto_servico import ProdutoServico


class ProdutoService:

    # Mapa tipo -> classe concreta. Substitui o encadeamento de ifs.
    _TIPOS = {
        "fisico": ProdutoFisico,
        "digital": ProdutoDigital,
        "servico": ProdutoServico
    }

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

        classe = ProdutoService._TIPOS.get(produto_dto.tipo)

        if classe is None:
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

        # Monta os argumentos específicos de cada subtipo. Cada classe
        # ignora o que não lhe diz respeito e valida o resto no __init__.
        extras = {}

        if classe is ProdutoFisico:
            extras["estoque"] = produto_dto.estoque
            extras["frete"] = produto_dto.frete
        elif classe is ProdutoServico:
            extras["prazo_execucao"] = produto_dto.prazo_execucao

        # POLIMORFISMO: a mesma linha instancia o subtipo correto; a
        # validação específica acontece dentro da subclasse escolhida.
        produto = classe(
            codigo=produto_dto.codigo,
            nome=produto_dto.nome,
            **extras
        )

        # ENCAPSULAMENTO: preço passa pela property validada.
        produto.preco = produto_dto.preco

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

        # POLIMORFISMO: pergunta ao próprio objeto se ele controla
        # estoque, em vez de inspecionar o campo `tipo`.
        if not produto.pode_ter_estoque():
            raise ValueError(
                "Somente produtos físicos possuem estoque."
            )

        if quantidade is None:
            raise ValueError(
                "A quantidade informada é inválida."
            )

        # A regra de "não ficar negativo" vive dentro da subclasse.
        produto.ajustar_estoque(quantidade)

        db.session.commit()

        return produto
