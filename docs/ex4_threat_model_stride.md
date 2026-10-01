# Exercício 4 — Modelagem de ameaças com STRIDE

## 1. Misuse cases

### MC 1 — Acesso como outro usuário

Um atacante rouba ou falsifica um token JWT e acessa dados de pacientes e
consultas como se fosse um usuário legítimo.

- **Ativos afetados:** contas, tokens e dados clínicos.
- **Controle atual:** JWT assinado e com expiração.
- **Mitigação:** armazenar a chave JWT fora do código, exigir HTTPS e implementar
  rotação de chaves.

### MC 2 — Escalação de privilégio

Um usuário informa `role="admin"` durante o cadastro e obtém permissões
administrativas.

- **Ativos afetados:** usuários, pacientes e consultas.
- **Controle atual:** RBAC nas rotas protegidas.
- **Mitigação:** remover `role` do cadastro público e permitir que somente um
  administrador altere papéis.

### MC 3 — Alteração indevida de consulta

Um usuário altera o horário, o profissional ou o status de uma consulta sem ter
permissão ou sem respeitar as regras de agendamento.

- **Ativos afetados:** agenda e dados das consultas.
- **Controle atual:** RBAC e validação de tipos com Pydantic.
- **Mitigação:** validar conflitos de horário, registrar quem realizou cada alteração.

## 2. STRIDE por componente

### Autenticação e autorização

| STRIDE                 | Ameaça                                 | Mitigação                         |
| ---------------------- | -------------------------------------- | --------------------------------- |
| Spoofing               | uso de token roubado ou forjado        | rotação de chave                  |
| Information Disclosure | vazamento de senha ou token            | hash de senha                     |
| Elevation of Privilege | usuário se cadastra como administrador | impedir escolha pública de `role` |

### Rotas de pacientes e consultas

| STRIDE                 | Ameaça                                       | Mitigação                                  |
| ---------------------- | -------------------------------------------- | ------------------------------------------ |
| Tampering              | alteração indevida de uma consulta           | RBAC                                       |
| Information Disclosure | exposição de CPF, `notes` ou campos internos | response models e autorização por registro |

### Banco de dados

| STRIDE                 | Ameaça                                   | Mitigação                        |
| ---------------------- | ---------------------------------------- | -------------------------------- |
| Tampering              | alteração direta do arquivo `clinica.db` | restringir permissões do arquivo |
| Information Disclosure | cópia ou leitura do banco                | controle de acesso               |
| Denial of Service      | exclusão, corrupção ou bloqueio do banco | backup e restauração             |

## 3. Threat model

| Ativo              | Superfície de ataque              | Ameaça                                  | Controle atual                  | Mitigação necessária                 |
| ------------------ | --------------------------------- | --------------------------------------- | ------------------------------- | ------------------------------------ |
| contas e tokens    | `/user/signin`                    | falsificação de identidade              | JWT, expiração e senha com hash | chave externa e rotação              |
| papéis de usuário  | `/user/signup`                    | escalação de privilégio                 | RBAC                            | cadastro público sem campo `role`    |
| dados de pacientes | rotas `/patient` e `/appointment` | acesso ou alteração indevida            | autenticação, RBAC e Pydantic   | autorização por registro e auditoria |
| sessão da recepção | `/appointment/agenda`             | XSS persistente                         | autoescape do Jinja2            | manter escape                        |
| banco clínico      | arquivo `clinica.db`              | leitura, alteração ou indisponibilidade | acesso por SQLModel             | permissões, criptografia e backup    |
