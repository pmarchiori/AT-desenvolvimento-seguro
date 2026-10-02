# Exercício 8 — Identificação de vulnerabilidades OWASP

## 1. Broken Object Level Authorization (BOLA)

No starter kit, a rota de listagem de consultas permitia que qualquer profissional
autenticado recebesse todas as consultas. Não existia filtro pelo identificador do
profissional proprietário. Assim, um profissional podia acessar objetos pertencentes
a outros profissionais e pacientes.

Essa vulnerabilidade **já está mitigada na versão atual**. As operações de consulta,
alteração e exclusão verificam `appointment.professional_id`, e a listagem aplica um
filtro para o profissional autenticado.

## 2. Injection por validação de entrada insuficiente

Os modelos de pacientes e consultas aceitam diversos textos sem whitelist, limite
de tamanho ou validação por expressão regular. Por exemplo, `status`, `notes`,
`name`, `cpf` e `phone` aceitam qualquer string. Isso permite persistir conteúdo
inesperado, inclusive payloads de XSS, e transfere toda a responsabilidade de
segurança para o ponto em que o valor for utilizado ou exibido.

O SQLModel gera consultas parametrizadas e reduz atualmente o risco de SQL
injection, enquanto a agenda HTML utiliza o autoescape do Jinja2. Ainda assim, o
padrão de entrada é vulnerável porque não define formatos e valores permitidos. Um
novo endpoint, filtro ou template que reutilize esses dados em outro contexto pode
transformar o conteúdo persistido em uma injeção explorável.

## 3. Broken Object Property Level Authorization

A rota `POST /patient/new` usa diretamente o modelo de banco `Patient` como modelo
de entrada. Com isso, o cliente pode enviar propriedades como `id` e
`professional_id`, embora esses campos devam ser controlados pela aplicação. Um
usuário autorizado a cadastrar pacientes pode escolher livremente o vínculo do
paciente com um profissional.

Além disso, os modelos Pydantic atuais não usam `extra = "forbid"`. Em modelos como
`AppointmentCreate`, propriedades não declaradas podem ser enviadas e descartadas
silenciosamente, em vez de a requisição ser rejeitada. A mitigação seria de
separar os modelos de persistência, entrada e resposta, declarar somente as
propriedades autorizadas e rejeitar campos extras.
