from sqlalchemy import func

from extensions import db
from models.cliente import Cliente


class ClienteService:

    @staticmethod
    def criar(cliente_dto):

        erro = cliente_dto.validar()

        if erro:
            raise ValueError(erro)

        cliente_existente = Cliente.query.filter(
            func.lower(Cliente.email) ==
            cliente_dto.email
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

        db.session.add(cliente)
        db.session.commit()

        return cliente

    @staticmethod
    def listar():

        return Cliente.query.order_by(
            Cliente.nome
        ).all()

    @staticmethod
    def buscar_por_id(cliente_id):

        if cliente_id <= 0:
            raise ValueError(
                "Índice de cliente inválido."
            )

        cliente = db.session.get(
            Cliente,
            cliente_id
        )

        if cliente is None:
            raise LookupError(
                "Cliente não encontrado."
            )

        return cliente
