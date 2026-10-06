from extensions import db


# =====================================================================
# PILAR: ABSTRAÇÃO
# ---------------------------------------------------------------------
# EntidadeBase define o CONTRATO comum a todas as entidades de domínio
# (Cliente, e futuramente Produto, Pedido, etc.) sem se preocupar com
# os detalhes específicos de cada uma. Ela expõe apenas o que é
# essencial e compartilhado: toda entidade possui um "id" e sabe se
# converter em dicionário (to_dict).
#
# PILAR: HERANÇA
# ---------------------------------------------------------------------
# As entidades concretas HERDAM desta classe. Marcamos como
# "abstract = True" para que o SQLAlchemy NÃO crie uma tabela para a
# base — ela serve apenas para reutilização de código e padronização.
# =====================================================================
class EntidadeBase(db.Model):

    # __abstract__ diz ao SQLAlchemy que esta classe é apenas um molde
    # (abstração) e não deve virar uma tabela própria no banco.
    __abstract__ = True

    # Atributo comum a TODAS as entidades. Por estar na base, não
    # precisa ser reescrito em cada filha (reaproveitamento via herança).
    id = db.Column(db.Integer, primary_key=True)

    # PILAR: POLIMORFISMO
    # -----------------------------------------------------------------
    # to_dict() define uma assinatura única usada por todo o sistema
    # (ex.: controllers chamam entidade.to_dict() sem saber o tipo
    # concreto). Cada subclasse SOBRESCREVE este método para devolver
    # seus próprios campos. Aqui lançamos NotImplementedError para
    # garantir que toda filha forneça sua própria implementação.
    def to_dict(self):
        raise NotImplementedError(
            "Cada entidade deve implementar seu próprio to_dict()."
        )

    # Comportamento comum reutilizável: representação textual padrão.
    # Usa to_dict() de forma polimórfica — funciona para qualquer filha.
    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
