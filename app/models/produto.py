from decimal import Decimal

from extensions import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

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
