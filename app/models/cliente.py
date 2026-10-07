from extensions import db

from models.base import EntidadeBase


class Cliente(EntidadeBase):
    __tablename__ = "clientes"

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
