from abc import ABC, abstractmethod


class BaseDTO(ABC):

    @classmethod
    @abstractmethod
    def from_dict(cls, dados):
        raise NotImplementedError

    @abstractmethod
    def validar(self):
        raise NotImplementedError
