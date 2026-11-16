CREATE DATABASE IF NOT EXISTS cantina_honestidade;
USE cantina_honestidade;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    perfil ENUM('administrador', 'gerente', 'cliente') NOT NULL,
    status ENUM('ativo', 'inativo') NOT NULL,
    matricula VARCHAR(7) NOT NULL,

    CONSTRAINT chk_usuario_nome CHECK (CHAR_LENGTH(TRIM(nome)) > 0),
    CONSTRAINT chk_usuario_matricula CHECK (matricula REGEXP '^[0-9]{7}$')
);

CREATE TABLE IF NOT EXISTS carteiras (
    id_carteira INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    saldo_atual DECIMAL(12,2) NOT NULL DEFAULT 0.00,

    CONSTRAINT fk_carteira_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT chk_saldo_carteira
        CHECK (saldo_atual >= 0)
);

CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT NULL,
    valor_compra_unitario_atual DECIMAL(10,2) NOT NULL,
    percentual_contribuicao DECIMAL(5,2) NOT NULL,
    preco_minimo_contribuicao DECIMAL(10,2) NOT NULL,
    quantidade_estoque INT NOT NULL,
    fornecedor_atual VARCHAR(150) NULL,
    status ENUM('ativo', 'inativo') NOT NULL DEFAULT 'ativo',
    motivo_inativacao ENUM('estoque_zero', 'manual') NULL,

    CONSTRAINT chk_produto_nome CHECK (CHAR_LENGTH(TRIM(nome)) BETWEEN 1 AND 50),
    CONSTRAINT chk_valor_compra CHECK (valor_compra_unitario_atual > 0),
    CONSTRAINT chk_percentual_contribuicao CHECK (percentual_contribuicao >= 0),
    CONSTRAINT chk_preco_minimo CHECK (preco_minimo_contribuicao > 0),
    CONSTRAINT chk_estoque CHECK (quantidade_estoque >= 0),
    CONSTRAINT chk_status_estoque CHECK (status != 'ativo' OR quantidade_estoque > 0)
);

CREATE TABLE IF NOT EXISTS vendas (
    id_venda INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_total DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_venda_cliente FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    CONSTRAINT chk_venda_valor CHECK (valor_total >= 0)
);

CREATE TABLE IF NOT EXISTS itens_venda (
    id_item_venda INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_venda INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_minimo_unitario_historico DECIMAL(10,2) NOT NULL,
    valor_total_pago DECIMAL(12,2) NOT NULL,
    valor_unitario_efetivo DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_item_venda FOREIGN KEY (id_venda) REFERENCES vendas(id_venda) ON DELETE CASCADE,
    CONSTRAINT fk_item_produto FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
    CONSTRAINT chk_item_quantidade CHECK (quantidade > 0),
    CONSTRAINT chk_item_preco_minimo CHECK (preco_minimo_unitario_historico > 0),
    CONSTRAINT chk_item_valor_total CHECK (valor_total_pago >= 0),
    CONSTRAINT chk_item_valor_unitario CHECK (valor_unitario_efetivo >= 0)
);

CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id_movimentacao INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_produto INT NOT NULL,
    id_usuario_responsavel INT NOT NULL,
    id_item_venda INT UNIQUE,
    
    tipo ENUM('entrada', 'saída') NOT NULL,

    motivo ENUM(
        'reposicao',
        'venda',
        'avaria',
        'ajuste'
    ) NOT NULL,

    quantidade INT NOT NULL,
    valor_compra_unitario_registrado DECIMAL(10,2) NULL,
    custo_total DECIMAL(12,2) NULL,
    fornecedor VARCHAR(150) NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descricao VARCHAR(255) NULL,

    CONSTRAINT fk_movimentacao_produto FOREIGN KEY (id_produto) REFERENCES produtos(id_produto),
    CONSTRAINT fk_movimentacao_usuario FOREIGN KEY (id_usuario_responsavel) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_movimentacao_item_venda FOREIGN KEY (id_item_venda) REFERENCES itens_venda(id_item_venda),
    CONSTRAINT chk_movimentacao_quantidade CHECK (quantidade > 0),
    CONSTRAINT chk_movimentacao_valor_compra CHECK (     valor_compra_unitario_registrado IS NULL     OR valor_compra_unitario_registrado > 0 ),
    CONSTRAINT chk_movimentacao_custo CHECK (     custo_total IS NULL OR custo_total >= 0 ),
    CONSTRAINT chk_movimentacao_regras CHECK (
        ( tipo = 'entrada' AND motivo = 'reposicao' AND fornecedor IS NOT NULL AND CHAR_LENGTH(TRIM(fornecedor)) > 0 AND valor_compra_unitario_registrado IS NOT NULL)
            OR
            (
                tipo = 'saída'
                AND motivo = 'venda'
                AND id_item_venda IS NOT NULL
            )
            OR
            (
                tipo = 'saída'
                AND motivo IN ('avaria', 'ajuste')
                AND id_item_venda IS NULL
            )
        )
);

CREATE TABLE IF NOT EXISTS historico_alteracoes_produto (
    id_alteracao INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_produto INT NOT NULL,
    id_usuario_responsavel INT NOT NULL,
    alteracoes JSON NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_historico_produto
        FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto),

    CONSTRAINT fk_historico_usuario
        FOREIGN KEY (id_usuario_responsavel)
        REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS movimentacoes_carteira (
    id_movimentacao INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_carteira INT NOT NULL,
    id_venda INT UNIQUE,
    id_usuario_responsavel INT NOT NULL,
    tipo ENUM('entrada', 'saída') NOT NULL,
    valor DECIMAL(12,2) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descricao VARCHAR(255) NULL,

    CONSTRAINT fk_mov_carteira FOREIGN KEY (id_carteira) REFERENCES carteiras(id_carteira),
    CONSTRAINT fk_mov_venda FOREIGN KEY (id_venda) REFERENCES vendas(id_venda),
    CONSTRAINT fk_mov_usuario FOREIGN KEY (id_usuario_responsavel) REFERENCES usuarios(id_usuario),
    CONSTRAINT chk_mov_carteira_valor CHECK (valor > 0),
    CONSTRAINT chk_mov_carteira_venda CHECK (     
        (tipo = 'entrada' AND id_venda IS NULL) OR     
        (tipo = 'saída' AND id_venda IS NOT NULL) )
);

CREATE TABLE IF NOT EXISTS orcamentos (
    id_orcamento INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_administrador INT NOT NULL,
    valor_definido DECIMAL(12,2) NOT NULL,
    periodo_inicial DATE NOT NULL,
    periodo_final DATE NOT NULL,
    data_hora_definicao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orcamento_administrador FOREIGN KEY (id_administrador) REFERENCES usuarios(id_usuario),
    CONSTRAINT chk_orcamento_valo  CHECK (valor_definido > 0),
    CONSTRAINT chk_orcamento_period  CHECK (periodo_final >= periodo_inicial)
);
