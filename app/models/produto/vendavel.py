from abc import ABC, abstractmethod
from decimal import Decimal


class Vendavel(ABC):

    @abstractmethod
    def calcular_valor_total(self, quantidade: int) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def calcular_frete(self, quantidade: int) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def pode_ter_estoque(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def verificar_disponibilidade(self, quantidade: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def baixar_estoque(self, quantidade: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def descricao_tipo(self) -> str:
        raise NotImplementedError
