/* PARTE DO THIAGO : AQUI VAI O CÓDIGO QUE CRIA A DATABASE E A TABELA */
/* Este código é temporário para que todos possam usar em seus respectivos pcs da xuxa*/
/* Evita erros caso o banco ou a tabela já existam. */
thiago * / CREATE DATABASE IF NOT EXISTS estoque;
USE estoque;
CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);