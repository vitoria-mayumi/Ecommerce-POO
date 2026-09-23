from dataclasses import dataclass

from utils.validacoes import validar_email


@dataclass
class ClienteDTO:
    nome: str
    endereco: str
    email: str

    @classmethod
    def from_dict(cls, dados):
        email = str(
            dados.get("email", "")
        ).strip().lower()

        return cls(
            nome=str(dados.get("nome", "")).strip(),
            endereco=str(dados.get("endereco", "")).strip(),
            email=email
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
