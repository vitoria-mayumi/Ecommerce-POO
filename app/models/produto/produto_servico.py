"""
SUBCLASSE CONCRETA -> Pilares: Herança + Polimorfismo + Encapsulamento.

`ProdutoServico` representa serviços prestados (ex.: instalação,
consultoria). Não tem estoque nem frete, mas possui um PRAZO DE
EXECUÇÃO em dias, que não existe nos demais tipos.
"""

from decimal import Decimal

from models.produto import Produto


class ProdutoServico(Produto):

    __mapper_args__ = {
        "polymorphic_identity": "servico"
    }

    def __init__(self, *, prazo_execucao=0, **kwargs):
        super().__init__(**kwargs)
        self.prazo_execucao = prazo_execucao

    @classmethod
    def from_dto(cls, dto) -> "ProdutoServico":
        return cls._montar_base(dto, prazo_execucao=dto.prazo_execucao)

    def _validar_prazo(self, valor):
        try:
            prazo = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Prazo de execução inválido para o serviço.")

        if prazo < 0:
            raise ValueError("O prazo de execução não pode ser negativo.")

        return prazo

    def calcular_frete(self, quantidade: int) -> Decimal:
        return Decimal("0.00")

    def pode_ter_estoque(self) -> bool:
        return False

    def descricao_tipo(self) -> str:
        return "Serviço (prazo de execução em dias, sem frete)"

    def _dados_especificos(self) -> dict:
        return {"prazo_execucao_dias": self.prazo_execucao}
