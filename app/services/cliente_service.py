from sqlalchemy import func

from models.cliente import Cliente

from services.base_service import BaseService


class ClienteService(BaseService):
    model = Cliente

    @classmethod
    def criar(cls, cliente_dto):

        erro = cliente_dto.validar()

        if erro:
            raise ValueError(erro)

        cliente_existente = Cliente.query.filter(
            func.lower(Cliente.email) == cliente_dto.email
        ).first()

        if cliente_existente:
            raise ValueError(
                "Já existe um cliente cadastrado com esse email."
            )

        cliente = Cliente(
            nome=cliente_dto.nome,
            endereco=cliente_dto.endereco,
            email=cliente_dto.email
        )

        return cls._salvar(cliente)

    @classmethod
    def listar(cls):
        return Cliente.query.order_by(Cliente.nome).all()

