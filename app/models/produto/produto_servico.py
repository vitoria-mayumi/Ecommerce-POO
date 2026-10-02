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

    def __init__(self, *args, prazo_execucao=0, **kwargs):
        kwargs.setdefault("tipo", "servico")
        super().__init__(*args, **kwargs)
        self.definir_prazo(prazo_execucao)
        self.frete = Decimal("0.00")

    # ENCAPSULAMENTO: validação do prazo dentro da própria classe.
    def definir_prazo(self, valor):
        if valor is None or int(valor) < 0:
            raise ValueError(
                "Prazo de execução inválido para o serviço."
            )
        self.prazo_execucao = int(valor)

    # -------- POLIMORFISMO: implementação do contrato Vendavel --------
    def calcular_frete(self, quantidade: int) -> Decimal:
        return Decimal("0.00")

    def pode_ter_estoque(self) -> bool:
        return False

    def descricao_tipo(self) -> str:
        return "Serviço (prazo de execução em dias, sem frete)"

    # Acrescenta o prazo ao JSON de resposta (extensão polimórfica).
    def _dados_especificos(self) -> dict:
        return {"prazo_execucao_dias": self.prazo_execucao}
