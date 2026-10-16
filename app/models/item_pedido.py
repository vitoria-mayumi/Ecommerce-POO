from abc import abstractmethod, ABC

from extensions import db


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
# DEMONSTRAÇÃO DIDÁTICA DOS PILARES DA ORIENTAÇÃO A OBJETOS
# ------------------------------------------------------------
# As classes abaixo não participam do mapeamento do SQLAlchemy.
# Elas existem apenas para ilustrar, de forma isolada e
# executável, cada um dos pilares de POO.
# ============================================================


# ============================================================
# 1. ABSTRAÇÃO + 2. CLASSE ABSTRATA
# ------------------------------------------------------------
# Uma classe abstrata (ABC) define um contrato: todo item
# calculável precisa saber calcular seu total, mas o "como"
# é escondido de quem usa (abstração).
# ============================================================

class ItemCalculavel(ABC):

    @abstractmethod
    def calcular_total(self) -> float:
        """Contrato que as subclasses são obrigadas a implementar."""
        raise NotImplementedError


# ============================================================
# 3. HERANÇA + 4. ENCAPSULAMENTO
# ------------------------------------------------------------
# ItemPedidoEspecial HERDA de ItemCalculavel e ENCAPSULA seus
# dados em atributos privados (prefixo "__"), expostos apenas
# por métodos de acesso controlados.
# ============================================================

class ItemPedidoEspecial(ItemCalculavel):

    def __init__(self, quantidade: int, preco_unitario: float):
        self.__quantidade = quantidade
        self.__preco_unitario = preco_unitario

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @property
    def preco_unitario(self) -> float:
        return self.__preco_unitario

    def calcular_total(self) -> float:
        return self.__quantidade * self.__preco_unitario


# ============================================================
# 5. POLIMORFISMO
# ------------------------------------------------------------
# Duas subclasses implementam calcular_total() de formas
# diferentes. A função calcular_item() trata ambas de maneira
# uniforme, sem conhecer o tipo concreto.
# ============================================================

class ItemComFrete(ItemCalculavel):

    def __init__(self, quantidade: int, preco: float, frete: float):
        self.quantidade = quantidade
        self.preco = preco
        self.frete = frete

    def calcular_total(self) -> float:
        return (self.quantidade * self.preco) + self.frete


class ItemSemFrete(ItemCalculavel):

    def __init__(self, quantidade: int, preco: float):
        self.quantidade = quantidade
        self.preco = preco

    def calcular_total(self) -> float:
        return self.quantidade * self.preco


def calcular_item(item: ItemCalculavel) -> float:
    """Polimorfismo: aceita qualquer objeto que seja ItemCalculavel."""
    return item.calcular_total()


# ============================================================
# 6. ASSOCIAÇÃO
# ------------------------------------------------------------
# O processador USA um item que foi criado em outro lugar.
# O item tem vida própria e independe do processador.
# ============================================================

class ProcessadorItemPedido:

    def __init__(self, item):
        self.item = item

    def obter_produto(self):
        return self.item.produto


# ============================================================
# 7. AGREGAÇÃO
# ------------------------------------------------------------
# A lista agrega itens criados externamente. Se a lista for
# destruída, os itens continuam existindo (relação "tem-um"
# fraca).
# ============================================================

class ListaItensPedido:

    def __init__(self, itens):
        self.itens = itens

    def quantidade(self) -> int:
        return len(self.itens)

    def calcular_total(self) -> float:
        return sum(
            (item.subtotal + item.frete_total)
            for item in self.itens
        )


# ============================================================
# 8. COMPOSIÇÃO
# ------------------------------------------------------------
# Os itens são criados e gerenciados internamente pelo objeto.
# Se o PedidoComItens for destruído, seus itens também somem
# (relação "é-parte-de" forte).
# ============================================================

class PedidoComItens:

    def __init__(self):
        self.__itens = []

    def adicionar_item(self, quantidade: int, preco_unitario: float):
        self.__itens.append(
            ItemPedidoEspecial(quantidade, preco_unitario)
        )

    def calcular_total(self) -> float:
        return sum(item.calcular_total() for item in self.__itens)
