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
`tipo` é o discriminador. O esquema do banco não mudou, mas o código passa
a ser orientado a objetos de verdade.

| Pilar | Onde está aplicado | Como |
|-------|--------------------|------|
| **Interface** | `app/models/produto/vendavel.py` | `Vendavel(ABC)` define o contrato de um item vendável (`calcular_valor_total`, `calcular_frete`, `pode_ter_estoque`, `verificar_disponibilidade`, `baixar_estoque`, `descricao_tipo`) sem implementação. |
| **Abstração / Classe Abstrata** | `app/models/produto/produto.py` | `Produto` implementa parte do contrato e deixa `calcular_frete`, `pode_ter_estoque` e `descricao_tipo` abstratos. A base **não é instanciável** (`TypeError` ao tentar). |
| **Herança** | `produto_fisico.py`, `produto_digital.py`, `produto_servico.py` | `ProdutoFisico`, `ProdutoDigital` e `ProdutoServico` herdam de `Produto` e reaproveitam a fábrica, as properties e a serialização da base. |
| **Encapsulamento** | `produto.py`: properties `preco`, `estoque`, `frete`, `prazo_execucao` sobre as colunas `_preco`, `_estoque`, `_frete`, `_prazo_execucao` | Nenhum atributo muda sem validação. A base **recusa** estoque, frete e prazo por padrão; só a subclasse que possui o atributo sobrescreve o gancho `_validar_*` e o aceita. Ex.: `digital.estoque = 99` e `fisico.estoque = -50` lançam `ValueError`. |
| **Polimorfismo** | `from_dto`, `calcular_frete`, `verificar_disponibilidade`, `baixar_estoque`, `_validar_*`, `_dados_especificos`, `descricao_tipo` | Cada subclasse responde à mesma mensagem de forma diferente. Ex.: físico confere e baixa estoque; digital e serviço herdam a versão padrão, que não faz nada. |
| **Associação** | `models/produto/produto.py` ↔ `models/item_pedido.py` | `Produto` ↔ `ItemPedido` via `relationship`. |
| **Agregação / Composição** | `models/pedido.py` | `Pedido` compõe seus `ItemPedido` (`cascade="all, delete-orphan"` → o item não existe sem o pedido). |

Padrões usados:

- **Factory Method**: `Produto.criar(dto)` resolve a subclasse pelo mapa
  polimórfico do próprio SQLAlchemy (`resolver_classe`) e chama
  `Subclasse.from_dto(dto)`. Não existe dicionário `tipo → classe`
  mantido à mão.
- **Template Method**: `calcular_valor_total = calcular_subtotal + calcular_frete`.
  O algoritmo fica na base e o passo `calcular_frete` é definido por cada
  subclasse.

### Separação de responsabilidades

| Camada | Responsabilidade |
|--------|------------------|
| `controllers/produto_controller.py` | Lê a requisição HTTP, monta o DTO e traduz exceções em códigos HTTP. Não converte nem valida dados. |
| `dtos/produto_dto.py`, `dtos/estoque_dto.py` | Convertem e limpam o JSON bruto (texto → número, `strip`, `lower`). |
| `services/produto_service.py` | Orquestra: verifica a unicidade do código, delega a criação a `Produto.criar` e persiste. Não conhece os tipos concretos. |
| `models/produto/*` | Regras de negócio de cada tipo: validação, cálculo de valor/frete e estoque. |

### Onde o polimorfismo substituiu o `if tipo`

- `produto_service.py`: `Produto.criar(dto)` no lugar da cadeia
  `if classe is ProdutoFisico / elif ProdutoServico`.
- `pedido_service.py`: `produto.verificar_disponibilidade(qtd)`,
  `produto.calcular_subtotal(qtd)`, `produto.calcular_frete(qtd)` e
  `produto.baixar_estoque(qtd)` são chamados para qualquer tipo, sem
  `if produto.pode_ter_estoque()`.

**Aberto/Fechado:** para adicionar um tipo novo, basta criar uma subclasse
de `Produto` com `polymorphic_identity`, `from_dto` e os métodos abstratos,
e importá-la em `models/produto/__init__.py`. Services e controllers não mudam.

### Formato de resposta de produto

Os campos comuns (`id`, `codigo`, `nome`, `preco`, `tipo`, `tipo_descricao`)
aparecem para todo produto. Cada tipo acrescenta só os seus campos:

- físico: `estoque`, `frete`
- serviço: `prazo_execucao_dias`
- digital: nenhum campo extra

---

## Estrutura relevante

```
app/
├── models/
│   ├── produto/
│   │   ├── vendavel.py          # Interface (ABC): contrato Vendavel
│   │   ├── produto.py           # Classe ABSTRATA base + STI + fábrica + encapsulamento
│   │   ├── produto_fisico.py    # Subclasse concreta (estoque + frete)
│   │   ├── produto_digital.py   # Subclasse concreta (sem estoque/frete)
│   │   └── produto_servico.py   # Subclasse concreta (prazo de execução)
│   ├── pedido.py                # Composição com ItemPedido
│   └── item_pedido.py
├── dtos/
│   ├── produto_dto.py           # Conversão do JSON de criação
│   └── estoque_dto.py           # Conversão do JSON de ajuste de estoque
├── services/
│   ├── produto_service.py       # Orquestração, sem if tipo
│   └── pedido_service.py        # Usa o contrato Vendavel do produto
└── controllers/
    └── produto_controller.py    # Rotas HTTP (só entrada/saída)
```
