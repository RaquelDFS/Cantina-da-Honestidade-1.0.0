
# Cantina da Honestidade 1.0.0

Sistema de gestão para a Cantina da Honestidade do SENAI Fraiburgo, com controle de usuários, créditos, compras e movimentações financeiras.

**Curso:** Superior de Tecnologia em Análise e Desenvolvimento de Sistemas (ADS)
**Turma:** GR ADSI 2025/2 1
**Unidade Curricular:** Projeto Aplicado II (AEx) - 474830
**Instituição:** SENAI/SC - Fraiburgo

## 1. Contextualização

A Cantina da Honestidade do SENAI/SC – Fraiburgo opera por confiança: os produtos ficam disponíveis e o pagamento é realizado voluntariamente em dinheiro, sem registro tecnológico das operações.

### Problema

Não há controle de quais produtos foram retirados, quem comprou, quanto foi pago ou qual o total arrecadado.

Isso permite retiradas sem pagamento, gerando perdas, e impede a consulta ao histórico de compras ou ao saldo por usuário.

O pagamento somente em dinheiro também dificulta situações em que o usuário não possui o valor exato.

### Impacto

A instituição sofre perdas financeiras e enfrenta dificuldades para acompanhar os resultados da cantina.

Os usuários, por sua vez, não possuem uma ferramenta para consultar seus gastos ou acompanhar o saldo disponível.

O mercado já oferece soluções semelhantes, como carteiras digitais, pagamentos por QR Code e relatórios de movimentações, demonstrando a possibilidade de utilizar recursos tecnológicos nesse contexto.

### Justificativa

O problema é real e mensurável na instituição.

A utilização da tecnologia permite preservar o conceito de honestidade enquanto acrescenta recursos de controle, como carteira virtual e registro de compras.

O objetivo é reduzir perdas, aumentar a transparência e tornar o processo mais prático para usuários e administradores.

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

- Python 3 instalado.
- MySQL Server 8 instalado e em execução.
- Git instalado.
- Visual Studio Code (recomendado).

Também é necessário conhecer a senha do usuário `root` do MySQL.

Os comandos apresentados neste documento utilizam o **PowerShell do Windows**.

## 4. Instalação do projeto

### 4.1. Clonar o repositório

Abra o PowerShell e execute:

```powershell
git clone https://github.com/RaquelDFS/Cantina-da-Honestidade-1.0.0.git
```

Acesse a pasta do projeto:

```powershell
cd Cantina-da-Honestidade-1.0.0
```

### 4.2. Criar o ambiente virtual

O ambiente virtual permite instalar as dependências do projeto separadamente de outros projetos Python.

Execute:

```powershell
py -m venv .venv
```

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Quando ativado, o terminal apresentará `(.venv)` antes do caminho da pasta.

### 4.3. Instalar as dependências

Com o ambiente virtual ativado, execute:

```powershell
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:

```text
streamlit
mysql-connector-python
streamlit-cookies-controller
```

## 5. Configuração do MySQL

O sistema utiliza o MySQL local com as seguintes configurações:

| Configuração   | Valor                 |
| -------------- | --------------------- |
| Servidor       | localhost             |
| Usuário        | root                  |
| Banco de dados | cantina_honestidade   |
| Senha          | Definida pelo usuário |

A senha do MySQL deve ser informada por meio da variável de ambiente `MYSQL_PASSWORD`.

### 5.1. Configurar a senha

No PowerShell, execute:

```powershell
$senhaSegura = Read-Host "Digite a senha do MySQL" -AsSecureString

$env:MYSQL_PASSWORD = [System.Net.NetworkCredential]::new(
    "",
    $senhaSegura
).Password
```

A senha não será exibida durante a digitação.

A variável ficará disponível na sessão atual do PowerShell.

**Importante:** ao abrir outro terminal, será necessário configurar novamente a variável.

Não coloque senhas pessoais diretamente nos arquivos do projeto nem envie credenciais ao GitHub.

### 5.2. Configuração da conexão Python

O arquivo `database/inicializar.py` é responsável pela inicialização do banco e pela conexão utilizada pela aplicação.

A configuração de conexão deve utilizar a variável de ambiente:

```python
import os
import mysql.connector
from pathlib import Path

config = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("MYSQL_PASSWORD")
}
```

Essa configuração permite que cada integrante utilize sua própria senha do MySQL sem precisar modificar o código.

**Atenção:** a leitura de `MYSQL_PASSWORD` precisa estar presente na versão compartilhada de `database/inicializar.py`. Enquanto essa correção não for integrada ao repositório, a instalação por clonagem poderá exigir esse ajuste manual.

## 6. Inicialização do banco de dados

O arquivo `database/schema.sql` contém as instruções SQL necessárias para criar o banco de dados e suas tabelas.

O banco utilizado pelo sistema é:

```text
cantina_honestidade
```

A aplicação possui uma função chamada `inicializar_banco()`, localizada em `database/inicializar.py`.

Essa função é chamada automaticamente pelo arquivo `app.py` durante a inicialização da aplicação.

Portanto, após configurar a conexão MySQL, não é necessário executar manualmente cada comando SQL do schema.

As tabelas previstas são:

1. usuarios
2. carteiras
3. produtos
4. vendas
5. itens_venda
6. movimentacoes_estoque
7. historico_alteracoes_produto
8. movimentacoes_carteira
9. orcamentos

A criação da estrutura foi validada em um banco de testes separado, utilizando MySQL 8.0.

**Observação:** a inicialização utiliza instruções `CREATE TABLE IF NOT EXISTS`. Esse procedimento cria tabelas inexistentes, mas não substitui um processo de atualização de estruturas já existentes.

## 7. Executar a aplicação

Com o ambiente virtual ativado e a senha do MySQL configurada, execute:

```powershell
python -m streamlit run app.py
```

Aguarde a inicialização.

O Streamlit informará o endereço local para acessar a aplicação pelo navegador, geralmente:

```text
http://localhost:8501
```

Na primeira execução, a aplicação tentará inicializar o banco de dados automaticamente.

Caso ocorra algum erro de conexão, verifique se o MySQL Server está em execução e se a variável `MYSQL_PASSWORD` foi configurada corretamente.

## 8. Criar o primeiro administrador

O cadastro público do sistema permite criar usuários com perfil `cliente`.

Para realizar o primeiro acesso administrativo, foi desenvolvido o script:

```text
database/criar_admin_inicial.py
```

Esse script permite cadastrar o primeiro administrador diretamente no banco de dados, utilizando a função de geração de hash de senha já existente no projeto.

### 8.1. Preparar o terminal

Abra outro terminal PowerShell na pasta principal do projeto.

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Configure o banco de dados:

```powershell
$env:MYSQL_DATABASE = "cantina_honestidade"
```

Configure a senha do MySQL:

```powershell
$senhaSegura = Read-Host "Digite a senha do MySQL" -AsSecureString

$env:MYSQL_PASSWORD = [System.Net.NetworkCredential]::new(
    "",
    $senhaSegura
).Password
```

### 8.2. Executar o cadastro

Execute:

```powershell
python -m database.criar_admin_inicial
```

O programa solicitará:

```text
=== Cadastro do primeiro administrador ===

Nome:
E-mail:
Matricula (7 numeros):
Senha (10 a 20 caracteres):
```

Preencha os dados respeitando as seguintes regras:

- Nome e e-mail obrigatórios.
- Matrícula com exatamente 7 números.
- Senha com 10 a 20 caracteres.

O script verifica se já existe um usuário com perfil `administrador`.

Caso já exista, um novo administrador não será criado por esse procedimento.

Se o cadastro for realizado corretamente, será exibida a mensagem:

```text
Administrador cadastrado com sucesso!
```

### 8.3. Primeiro acesso

Após cadastrar o administrador, acesse a aplicação Streamlit.

Na tela de login, informe:

- A matrícula cadastrada.
- A senha definida durante o cadastro.

O sistema utilizará a função `autenticar_usuario()` para validar as credenciais e identificar o perfil do usuário.

## 9. Encerrar a aplicação

Para interromper o Streamlit, volte ao terminal em que a aplicação está em execução e pressione:

```text
Ctrl + C
```

Para desativar o ambiente virtual, execute:

```powershell
deactivate
```

## 10. Problemas comuns

### Erro de conexão com MySQL

Verifique se:

- O MySQL Server está em execução.
- A senha do usuário `root` está correta.
- A variável `MYSQL_PASSWORD` foi configurada.
- O arquivo `database/inicializar.py` utiliza essa variável.

### Erro ao importar bibliotecas

Verifique se o ambiente virtual está ativado e execute novamente:

```powershell
python -m pip install -r requirements.txt
```

### O administrador não consegue fazer login

Confira se:

- A matrícula foi digitada corretamente.
- A senha corresponde à cadastrada.
- O administrador foi criado no mesmo banco utilizado pela aplicação.
- O usuário está com status `ativo`.

### Administrador já cadastrado

O script de inicialização permite criar o primeiro administrador somente quando ainda não existe um usuário com esse perfil.

Se já houver um administrador, o script informará essa condição e não realizará outro cadastro.

## 11. Organização do projeto

A aplicação está organizada nas seguintes pastas e arquivos:

```text
Cantina-da-Honestidade-1.0.0/
|
|-- controllers/
|   |-- usuario_controller.py
|   |-- ...
|
|-- database/
|   |-- conexao.py
|   |-- inicializar.py
|   |-- criar_admin_inicial.py
|   |-- schema.sql
|
|-- models/
|
|-- views/
|
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
```

**controllers:** contém funções responsáveis pelas operações e regras da aplicação.

**database:** contém a configuração de conexão, inicialização do banco, schema SQL e script de criação do administrador.

**models:** contém arquivos relacionados à organização dos dados do sistema.

**views:** contém as telas e componentes de interface desenvolvidos com Streamlit.

**app.py:** arquivo principal responsável pela execução da aplicação.

**requirements.txt:** lista as bibliotecas necessárias.

**README.md:** apresenta o projeto e orienta sua instalação e execução.

## 12. Considerações finais

A Cantina da Honestidade é um projeto acadêmico desenvolvido no curso de Tecnologia em Análise e Desenvolvimento de Sistemas do SENAI/SC – Fraiburgo, na unidade curricular Projeto Aplicado II.

O sistema busca aplicar os conhecimentos adquiridos durante a graduação no desenvolvimento de uma solução para uma necessidade real da instituição.

A aplicação utiliza Python, Streamlit e MySQL, com organização de código em diferentes módulos e versionamento por meio do GitHub.
