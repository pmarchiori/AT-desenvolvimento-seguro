## Preparação do ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execução da API

```bash
uvicorn main:app --reload --port 8080
```

A documentação interativa estará em `http://127.0.0.1:8080/docs`.

## Testes

```bash
pytest
```
