# Cantina da Honestidade 1.0.0

Sistema de gestão para a Cantina da Honestidade do SENAI Florianópolis, com controle de usuários, créditos, compras e movimentações financeiras.

**Curso:** Superior de Tecnologia em Análise e Desenvolvimento de Sistemas (ADS)

**Turma:** GR ADSI 2025/2 1

**Unidade Curricular:** Projeto Aplicado II (AEx) - 474830

**Instituição:** SENAI/SC - Florianópolis

## 1. Contextualização

A Cantina da Honestidade da Unidade SENAI Fraiburgo funciona em um modelo de autoatendimento, no qual os usuários retiram os produtos disponíveis e realizam o pagamento voluntariamente, sem a presença de um atendente.

### Problema

A ausência de um sistema de controle dificulta o registro das compras, o acompanhamento dos pagamentos e a gestão dos produtos.

### Impacto

A falta de controle pode gerar prejuízos financeiros, inconsistências no estoque e dificuldade para acompanhar o consumo e a arrecadação da cantina, comprometendo sua organização e sustentabilidade.

### Justificativa

A implementação de um sistema de gerenciamento busca modernizar o funcionamento da cantina, automatizando o registro das compras, o controle de estoque e a gestão de créditos dos usuários. Dessa forma, pretende-se reduzir perdas, facilitar os pagamentos e proporcionar maior transparência, praticidade e eficiência na administração da Cantina da Honestidade.

## 2. Tecnologias utilizadas

O sistema utiliza as seguintes tecnologias:

- **Python:** linguagem de programação.
- **Streamlit:** desenvolvimento da interface.
- **MySQL:** armazenamento dos dados.
- **MySQL Connector/Python:** conexão entre Python e MySQL.
- **Streamlit Cookies Controller:** gerenciamento de cookies.
- **Git e GitHub:** versionamento e colaboração no desenvolvimento.

## 3. Pré-requisitos

Antes de instalar o projeto, é necessário possuir:

- Python 3.10 ou superior
- MySQL Server
- Git
- Visual Studio Code (recomendado) ou outra IDE
- Terminal: CMD ou PowerShell (Windows), Terminal (Linux/macOS)
- Conexão com a internet para clonar o repositório e instalar dependências.

## 4. Instalação do projeto

### 4.1. Clonar o repositório

Abra o terminal e execute:

git clone https://github.com/RaquelDFS/Cantina-da-Honestidade-1.0.0.git

Acesse a pasta do projeto pelo terminal:

cd Cantina-da-Honestidade-1.0.0

### 4.2. Criar o ambiente virtual

O ambiente virtual permite instalar as dependências do projeto separadamente de outros projetos Python.

Execute:
Windows:
py -m venv venv


Linux/macOS:
python3 -m venv venv

Ative o ambiente virtual:
Windows (CMD):
venv\Scripts\activate


Windows (PowerShell):
.\venv\Scripts\Activate.ps1


Linux/macOS:
source venv/bin/activate


Quando ativado, o terminal apresentará `(.venv)` antes do caminho da pasta.

### 4.3. Instalar as dependências

Com o ambiente virtual ativado, execute no seu terminal:
pip install -r requirements.txt


Isso instalará as bibliotecas necessárias para o funcionamento do projeto.

## 5. Configuração do MySQL

O sistema utiliza o MySQL local com as seguintes configurações:

| Configuração   | Valor                 |
| -------------- | --------------------- |
| Servidor       | localhost             |
| Usuário        | root                  |
| Banco de dados | cantina_honestidade   |
| Senha          | Definida pelo usuário |

A senha do MySQL deve ser informada por meio da variável de ambiente `MYSQL_PASSWORD`.

### 5.1. Configurar o banco
Configure as variáveis de ambiente para informar o banco de dados e a senha de acesso.

Windows:
set MYSQL_DATABASE=cantina_honestidade
set MYSQL_PASSWORD=sua_senha_mysql


