from utils.validacoes import validar_email

from dtos.base_dto import BaseDTO


class ClienteDTO(BaseDTO):

    def __init__(self, nome, endereco, email):
        self.nome = nome
        self.endereco = endereco
        self.email = email

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = str(valor or "").strip()

    @property
    def endereco(self):
        return self._endereco

    @endereco.setter
    def endereco(self, valor):
        self._endereco = str(valor or "").strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        self._email = str(valor or "").strip().lower()

    @classmethod
    def from_dict(cls, dados):
        return cls(
            nome=dados.get("nome", ""),
            endereco=dados.get("endereco", ""),
            email=dados.get("email", "")
        )

    def validar(self):
        if not self.nome:
            return "O nome do cliente é obrigatório."

        if not self.endereco:
            return "O endereço é obrigatório."

        if not self.email:
            return "O email é obrigatório."

        if not validar_email(self.email):
            return "Informe um email válido."

        return None
