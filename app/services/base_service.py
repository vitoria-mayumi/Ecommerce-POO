from abc import ABC, abstractmethod

from extensions import db


# =====================================================================
# PILAR: ABSTRAÇÃO
# ---------------------------------------------------------------------
# BaseService é uma classe ABSTRATA (herda de ABC) que descreve o que
# um "serviço de entidade" deve saber fazer, escondendo os detalhes de
# acesso ao banco. Quem usa o serviço só precisa conhecer os métodos
# públicos (criar, listar, buscar_por_id) — não como eles funcionam
# por dentro.
#
# PILAR: HERANÇA
# ---------------------------------------------------------------------
# Serviços concretos (ex.: ClienteService) HERDAM esta base e ganham
# de graça a lógica repetitiva de persistência e busca por id,
# evitando duplicação de código entre os vários serviços.
# =====================================================================
class BaseService(ABC):

    # PILAR: ABSTRAÇÃO (método abstrato)
    # -----------------------------------------------------------------
    # Cada serviço concreto é OBRIGADO a dizer qual entidade (model)
    # ele gerencia. O @abstractmethod impede que a base seja usada
    # diretamente e força as filhas a definirem este detalhe.
    @property
    @abstractmethod
    def model(self):
        raise NotImplementedError

    # Comportamento comum reutilizável por herança: salvar no banco.
    # Centraliza o padrão add + commit num único lugar.
    @classmethod
    def _salvar(cls, entidade):
        db.session.add(entidade)
        db.session.commit()
        return entidade

    # PILAR: POLIMORFISMO
    # -----------------------------------------------------------------
    # buscar_por_id usa cls.model, que é resolvido em tempo de execução
    # conforme a subclasse concreta. O MESMO código serve para qualquer
    # entidade: ClienteService.buscar_por_id busca Cliente, outro
    # serviço buscaria sua própria model, sem reescrever este método.
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

    # Listagem genérica, reutilizável por qualquer serviço filho.
    @classmethod
    def listar(cls):
        return cls.model.query.all()
