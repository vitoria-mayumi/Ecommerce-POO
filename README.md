# Ecommerce-POO

Projeto de POO para uma API de E-Commerce (Flask + SQLAlchemy).

As três operações de produto exigidas na atividade são:

- **Adicionar produto** (físico, digital ou serviço) — `POST /produtos`
- **Listar catálogo** — `GET /produtos`
- **Buscar produto por nome** — `GET /produtos/busca?nome=...`

---

## Como configurar o ambiente

### Windows

```
py -m venv venv
.\venv\Scripts\python.exe -m pip install Flask Flask-SQLAlchemy
.\venv\Scripts\python.exe app/app.py
```

### macOS / Linux

```
python3 -m venv venv
venv/bin/python -m pip install Flask Flask-SQLAlchemy
venv/bin/python app/app.py
```

A API sobe em `http://localhost:8000`. A rota `GET /` lista todas as rotas.

---

## Aplicação dos Pilares de Orientação a Objetos (módulo Produto)

Toda a hierarquia de `Produto` foi modelada com **Single Table Inheritance**
do SQLAlchemy: as subclasses compartilham a tabela `produtos` e a coluna
`tipo` é o discriminador. Assim o banco (`instance/database.db`) continua
igual, mas o código passa a ser orientado a objetos de verdade.

| Pilar | Onde está aplicado | Como |
|-------|--------------------|------|
| **Interface** | `app/models/vendavel.py` | `Vendavel(ABC)` define o contrato de um item vendável (`calcular_valor_total`, `calcular_frete`, `pode_ter_estoque`, `descricao_tipo`) sem implementação. |
| **Abstração / Classe Abstrata** | `app/models/produto.py` | `Produto` implementa parte do contrato e deixa métodos abstratos. A base **não é instanciável** (`TypeError` ao tentar). |
| **Herança** | `produto_fisico.py`, `produto_digital.py`, `produto_servico.py` | `ProdutoFisico`, `ProdutoDigital`, `ProdutoServico` herdam de `Produto`. |
| **Encapsulamento** | `produto.py` (property `preco` sobre a coluna `_preco`); `ProdutoFisico.definir_estoque/definir_frete`; `ProdutoServico.definir_prazo` | O estado interno só muda passando por validação. |
| **Polimorfismo** | `calcular_frete`, `pode_ter_estoque`, `descricao_tipo`, `_dados_especificos` | Cada subclasse responde ao mesmo método de forma diferente. Físico cobra frete e tem estoque; digital e serviço não. |
| **Associação** | `models/produto.py` ↔ `models/item_pedido.py` | `Produto` ↔ `ItemPedido` via `relationship`. |
| **Agregação / Composição** | `models/pedido.py` | `Pedido` compõe seus `ItemPedido` (`cascade="all, delete-orphan"` → o item não existe sem o pedido). |

### Onde o polimorfismo substituiu o `if tipo`

Antes, a lógica dependia de `if produto.tipo == "fisico"` espalhado pelos
serviços. Depois da refatoração:

- `app/services/produto_service.py` → fábrica `_TIPOS` (tipo → classe) e
  chamadas a `produto.pode_ter_estoque()` / `produto.ajustar_estoque()`.
- `app/services/pedido_service.py` → `produto.pode_ter_estoque()`,
  `produto.calcular_frete(qtd)`, `produto.baixar_estoque(qtd)`.

Para adicionar um novo tipo de produto, basta criar uma nova subclasse de
`Produto` e registrá-la em `_TIPOS` — os serviços praticamente não mudam
(princípio Aberto/Fechado).

---

## Estrutura relevante

```
app/
├── models/
│   ├── vendavel.py          # Interface (ABC) — contrato Vendavel
│   ├── produto.py           # Classe ABSTRATA base + STI + encapsulamento
│   ├── produto_fisico.py    # Subclasse concreta (estoque + frete)
│   ├── produto_digital.py   # Subclasse concreta (sem estoque/frete)
│   ├── produto_servico.py   # Subclasse concreta (prazo de execução)
│   └── ...
├── services/
│   ├── produto_service.py   # Fábrica polimórfica, sem if tipo
│   └── pedido_service.py    # Usa métodos polimórficos do produto
└── controllers/
    └── produto_controller.py  # Rotas HTTP (inalteradas)
```
