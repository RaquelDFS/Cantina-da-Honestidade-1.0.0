# Cantina-da-Honestidade-1.0.0
Sistema de gestão para a Cantina da Honestidade do SENAI Fraiburgo, com controle de usuários, créditos, compras e movimentações financeiras. Curso Superior de Tecnologia em ADS | Turma GR ADSI 2025/2 1 | UC: Projeto Aplicado II (AEx) - 474830

A Cantina da Honestidade do SENAI/SC – Fraiburgo opera por confiança: produtos ficam disponíveis e o pagamento é feito voluntariamente em dinheiro, sem nenhum registro tecnológico das operações.

# Problema:
Não há controle de quais produtos foram retirados, quem comprou, quanto foi pago ou qual o total arrecadado. Isso permite retiradas sem pagamento (gerando perdas) e impede consulta de histórico de compras ou saldo por usuário. O pagamento só em dinheiro também dificulta casos sem valor exato.

# Impacto:
A instituição sofre perdas financeiras e falta de controle sobre os resultados; os usuários não têm como acompanhar gastos ou saldo. O mercado já oferece soluções similares (carteira digital, QR Code, relatórios), mostrando que há demanda por esse tipo de sistema em cantinas escolares.

# Justificativa:
O problema é real e mensurável na instituição, e a tecnologia permite preservar o conceito de honestidade enquanto adiciona controle — carteira virtual e registro automático de compras, com o objetivo de reduzir perdas, aumentar transparência e tornar o processo mais prático para usuários e administradores.

# Instalação e execução:
1. Antes de começar, faça a instalação de: 
    - Python
    - MySQL Server
    - Git

2. Clone o repositório e entre na pasta do projeto:

    - git clone https://github.com/RaquelDFS/Cantina-da-Honestidade-1.0.0.git
    - cd Cantina-da-Honestidade-1.0.0

3. Criar o ambiente virtual e ativar:

Crie um ambiente virtual para instalar as dependências do projeto separadamente de outros projetos Python:

- py -m venv venv

No Windows, usando o Prompt de Comando (CMD):

- venv\Scripts\activate

4. Instalar as dependências

Com o ambiente virtual ativado, execute:

- pip install -r requirements.txt

5. Configurar a variável MYSQL_PASSWORD:
No CMD, execute:

- set MYSQL_PASSWORD=sua_senha_do_mysql

Substitua sua_senha_do_mysql pela senha do seu MySQL.
Importante: esse comando mantém a variável configurada apenas na sessão atual do terminal. Se abrir outro terminal, será necessário configurá-la novamente.

6. Executar o projeto:

- python -m streamlit run app.py

7. Encerrar a execução:
Para interromper o sistema, volte ao terminal e pressione:

- Ctrl + C

8. Desativar o ambiente virtual:
Execute

- deactivate
