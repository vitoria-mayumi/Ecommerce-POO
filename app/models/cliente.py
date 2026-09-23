from extensions import db


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
