/* PARTE DO THIAGO : AQUI VAI O CÓDIGO QUE CRIA A DATABASE E A TABELA */ 
/* Este código é temporário para que todos possam usar em seus respectivos pcs da xuxa*/ 

CREATE DATABASE estoque;
USE estoque;

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);