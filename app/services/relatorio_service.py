from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models.produto import Produto
from models.item_pedido import ItemPedido


class RelatorioService:

    def __init__(self):
        self.produtos = Produto.query.all()

    def vendas(self):

        if not self.produtos:
            return {
                "produtos_mais_vendidos": [],
                "faturamento_total": 0
            }

        produtos_mais_vendidos = self._montar_produtos_vendidos()
        faturamento = self._calcular_faturamento()

        return {
            "produtos_mais_vendidos": produtos_mais_vendidos,
            "faturamento_produtos": faturamento["produtos"],
            "faturamento_frete": faturamento["frete"],
            "faturamento_total": faturamento["total"]
        }

    def _montar_produtos_vendidos(self):

        resultado = []

        for produto in self.produtos:

            quantidade_vendida = db.session.query(
                func.coalesce(
                    func.sum(ItemPedido.quantidade),
                    0
                )
            ).filter(
                ItemPedido.produto_id == produto.id
            ).scalar()

            faturamento = db.session.query(
                func.coalesce(
                    func.sum(ItemPedido.subtotal),
                    0
                )
            ).filter(
                ItemPedido.produto_id == produto.id
            ).scalar()

            resultado.append({
                "produto_id": produto.id,
                "codigo": produto.codigo,
                "nome": produto.nome,
                "quantidade_vendida": int(
                    quantidade_vendida or 0
                ),
                "faturamento": float(
                    faturamento or 0
                )
            })

        resultado.sort(
            key=lambda item: item["quantidade_vendida"],
            reverse=True
        )

        return resultado

    def _calcular_faturamento(self):

        faturamento_produtos = db.session.query(
            func.coalesce(
                func.sum(ItemPedido.subtotal),
                0
            )
        ).scalar()

        faturamento_frete = db.session.query(
            func.coalesce(
                func.sum(ItemPedido.frete_total),
                0
            )
        ).scalar()

        faturamento_consolidado = (
            Decimal(str(faturamento_produtos or 0)) +
            Decimal(str(faturamento_frete or 0))
        )

        return {
            "produtos": float(faturamento_produtos or 0),
            "frete": float(faturamento_frete or 0),
            "total": float(faturamento_consolidado)
        }
