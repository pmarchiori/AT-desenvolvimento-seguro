# Exercício 12 — Pipeline DevSecOps e auditoria automatizada

## Ferramentas no SDLC

| Análise            | Ferramenta  | Fase                              | Justificativa                                                                           |
| ------------------ | ----------- | --------------------------------- | --------------------------------------------------------------------------------------- |
| Estática (SAST)    | Bandit      | commit e pull request             | encontra padrões inseguros antes da integração, quando a correção é mais barata         |
| Dependências (SCA) | Trivy       | commit, pull request e build      | impede que uma versão vulnerável chegue ao artefato de deploy                           |
| Dinâmica (DAST)    | OWASP ZAP   | integração, com a API em execução | observa cabeçalhos, exposição e comportamento HTTP que a análise de código não confirma |
| Interativa (IAST)  | agente IAST | testes de integração em staging   | combina execução e contexto interno antes da promoção                                   |

## Critério do security gate

O pipeline bloqueia quando ocorrer qualquer uma destas condições:

- falha em teste automatizado de segurança ou autorização;
- achado SAST ou SCA alto/crítico;
- alerta dinâmico encontrado pelo ZAP;
- falha confirmada de autenticação ou autorização que exponha dados de saúde,
  independentemente do score numérico.s

## Priorização das vulnerabilidades

Os scores abaixo são estimativas CVSS v3.1 para os cenários analisados.

| Vulnerabilidade              | CVSS | Impacto de negócio                       |
| ---------------------------- | ---: | ---------------------------------------- |
| BOLA em consulta de terceiro |  8,1 | exposição ou alteração de dados clínicos |
| JWT forjado ou chave exposta |  9,8 | comprometimento de contas e prontuários  |
| Propriedades indevidas       |  8,1 | troca de ownership ou privilégio         |
| SQL injection                |  8,8 | leitura e alteração do banco clínico     |
| Força bruta no login         |  9,1 | tomada de contas                         |
| Stored XSS na agenda         |  6,1 | comprometimento da sessão da recepção    |

## Testes derivados do threat model

| Ameaça do Exercício 4       | Evidência pytest                                                                |
| --------------------------- | ------------------------------------------------------------------------------- |
| Spoofing por JWT adulterado | middleware rejeita token inválido com `401`                                     |
| Elevação de privilégio      | signup rejeita `role=admin` e recepcionista recebe `403` na rota administrativa |
| Bypass de MFA               | token administrativo sem MFA recebe `403`                                       |
| BOLA                        | profissional não lê, altera nem exclui consulta de outro profissional           |
| Information Disclosure      | response model não retorna `notes` nem `created_at`                             |
| Stored XSS                  | agenda codifica conteúdo persistido pelo autoescape                             |
| Abuso do login              | sexta tentativa inválida recebe `429`                                           |

## Fluxo do pipeline

Em pushes e pull requests, um único job executa pytest, Bandit, Trivy e, por último,
o ZAP contra a API em execução. Qualquer etapa com falha interrompe o job e bloqueia
o workflow, formando um security gate simples.
