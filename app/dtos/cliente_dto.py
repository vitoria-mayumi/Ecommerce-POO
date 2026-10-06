from utils.validacoes import validar_email

# Importa a base para aplicar HERANÇA e padronizar o contrato de DTOs.
from dtos.base_dto import BaseDTO


# =====================================================================
# PILAR: HERANÇA
# ---------------------------------------------------------------------
# ClienteDTO herda de BaseDTO, assumindo o contrato (from_dict/validar).
#
# OBSERVAÇÃO SOBRE A MUDANÇA:
# Antes era um @dataclass com atributos públicos "soltos". Trocamos por
# uma classe comum para podermos aplicar ENCAPSULAMENTO de verdade,
# controlando como cada campo é atribuído e lido.
# =====================================================================
class ClienteDTO(BaseDTO):

    def __init__(self, nome, endereco, email):
        # PILAR: ENCAPSULAMENTO
        # -------------------------------------------------------------
        # Usamos os SETTERS (via property abaixo) em vez de atribuir
        # direto aos atributos. Assim toda escrita passa por um ponto
        # único que normaliza/limpa o dado (strip, lower), protegendo
        # o estado interno do objeto.
        self.nome = nome
        self.endereco = endereco
        self.email = email

    # -----------------------------------------------------------------
    # PILAR: ENCAPSULAMENTO (atributo "nome")
    # Os dados reais ficam em atributos "privados" (prefixo _) e o
    # acesso externo é feito por property/setter. O setter garante que
    # o nome seja sempre armazenado sem espaços nas pontas.
    # -----------------------------------------------------------------
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        self._nome = str(valor or "").strip()

    # ENCAPSULAMENTO (atributo "endereco")
    @property
    def endereco(self):
        return self._endereco

    @endereco.setter
    def endereco(self, valor):
        self._endereco = str(valor or "").strip()

    # ENCAPSULAMENTO (atributo "email")
    # O setter centraliza a regra de normalização do email
    # (sem espaços e em minúsculas), impedindo estados inconsistentes.
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        self._email = str(valor or "").strip().lower()

    # PILAR: POLIMORFISMO (sobrescreve from_dict de BaseDTO)
    # -----------------------------------------------------------------
    # Fábrica que cria o DTO a partir do dicionário recebido na request.
    # A normalização agora acontece nos setters, mantendo este método
    # simples e sem repetir regras de limpeza.
    @classmethod
    def from_dict(cls, dados):
        return cls(
            nome=dados.get("nome", ""),
            endereco=dados.get("endereco", ""),
            email=dados.get("email", "")
        )

    # PILAR: POLIMORFISMO (sobrescreve validar de BaseDTO)
    # -----------------------------------------------------------------
    # Regras de validação específicas de Cliente. Retorna a mensagem de
    # erro ou None. O service chama este método de forma polimórfica.
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
