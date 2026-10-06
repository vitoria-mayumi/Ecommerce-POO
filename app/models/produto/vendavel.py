"""
INTERFACE (CONTRATO) -> Pilar de POO: Abstração / Interface

Em Python não existe a palavra-chave `interface` como em Java/C#.
O equivalente idiomático é uma classe abstrata (ABC) que define
APENAS o contrato (métodos abstratos, sem implementação).

`Vendavel` descreve "o que todo item vendável sabe fazer" sem dizer
"como" ele faz. Qualquer classe que queira ser tratada como um item
de venda no sistema é OBRIGADA a implementar estes métodos.

Isso permite PROGRAMAR VOLTADO À INTERFACE: os serviços dependem do
contrato `Vendavel`, e não de uma implementação concreta específica.
"""

from abc import ABC, abstractmethod
from decimal import Decimal


class Vendavel(ABC):
    """Contrato que todo item comercializável deve cumprir."""

    @abstractmethod
    def calcular_valor_total(self, quantidade: int) -> Decimal:
        """
        Calcula o valor total da venda de `quantidade` unidades,
        já considerando regras específicas do tipo (ex.: frete).
        Cada implementação decide COMO calcular -> polimorfismo.
        """
        raise NotImplementedError

    @abstractmethod
    def calcular_frete(self, quantidade: int) -> Decimal:
        """Retorna o frete aplicável para a quantidade informada."""
        raise NotImplementedError

    @abstractmethod
    def pode_ter_estoque(self) -> bool:
        """Indica se o item controla estoque físico."""
        raise NotImplementedError

    @abstractmethod
    def verificar_disponibilidade(self, quantidade: int) -> None:
        """Lança ValueError se `quantidade` unidades não puderem ser
        vendidas. Itens sem estoque estão sempre disponíveis."""
        raise NotImplementedError

    @abstractmethod
    def baixar_estoque(self, quantidade: int) -> None:
        """Registra a saída de `quantidade` unidades vendidas.
        Itens sem estoque não fazem nada."""
        raise NotImplementedError

    @abstractmethod
    def descricao_tipo(self) -> str:
        """Descrição legível do tipo do item (para relatórios/UI)."""
        raise NotImplementedError
