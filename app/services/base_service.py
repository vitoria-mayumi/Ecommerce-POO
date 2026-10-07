from abc import ABC, abstractmethod

from extensions import db


class BaseService(ABC):
    @property
    @abstractmethod
    def model(self):
        raise NotImplementedError

    @classmethod
    def _salvar(cls, entidade):
        db.session.add(entidade)
        db.session.commit()
        return entidade

    @classmethod
    def buscar_por_id(cls, entidade_id):

        if entidade_id <= 0:
            raise ValueError("Índice inválido.")

        entidade = db.session.get(cls.model, entidade_id)

        if entidade is None:
            raise LookupError(
                f"{cls.model.__name__} não encontrado(a)."
            )

        return entidade

    @classmethod
    def listar(cls):
        return cls.model.query.all()
