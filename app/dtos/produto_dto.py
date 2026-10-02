"""
DTO = Data Transfer Object (Objeto de Transferência de Dados).

Pense neste arquivo como um "formulário padronizado". Quando alguém
envia os dados de um produto para o sistema (em formato JSON, que é
texto solto vindo de fora), não dá para confiar que esses dados vêm
limpos: podem ter espaços sobrando, letras maiúsculas, números escritos
como texto, campos faltando, etc.

O `ProdutoDTO` é o objeto que recebe esses dados brutos, organiza em
campos com nomes claros e já aplica uma primeira limpeza/conversão.
Assim, o resto do sistema (service, models) recebe dados previsíveis,
em vez de um amontoado de texto cru.

É também um exemplo de ENCAPSULAMENTO: a regra de "como transformar o
JSON externo em dados utilizáveis" fica concentrada aqui, num lugar só.
"""

from dataclasses import dataclass
from typing import Any, Optional

# Funções utilitárias que convertem texto em número com segurança
# (se o valor for inválido, elas devolvem None em vez de quebrar).
from utils.validacoes import converter_inteiro, converter_preco


# @dataclass é um atalho do Python que gera automaticamente o
# "construtor" da classe a partir dos campos listados abaixo.
# Em vez de escrever um __init__ manualmente, só declaramos os campos.
@dataclass
class ProdutoDTO:
    # Campos obrigatórios (todo produto precisa deles):
    codigo: str          # identificador único do produto
    nome: str            # nome exibido no catálogo
    tipo: str            # "fisico", "digital" ou "servico"
    preco: Any           # Any pois chega como texto e vira número depois

    # Campos opcionais (só alguns tipos usam).
    # O "= None" / "= 0" define o valor padrão quando o campo não vem.
    estoque: Optional[int] = None      # usado só por produto físico
    frete: Any = 0                     # usado só por produto físico
    prazo_execucao: Optional[int] = None  # usado só por serviço

    # @classmethod: método "de fábrica". Em vez de criar o DTO campo a
    # campo, chamamos ProdutoDTO.from_dict(json) e ele monta tudo.
    @classmethod
    def from_dict(cls, dados):
        # `dados` é o dicionário vindo do JSON enviado pelo cliente.
        # Para cada campo, pegamos o valor e já fazemos a limpeza:
        return cls(
            # .get("codigo", "") = pega "codigo" ou "" se não existir.
            # .strip() remove espaços no começo e no fim.
            codigo=str(dados.get("codigo", "")).strip(),
            nome=str(dados.get("nome", "")).strip(),
            # .lower() padroniza o tipo em minúsculas ("Fisico" -> "fisico").
            tipo=str(dados.get("tipo", "")).strip().lower(),
            # converte o preço para número; se for inválido, vira None.
            preco=converter_preco(dados.get("preco")),
            # converte o estoque para inteiro; se não vier, vira None.
            estoque=converter_inteiro(dados.get("estoque")),
            # frete padrão é 0 quando não informado.
            frete=converter_preco(dados.get("frete", 0)),
            prazo_execucao=converter_inteiro(
                dados.get("prazo_execucao")
            )
        )
