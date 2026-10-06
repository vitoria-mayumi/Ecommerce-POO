from extensions import db

# Importa a classe base para aplicar HERANÇA.
from models.base import EntidadeBase


# =====================================================================
# PILAR: HERANÇA
# ---------------------------------------------------------------------
# Antes, Cliente herdava diretamente de db.Model e declarava o campo
# "id" manualmente. Agora Cliente herda de EntidadeBase, que já fornece
# o "id" e o comportamento comum (__repr__). Reaproveitamos código e
# padronizamos todas as entidades do domínio.
# =====================================================================
class Cliente(EntidadeBase):
    __tablename__ = "clientes"

    # O campo "id" NÃO é mais declarado aqui — vem herdado de
    # EntidadeBase, demonstrando o reuso proporcionado pela herança.
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)

    pedidos = db.relationship(
        "Pedido",
        back_populates="cliente",
        lazy=True
    )

    # PILAR: POLIMORFISMO
    # -----------------------------------------------------------------
    # SOBRESCREVEMOS to_dict() definido como contrato em EntidadeBase.
    # O restante do sistema chama entidade.to_dict() de forma uniforme,
    # e cada entidade responde com seus próprios campos.
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "endereco": self.endereco,
            "email": self.email
        }
