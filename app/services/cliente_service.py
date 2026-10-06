from sqlalchemy import func

from models.cliente import Cliente

# Importa a base para aplicar HERANÇA de comportamento comum.
from services.base_service import BaseService


# =====================================================================
# PILAR: HERANÇA
# ---------------------------------------------------------------------
# ClienteService herda de BaseService e ganha, sem reescrever,
# os métodos listar() e buscar_por_id(), além do helper _salvar().
# Antes esses métodos eram implementados "na mão" aqui dentro.
# =====================================================================
class ClienteService(BaseService):

    # PILAR: ABSTRAÇÃO / POLIMORFISMO
    # -----------------------------------------------------------------
    # Satisfazemos o contrato abstrato "model" exigido por BaseService.
    # É este valor que torna os métodos genéricos da base (buscar_por_id,
    # listar) polimórficos: eles passam a operar sobre Cliente.
    model = Cliente

    @classmethod
    def criar(cls, cliente_dto):

        # PILAR: ENCAPSULAMENTO (reaproveitado do DTO)
        # -------------------------------------------------------------
        # O service não conhece as regras internas de validação do DTO;
        # apenas pede "valide-se". A lógica fica encapsulada no DTO.
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

        # Reaproveita o _salvar() HERDADO de BaseService (add + commit),
        # evitando duplicar a lógica de persistência.
        return cls._salvar(cliente)

    # PILAR: POLIMORFISMO (especialização por sobrescrita)
    # -----------------------------------------------------------------
    # A base oferece um listar() genérico (sem ordenação). Aqui
    # SOBRESCREVEMOS para ordenar por nome — comportamento específico
    # de Cliente — mantendo a mesma assinatura usada pelo controller.
    @classmethod
    def listar(cls):
        return Cliente.query.order_by(Cliente.nome).all()

    # buscar_por_id() NÃO é reescrito: usamos a versão HERDADA de
    # BaseService, que já funciona para Cliente graças ao atributo
    # "model" definido acima (polimorfismo em ação).
