# API de Agendamento Clínico

Projeto baseado no starter kit `clinica-api-assessment` fornecido para o Assessment.

## Ambiente

O starter kit requer Python 3.10 ou 3.11.

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crie o arquivo local de configuração a partir do modelo:

```bash
cp .env.example .env
```

Edite `.env` e substitua todos os placeholders por valores próprios. O arquivo
`.env` contém segredos e está ignorado pelo Git.

Para a integração M2M do laboratório, configure também `LAB_CLIENT_ID` e
`LAB_CLIENT_SECRET`.

## Executar os testes

```bash
python -m pytest -v
```

## Executar a API

```bash
python main.py
```

Swagger UI: `http://127.0.0.1:8000/docs`

## Documentação de segurança

- [Exercício 3 — análise CIA e DFD](docs/ex3_analise_cia_dfd.md)
- [Exercício 4 — threat model STRIDE](docs/ex4_threat_model_stride.md)
- [Exercício 5 — arquitetura de segurança](docs/ex5_arquitetura_seguranca.md)
- [Exercício 8 — vulnerabilidades OWASP](docs/ex8_vulnerabilidades_owasp.md)