Linux/macOS:
export MYSQL_DATABASE=cantina_honestidade
export MYSQL_PASSWORD="sua_senha_mysql"


Substitua sua_senha_mysql pela senha configurada no MySQL.

## 6. Criar o primeiro administrador

Para realizar o primeiro acesso administrativo, foi desenvolvido o script:
database/criar_admin_inicial.py
Esse script permite cadastrar o primeiro administrador diretamente no banco de dados, utilizando a função de geração de hash de senha.

### 6.1. Criando o primeiro administrador
Com o ambiente virtual ativado e as variáveis configuradas, execute:
py -m database.criar_admin_inicial


No Linux/macOS, caso necessário, substitua py por python3.

O sistema solicitará:
=== Cadastro do primeiro administrador ===

Nome:
E-mail:
Matrícula (7 números):
Senha (10 a 20 caracteres):


Preencha os dados respeitando as regras:
- Nome e e-mail obrigatórios.
- Matrícula com exatamente 7 números.
- Senha entre 10 e 20 caracteres.
Se tudo estiver correto, será exibida a mensagem:
Administrador cadastrado com sucesso!

## 7. Iniciar o sistema
Para iniciar a aplicação, execute:
streamlit run app.py


O sistema será iniciado e o endereço de acesso será exibido no terminal, normalmente:

http://localhost:8501

Acesse o endereço pelo navegador para utilizar a Cantina da Honestidade.

## 8. Finalizar o sistema
Para encerrar a aplicação:
1. Volte ao terminal onde o Streamlit está executando.
2. Pressione Ctrl + C.
3. Aguarde o encerramento.
Para desativar o ambiente virtual:
deactivate

## 9. Gestão financeira e orçamentária (P06)

A aplicação disponibiliza funcionalidades de acompanhamento financeiro e gestão de orçamentos para o perfil administrador.

### 9.1. Gestão de orçamentos

Na opção **Financeiro > Gerenciar orçamentos**, o administrador pode:

- Cadastrar um orçamento mensal, informando mês, ano e valor.
- Consultar os orçamentos cadastrados.
- Editar o valor de um orçamento existente.
- Evitar o cadastro duplicado de orçamento para o mesmo mês e ano.

Cada orçamento corresponde a um período mensal.

### 9.2. Indicadores financeiros

O painel administrativo apresenta indicadores para o mês e ano selecionados:

- **Orçamento:** valor definido para o período.
- **Gastos:** soma dos custos das movimentações de entrada de estoque com motivo `reposicao`.
- **Vendas:** soma dos valores totais das vendas registradas no período.
- **Saldo orçamentário:** orçamento menos gastos com reposições.
- **Percentual utilizado:** gastos divididos pelo orçamento, multiplicados por 100.
- **Resultado financeiro:** vendas menos gastos com reposições.

O resultado financeiro é um indicador simplificado: não considera todas as despesas operacionais da cantina. O valor de vendas representa as vendas registradas, não necessariamente os valores efetivamente recebidos.

### 9.3. Relatório financeiro mensal

O administrador pode selecionar um intervalo de meses e anos para consultar os indicadores financeiros de cada período.

O relatório permite comparar orçamentos, gastos, vendas, saldos e resultados financeiros entre diferentes meses.

### 9.4. Relatório financeiro diário

O administrador pode selecionar um intervalo de datas para consultar:

- Quantidade e valor das vendas por dia.
- Quantidade e custo das reposições por dia.
- Resultado financeiro diário.

O relatório também apresenta os dias sem movimentação, permitindo acompanhar todo o intervalo selecionado.

### 9.5. Exportação para Excel

Os relatórios mensal e diário podem ser exportados em arquivos `.xlsx`, utilizando a biblioteca `openpyxl`.

A biblioteca está incluída no arquivo `requirements.txt` e é instalada junto com as demais dependências do projeto.
