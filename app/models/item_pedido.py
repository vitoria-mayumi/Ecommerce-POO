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
