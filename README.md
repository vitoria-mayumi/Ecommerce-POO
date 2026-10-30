# Ecommerce-POO

Projeto de POO para uma API de E-Commerce (Flask + SQLAlchemy).

## Como configurar o ambiente

### Windows
```
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r app/requirements.txt
.\venv\Scripts\python.exe app/app.py
```

### macOS / Linux
```
python3 -m venv venv
venv/bin/python -m pip install -r app/requirements.txt
venv/bin/python app/app.py
```

A API sobe em `http://localhost:8000`. A rota `GET /` lista todas as rotas.

## Interface web

Com o servidor rodando, abra no navegador:

```
http://localhost:8000/static/index.html
```

A interface consome a API e cobre produtos (com os três tipos), clientes,
pedidos e o relatório de vendas. São apenas arquivos estáticos em
`app/static/`, servidos pelo próprio Flask: não precisa de build, de
instalar nada a mais nem de subir um segundo servidor.

O banco começa vazio. Cadastre primeiro alguns produtos e clientes, porque
a tela de pedidos monta as listas de seleção a partir deles.

## Problemas comuns

**`No module named 'flask'`** — as dependências não foram instaladas, ou o
servidor está sendo executado com o Python do sistema em vez do que está no
`venv`. Use o caminho completo (`venv/bin/python app/app.py`).

**`ensurepip is not available` ao criar o venv** — no Ubuntu/Debian falta o
pacote de venv: `sudo apt install python3-venv`. Sem acesso a sudo, uma
alternativa é o [uv](https://docs.astral.sh/uv/):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv
uv pip install -r app/requirements.txt --python venv/bin/python
venv/bin/python app/app.py
```

**Quero começar com o banco limpo** — pare o servidor e apague
`instance/database.db`. Ele é recriado vazio no próximo start.
