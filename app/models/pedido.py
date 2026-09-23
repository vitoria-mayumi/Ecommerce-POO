from decimal import Decimal
from datetime import datetime

from extensions import db


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
