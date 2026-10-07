from extensions import db
from models.cliente import Cliente
from models.pedido import Pedido
from models.item_pedido import ItemPedido
from models.produto import Produto
from services.cliente_service import ClienteService

#Concentra as regras de negócio e esconde detalhes do Controller(Abstração)
class PedidoService:

    @staticmethod
    def criar(pedido_dto):
        # Os objetos se relacionam para formar o pedido(Composição)
        if (
            pedido_dto.cliente_id is None or
            pedido_dto.cliente_id <= 0
        ):
            raise ValueError(
                "Índice do cliente inválido."
            )

        cliente = db.session.get(
            Cliente,
            pedido_dto.cliente_id
        )

        if cliente is None:
            raise LookupError(
                "Cliente não encontrado."
            )

        if not pedido_dto.itens:
            raise ValueError(
                "A lista de itens do pedido não pode estar vazia."
            )

        itens_validados = []

        for item in pedido_dto.itens:

            if (
                item.produto_id is None or
                item.produto_id <= 0
            ):
                raise ValueError(
                    "ID de produto inválido."
                )

            if (
                item.quantidade is None or
                item.quantidade <= 0
            ):
                raise ValueError(
                    "A quantidade deve ser um número inteiro "
                    "maior que zero."
                )
           # Os objetos possuem seus próprios dados e comportamentos(Encapsulamento)
            produto = db.session.get(
                Produto,
                item.produto_id
            )

            if produto is None:
                raise LookupError(
                    f"Produto {item.produto_id} não encontrado."
                )

            produto.verificar_disponibilidade(item.quantidade)

            itens_validados.append({
                "produto": produto,
                "quantidade": item.quantidade,
                "preco": produto.preco,
                "subtotal": produto.calcular_subtotal(item.quantidade),
                "frete": produto.calcular_frete(item.quantidade)
            })

        # Segunda etapa:
        # persistir o pedido.
        # Os objetos possuem seus próprios dados e comportamentos(Encapsulamento)
        pedido = Pedido(
            cliente=cliente
        )

        db.session.add(pedido)

        for item in itens_validados:

            produto = item["produto"]

            novo_item = ItemPedido(
                pedido=pedido,
                produto=produto,
                quantidade=item["quantidade"],
                preco_unitario=item["preco"],
                subtotal=item["subtotal"],
                frete_total=item["frete"]
            )

            db.session.add(novo_item)

            produto.baixar_estoque(item["quantidade"])

        db.session.commit()

        return pedido

    @staticmethod
    def listar_por_cliente(cliente_id):

        cliente = ClienteService.buscar_por_id(cliente_id)

        pedidos = Pedido.query.filter_by(
            cliente_id=cliente.id
        ).order_by(
            Pedido.data_criacao.desc()
        ).all()

        return pedidos