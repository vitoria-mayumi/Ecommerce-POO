from extensions import db


class EntidadeBase(db.Model):
    # Classe-base abstrata: fornece herança para as entidades sem
    # gerar uma tabela própria no banco. Sem isto, o SQLAlchemy
    # mapearia "EntidadeBase" para a tabela "entidade_base" e as
    # chaves estrangeiras (ex.: pedidos.cliente_id -> clientes.id)
    # deixariam de ser resolvidas.
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        raise NotImplementedError(
            "Cada entidade deve implementar seu próprio to_dict()."
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
