# Ecommerce-POO

Projeto de POO para uma API de E-Commerce (Flask + SQLAlchemy).

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
