"""
CLASSE ABSTRATA BASE -> Pilares: Abstração, Herança, Encapsulamento,
Polimorfismo e Interface.

`Produto` é a superclasse ABSTRATA de toda a hierarquia de itens do
catálogo. Ela:

- IMPLEMENTA a interface `Vendavel` (programação voltada ao contrato);
- usa SQLAlchemy "Single Table Inheritance" (STI): todas as subclasses
  compartilham a MESMA tabela `produtos`, e a coluna `tipo` funciona
  como discriminador polimórfico. Assim o banco existente é preservado;
- ENCAPSULA o preço via property/validação (o mundo externo não altera
  o estado interno sem passar pelas regras da classe);
- declara métodos ABSTRATOS que cada subtipo é obrigado a especializar
  (polimorfismo).

Produto é abstrata em dois sentidos:
  1. herda de ABC `Vendavel` e deixa métodos sem implementação;
  2. não possui `polymorphic_identity` própria -> nunca é instanciada
     diretamente, apenas suas subclasses concretas.
"""

from decimal import Decimal

from extensions import db
from models.produto.vendavel import Vendavel


# ----------------------------------------------------------------------
# Metaclasse combinada.
#
# `db.Model` já possui uma metaclasse própria (a `DeclarativeMeta` do
# SQLAlchemy) e `Vendavel` usa `ABCMeta` (por ser uma ABC). O Python não
# permite herdar de duas classes com metaclasses incompatíveis, então
# criamos uma metaclasse que herda de ambas. É o padrão canônico para
# unir "ORM declarativo" + "classe abstrata" na mesma hierarquia.
# ----------------------------------------------------------------------
class _ABCModelMeta(type(db.Model), type(Vendavel)):
    pass


class Produto(db.Model, Vendavel, metaclass=_ABCModelMeta):
    __tablename__ = "produtos"

    # ------------------------------------------------------------------
    # Mapeamento de colunas (estado compartilhado por toda a hierarquia).
    # Atributos com prefixo "_" sinalizam encapsulamento: devem ser
    # acessados pelas properties, não diretamente.
    # ------------------------------------------------------------------
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)

    # Coluna física mapeada com nome interno "_preco" para forçar o uso
    # da property `preco` (encapsulamento com validação).
    _preco = db.Column("preco", db.Numeric(10, 2), nullable=False)

    # Discriminador polimórfico do Single Table Inheritance.
    tipo = db.Column(db.String(20), nullable=False)

    # Colunas específicas de subtipos (nullable, pois nem todo subtipo
    # as utiliza). Cada subclasse dá sentido às que lhe interessam.
    estoque = db.Column(db.Integer, nullable=True)
    frete = db.Column(db.Numeric(10, 2), nullable=True)
    prazo_execucao = db.Column(db.Integer, nullable=True)

    # ASSOCIAÇÃO: um produto pode estar referenciado em vários itens de
    # pedido. (A composição real é Pedido -> ItemPedido.)
    itens_pedido = db.relationship(
        "ItemPedido",
        back_populates="produto",
        lazy=True
    )

    # Configuração do STI: usa `tipo` como discriminador. A base não tem
    # identidade concreta -> comporta-se como abstrata para o ORM.
    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "produto"
    }

    # ------------------------------------------------------------------
    # ENCAPSULAMENTO: acesso controlado ao preço.
    # ------------------------------------------------------------------
    @property
    def preco(self) -> Decimal:
        """Lê o preço sempre como Decimal."""
        return Decimal(str(self._preco)) if self._preco is not None else None

    @preco.setter
    def preco(self, valor):
        """Valida a regra de negócio antes de alterar o estado interno."""
        if valor is None:
            raise ValueError(
                "Preço inválido. Informe um valor numérico "
                "maior ou igual a zero."
            )

        preco = Decimal(str(valor))

        if preco < 0:
            raise ValueError(
                "O preço não pode ser negativo."
            )

        self._preco = preco

    # ------------------------------------------------------------------
    # MÉTODOS ABSTRATOS (contrato Vendavel) -> polimorfismo nas subclasses.
    # ------------------------------------------------------------------
    def calcular_valor_total(self, quantidade: int) -> Decimal:
        """Valor dos produtos + frete do tipo. Template method simples."""
        subtotal = self.preco * Decimal(quantidade)
        return subtotal + self.calcular_frete(quantidade)

    # calcular_frete, pode_ter_estoque e descricao_tipo permanecem
    # abstratos (herdados de Vendavel) e DEVEM ser implementados por
    # cada subclasse concreta.

    # ------------------------------------------------------------------
    # Serialização base. As subclasses ESTENDEM via `_dados_especificos`
    # (polimorfismo por extensão, mantendo o formato de resposta HTTP).
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        dados = {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "preco": float(self.preco),
            "tipo": self.tipo,
            "tipo_descricao": self.descricao_tipo(),
            "estoque": self.estoque,
            "frete": float(self.frete) if self.frete is not None else 0,
            "prazo_execucao_dias": self.prazo_execucao
        }
        dados.update(self._dados_especificos())
        return dados

    def _dados_especificos(self) -> dict:
        """Gancho de extensão. Subclasses sobrescrevem se necessário."""
        return {}
