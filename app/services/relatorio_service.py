from decimal import Decimal

from sqlalchemy import func

from extensions import db
from models.produto import Produto
from models.item_pedido import ItemPedido


class RelatorioService:

    @staticmethod
    def vendas():

        produtos = Produto.query.all()

        if not produtos:
            return {
                "produtos_mais_vendidos": [],
                "faturamento_total": 0
            }

        resultado = []

        for produto in produtos:

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
            "produtos_mais_vendidos": resultado,
            "faturamento_produtos": float(
                faturamento_produtos or 0
            ),
            "faturamento_frete": float(
                faturamento_frete or 0
            ),
            "faturamento_total": float(
                faturamento_consolidado
            )
        }
