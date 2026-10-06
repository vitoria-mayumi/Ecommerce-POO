"""
CLASSE ABSTRATA BASE -> Pilares: Abstração, Herança, Encapsulamento,
Polimorfismo e Interface.

`Produto` é a superclasse ABSTRATA de toda a hierarquia de itens do
catálogo. Ela:

- IMPLEMENTA a interface `Vendavel` (programação voltada ao contrato);
- usa SQLAlchemy "Single Table Inheritance" (STI): todas as subclasses
  compartilham a MESMA tabela `produtos`, e a coluna `tipo` funciona
  como discriminador polimórfico. Assim o banco existente é preservado;
- ENCAPSULA todo o estado (preço, estoque, frete, prazo) atrás de
  properties: nenhuma coluna é alterada sem passar por validação;
- fornece uma FÁBRICA polimórfica (`criar`) que escolhe a subclasse
  concreta sem nenhum `if tipo == ...`.

Produto é abstrata porque deixa métodos do contrato `Vendavel` sem
implementação (`calcular_frete`, `pode_ter_estoque`, `descricao_tipo`).
Tentar `Produto(...)` lança TypeError. A `polymorphic_identity`
"produto" existe apenas porque o SQLAlchemy exige uma identidade no
mapper base; `resolver_classe` impede que ela seja usada para criação.
"""

from decimal import Decimal

from extensions import db
from models.produto.vendavel import Vendavel

class _ABCModelMeta(type(db.Model), type(Vendavel)):
    pass


class Produto(db.Model, Vendavel, metaclass=_ABCModelMeta):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    _preco = db.Column("preco", db.Numeric(10, 2), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    _estoque = db.Column("estoque", db.Integer, nullable=True)
    _frete = db.Column("frete", db.Numeric(10, 2), nullable=True)
    _prazo_execucao = db.Column("prazo_execucao", db.Integer, nullable=True)

    itens_pedido = db.relationship(
        "ItemPedido",
        back_populates="produto",
        lazy=True
    )

    __mapper_args__ = {
        "polymorphic_on": tipo,
        "polymorphic_identity": "produto"
    }

    @classmethod
    def resolver_classe(cls, tipo: str) -> type:
        """Mapeia o discriminador `tipo` para a subclasse concreta."""
        mapper = cls.__mapper__.polymorphic_map.get(tipo) if tipo else None

        if mapper is None or mapper.class_ is Produto:
            raise ValueError(
                "Tipo inválido. Utilize: fisico, digital ou servico."
            )

        return mapper.class_

    @classmethod
    def criar(cls, dto) -> "Produto":
        """Ponto único de criação. Valida o que é comum a todo produto
        e delega a construção específica à subclasse (polimorfismo)."""
        if not dto.codigo:
            raise ValueError("O código do produto é obrigatório.")

        if not dto.nome:
            raise ValueError("O nome do produto é obrigatório.")

        classe = cls.resolver_classe(dto.tipo)

        return classe.from_dto(dto)

    @classmethod
    def _montar_base(cls, dto, **especificos) -> "Produto":
        """Helper usado pelas subclasses em `from_dto`: monta a parte
        COMUM (código, nome, preço) e repassa os campos específicos ao
        construtor da subclasse."""
        produto = cls(codigo=dto.codigo, nome=dto.nome, **especificos)
        produto.preco = dto.preco
        return produto

    @property
    def preco(self) -> Decimal:
        return Decimal(str(self._preco)) if self._preco is not None else None

    @preco.setter
    def preco(self, valor):
        if valor is None:
            raise ValueError(
                "Preço inválido. Informe um valor numérico "
                "maior ou igual a zero."
            )

        preco = Decimal(str(valor))

        if preco < 0:
            raise ValueError("O preço não pode ser negativo.")

        self._preco = preco

    @property
    def estoque(self):
        return self._estoque

    @estoque.setter
    def estoque(self, valor):
        self._estoque = self._validar_estoque(valor)

    def _validar_estoque(self, valor):
        raise ValueError("Somente produtos físicos possuem estoque.")

    @property
    def frete(self) -> Decimal:
        return (
            Decimal(str(self._frete))
            if self._frete is not None
            else Decimal("0.00")
        )

    @frete.setter
    def frete(self, valor):
        self._frete = self._validar_frete(valor)

    def _validar_frete(self, valor):
        raise ValueError("Somente produtos físicos possuem frete.")

    @property
    def prazo_execucao(self):
        return self._prazo_execucao

    @prazo_execucao.setter
    def prazo_execucao(self, valor):
        self._prazo_execucao = self._validar_prazo(valor)

    def _validar_prazo(self, valor):
        raise ValueError("Somente serviços possuem prazo de execução.")

    def calcular_subtotal(self, quantidade: int) -> Decimal:
        """Valor das unidades, sem frete."""
        return self.preco * Decimal(quantidade)

    def calcular_valor_total(self, quantidade: int) -> Decimal:
        """TEMPLATE METHOD: o algoritmo é fixo (subtotal + frete), mas o
        passo `calcular_frete` é definido por cada subclasse."""
        return self.calcular_subtotal(quantidade) + self.calcular_frete(quantidade)

    def verificar_disponibilidade(self, quantidade: int) -> None:
        return None

    def baixar_estoque(self, quantidade: int) -> None:
        return None

    def to_dict(self) -> dict:
        dados = {
            "id": self.id,
            "codigo": self.codigo,
            "nome": self.nome,
            "preco": float(self.preco),
            "tipo": self.tipo,
            "tipo_descricao": self.descricao_tipo()
        }
        dados.update(self._dados_especificos())
        return dados

    def _dados_especificos(self) -> dict:
        """Gancho de extensão. Subclasses sobrescrevem se necessário."""
        return {}
