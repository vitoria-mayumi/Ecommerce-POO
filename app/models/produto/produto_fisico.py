"""
SUBCLASSE CONCRETA -> Pilares: Herança + Polimorfismo + Encapsulamento.

`ProdutoFisico` HERDA de `Produto` e especializa o comportamento:
é o único tipo que controla ESTOQUE e cobra FRETE por unidade.

`polymorphic_identity = "fisico"` casa com o valor da coluna
discriminadora `tipo`, de modo que o SQLAlchemy reconstrói a instância
na subclasse correta ao ler do banco (polimorfismo do ORM).
"""

from decimal import Decimal

from extensions import db
from models.produto import Produto


class ProdutoFisico(Produto):

    # STI: nenhuma coluna nova; reutiliza a tabela `produtos`.
    __mapper_args__ = {
        "polymorphic_identity": "fisico"
    }

    def __init__(self, *args, estoque=0, frete=Decimal("0.00"), **kwargs):
        # Garante o tipo correto independentemente de quem instancia.
        kwargs.setdefault("tipo", "fisico")
        super().__init__(*args, **kwargs)
        # Usa as properties validadas (encapsulamento).
        self.definir_estoque(estoque)
        self.definir_frete(frete)

    # ENCAPSULAMENTO: regras de estoque centralizadas na própria classe.
    def definir_estoque(self, valor):
        if valor is None or int(valor) < 0:
            raise ValueError(
                "Estoque inválido para produto físico."
            )
        self.estoque = int(valor)

    def definir_frete(self, valor):
        if valor is None:
            raise ValueError("Valor de frete inválido.")
        frete = Decimal(str(valor))
        if frete < 0:
            raise ValueError("O frete não pode ser negativo.")
        self.frete = frete

    def baixar_estoque(self, quantidade: int) -> None:
        """Reduz o estoque garantindo que não fique negativo."""
        if self.estoque is None or self.estoque < quantidade:
            raise ValueError(
                f"Estoque insuficiente para o produto '{self.nome}'. "
                f"Disponível: {self.estoque or 0}; "
                f"solicitado: {quantidade}."
            )
        self.estoque -= quantidade

    def ajustar_estoque(self, variacao: int) -> None:
        """Soma (ou subtrai) uma variação, bloqueando valor negativo."""
        novo_estoque = (self.estoque or 0) + variacao
        if novo_estoque < 0:
            raise ValueError(
                "Operação inválida. O estoque não pode ficar negativo. "
                f"Estoque atual: {self.estoque}."
            )
        self.estoque = novo_estoque

    # -------- POLIMORFISMO: implementação do contrato Vendavel --------
    def calcular_frete(self, quantidade: int) -> Decimal:
        return Decimal(str(self.frete or 0)) * Decimal(quantidade)

    def pode_ter_estoque(self) -> bool:
        return True

    def descricao_tipo(self) -> str:
        return "Produto físico (com estoque e frete)"
