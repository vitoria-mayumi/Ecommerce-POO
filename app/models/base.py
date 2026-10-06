from extensions import db


class EntidadeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        raise NotImplementedError(
            "Cada entidade deve implementar seu próprio to_dict()."
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
