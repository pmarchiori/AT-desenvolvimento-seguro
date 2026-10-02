# Exercício 13 — Relatório final de segurança

## 1. Resultado do OWASP ZAP

O scan passivo foi executado contra a aplicação local. O ZAP analisou dois
endpoints e encontrou dois alertas:

| Severidade  | Quantidade |
| ----------- | ---------: |
| Alta        |          0 |
| Média       |          0 |
| Baixa       |          1 |
| Informativa |          1 |

### Finding 1 — Cross-Origin-Resource-Policy ausente

- **Severidade:** baixa;
- **Endpoint:** `GET /`;
- **Categoria:** OWASP — Security Misconfiguration;
- **Situação:** não corrigido.

No Exercício 10 foram adicionados HSTS, `X-Frame-Options` e
`X-Content-Type-Options`, mas o header `Cross-Origin-Resource-Policy` não foi
implementado. A correção recomendada é adicionar:

```text
Cross-Origin-Resource-Policy: same-origin
```

### Finding 2 — Conteúdo armazenável em cache

- **Severidade:** informativa;
- **Endpoint:** `GET /`;
- **Categoria:** OWASP — Security Misconfiguration;
- **Situação:** risco aceito para esse endpoint.

A página inicial retorna apenas uma mensagem pública e não contém dados de pacientes.
Por isso, o cache dessa resposta não representa risco significativo.

## 2. Relação com as correções anteriores

| Problema                   | Categoria OWASP | Correção aplicada                    | Evidência                                             |
| -------------------------- | --------------- | ------------------------------------ | ----------------------------------------------------- |
| BOLA em consultas          | API1:2023       | verificação de ownership             | profissional não lê, altera ou exclui consulta alheia |
| Campos extras              | API3:2023       | Pydantic com `extra = "forbid"`      | requisições com campos extras recebem `422`           |
| SQL injection              | A03:2021        | regex e queries parametrizadas       | entrada semelhante a SQL injection é rejeitada        |
| Stored XSS                 | A03:2021        | validação e autoescape do Jinja2     | `<script>` é exibido como texto                       |
| JWT inválido e privilégios | API2:2023       | middleware JWT, RBAC e MFA           | tokens inválidos e acessos indevidos são bloqueados   |
| Força bruta no login       | API4:2023       | rate limiting                        | sexta tentativa inválida recebe `429`                 |
| Configuração HTTP insegura | API8:2023       | CORS e headers de segurança          | testes verificam origens e headers                    |
| Dependências vulneráveis   | A06:2021        | atualização das dependências e Trivy | pipeline bloqueou as versões antigas                  |
| Credenciais no código      | A02:2021        | `BaseSettings` e `.env`              | URL do banco não fica no código-fonte                 |
| Acesso do laboratório      | API1/API2:2023  | Client Credentials, escopo e claims  | token M2M não acessa rotas humanas                    |

Esses testes também cobrem as principais ameaças STRIDE do Exercício 4: falsificação
de identidade, alteração indevida, exposição de informações, negação de serviço e
elevação de privilégio.

## 3. Riscos residuais

Mesmo com as correções, ainda existem alguns riscos:

- o ZAP analisou somente dois endpoints e não acessou as rotas autenticadas;
- o header `Cross-Origin-Resource-Policy` ainda não foi adicionado;
- o cache das respostas com dados clínicos não foi testado;
- o MFA utiliza um código global simulado;
- não existe trilha de auditoria;
- o SQLite não possui criptografia ou estratégia de backup;

## 4. Decisão sobre o deploy

Os dois alertas encontrados pelo ZAP são de baixa severidade e, isoladamente, não
bloqueariam a aplicação. Porém, o scan não cobriu as rotas autenticadas que tratam
dados de saúde. O MFA também é apenas simulado e ainda não existe auditoria das
alterações realizadas no sistema.

Por esses motivos, a aplicação é válida em ambiente de estudos e testes, mas o deploy em produção deveria ser bloqueado até que os riscos relacionados a dados clínicos sejam avaliados e se necessário, corrigidos.
