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
# 1. ABSTRAÇÃO
# ============================================================

class OperacaoItemPedido:

    @abstractmethod
    def executar(self):
        pass


# ============================================================
# 2. CLASSE ABSTRATA
# ============================================================

class ItemPedidoAbstrato(ABC):

    @abstractmethod
    def calcular_total(self):
        """
        Define uma operação que as classes
        filhas deverão implementar.
        """
        pass

# ============================================================
# 4. HERANÇA
# ============================================================

class ItemPedidoEspecial(ItemPedidoAbstrato):

    def __init__(
        self,
        quantidade,
        preco_unitario
    ):

        self.quantidade = quantidade
        self.preco_unitario = preco_unitario

    def calcular_total(self):
        return (
            self.quantidade *
            self.preco_unitario
        )


# ============================================================
# 5. ENCAPSULAMENTO
# ============================================================

class CalculadoraItem:

    def __init__(self, quantidade, preco):

        self.__quantidade = quantidade
        self.__preco = preco

    def obter_quantidade(self):
        return self.__quantidade

    def obter_preco(self):
        return self.__preco

    def calcular(self):

        return (
            self.__quantidade *
            self.__preco
        )


# ============================================================
# 6. ASSOCIAÇÃO
# ============================================================

class ProcessadorItemPedido:

    def __init__(self, item):

        """
        Associação:

        O ProcessadorItemPedido recebe
        um ItemPedido que já existe.
        """

        self.item = item

    def obter_produto(self):

        return self.item.produto


# ============================================================
# 7. AGREGAÇÃO
# ============================================================

class ListaItensPedido:

    def __init__(self, itens):

        """
        Agregação:

        A lista recebe itens que foram
        criados externamente.
        """

        self.itens = itens

    def quantidade(self):

        return len(self.itens)

    def calcular_total(self):

        total = 0

        for item in self.itens:

            total += (
                item.subtotal +
                item.frete_total
            )

        return total


# ============================================================
# 8. COMPOSIÇÃO
# ============================================================

class PedidoComItens:

    def __init__(self):

        """
        Composição:

        Os itens pertencem ao objeto
        e são gerenciados internamente.
        """

        self.__itens = []

    def adicionar_item(
        self,
        quantidade,
        preco_unitario
    ):

        item = ItemPedidoEspecial(
            quantidade,
            preco_unitario
        )

        self.__itens.append(item)

    def calcular_total(self):

        total = 0

        for item in self.__itens:

            total += item.calcular_total()

        return total


# ============================================================
# 9. POLIMORFISMO
# ============================================================

class ItemComFrete(ItemPedidoInterface):

    def __init__(
        self,
        quantidade,
        preco,
        frete
    ):

        self.quantidade = quantidade
        self.preco = preco
        self.frete = frete

    def calcular(self):

        return (
            self.quantidade *
            self.preco
        ) + self.frete


class ItemSemFrete(ItemPedidoInterface):

    def __init__(
        self,
        quantidade,
        preco
    ):

        self.quantidade = quantidade
        self.preco = preco

    def calcular(self):

        return (
            self.quantidade *
            self.preco
        )


def calcular_item(item):

    """
    Polimorfismo:

    A mesma função pode receber
    diferentes tipos de objetos.
    """

    return item.calcular()
