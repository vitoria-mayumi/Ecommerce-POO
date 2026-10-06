"""
SUBCLASSE CONCRETA -> Pilares: Herança + Polimorfismo + Encapsulamento.

`ProdutoFisico` HERDA de `Produto` e especializa o comportamento:
é o único tipo que controla ESTOQUE e cobra FRETE por unidade.

`polymorphic_identity = "fisico"` casa com o valor da coluna
discriminadora `tipo`, de modo que o SQLAlchemy reconstrói a instância
na subclasse correta ao ler do banco (polimorfismo do ORM).
"""

from decimal import Decimal, InvalidOperation

from models.produto import Produto


class ProdutoFisico(Produto):

    __mapper_args__ = {
        "polymorphic_identity": "fisico"
    }

    def __init__(self, *, estoque=0, frete=Decimal("0.00"), **kwargs):
        super().__init__(**kwargs)
        self.estoque = estoque
        self.frete = frete

    @classmethod
    def from_dto(cls, dto) -> "ProdutoFisico":
        return cls._montar_base(dto, estoque=dto.estoque, frete=dto.frete)

    def _validar_estoque(self, valor):
        try:
            estoque = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Estoque inválido para produto físico.")

        if estoque < 0:
            raise ValueError("O estoque não pode ser negativo.")

        return estoque

    def _validar_frete(self, valor):
        try:
            frete = Decimal(str(valor)) if valor is not None else None
        except InvalidOperation:
            frete = None

        if frete is None:
            raise ValueError("Valor de frete inválido.")

        if frete < 0:
            raise ValueError("O frete não pode ser negativo.")

        return frete

    def verificar_disponibilidade(self, quantidade: int) -> None:
        if (self.estoque or 0) < quantidade:
            raise ValueError(
                f"Estoque insuficiente para o produto '{self.nome}'. "
                f"Disponível: {self.estoque or 0}; "
                f"solicitado: {quantidade}."
            )

    def baixar_estoque(self, quantidade: int) -> None:
        self.verificar_disponibilidade(quantidade)
        self.estoque = self.estoque - quantidade

    def ajustar_estoque(self, variacao: int) -> None:
        """Soma (ou subtrai) uma variação, bloqueando valor negativo."""
        novo_estoque = (self.estoque or 0) + variacao
        if novo_estoque < 0:
            raise ValueError(
                "Operação inválida. O estoque não pode ficar negativo. "
                f"Estoque atual: {self.estoque}."
            )
        self.estoque = novo_estoque

    def calcular_frete(self, quantidade: int) -> Decimal:
        return self.frete * Decimal(quantidade)

    def pode_ter_estoque(self) -> bool:
        return True

    def descricao_tipo(self) -> str:
        return "Produto físico (com estoque e frete)"

    def _dados_especificos(self) -> dict:
        return {
            "estoque": self.estoque,
            "frete": float(self.frete)
        }
