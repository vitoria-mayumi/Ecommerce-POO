from abc import ABC, abstractmethod


# =====================================================================
# PILAR: ABSTRAÇÃO
# ---------------------------------------------------------------------
# BaseDTO abstrai a ideia de "objeto de transporte de dados que sabe
# se validar e se construir a partir de um dicionário". Os detalhes de
# QUAIS campos existem e COMO validá-los ficam nas subclasses.
#
# PILAR: POLIMORFISMO
# ---------------------------------------------------------------------
# Os métodos from_dict() e validar() têm assinatura fixa aqui, mas cada
# DTO concreto fornece sua própria versão. Assim o service pode chamar
# dto.validar() sem saber se é um ClienteDTO, ProdutoDTO, etc.
# =====================================================================
class BaseDTO(ABC):

    @classmethod
    @abstractmethod
    def from_dict(cls, dados):
        # Constrói o DTO a partir de dados crus (ex.: JSON da request).
        raise NotImplementedError

    @abstractmethod
    def validar(self):
        # Retorna uma mensagem de erro (str) ou None se estiver válido.
        raise NotImplementedError
