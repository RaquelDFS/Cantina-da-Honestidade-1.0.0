-- ==========================================================
-- CANTINA DA HONESTIDADE
-- MIGRACAO 001 - P05: AJUSTES DE INVENTARIO
-- ==========================================================
--
-- Objetivo:
-- Permitir ajustes positivos e negativos de estoque,
-- exigindo justificativa para ambos.
--
-- Aplicacao:
-- Bancos MySQL que ja possuem a tabela movimentacoes_estoque.
--
-- IMPORTANTE:
-- 1. Fazer backup antes de executar.
-- 2. Verificar se existem ajustes antigos sem justificativa.
-- 3. Executar esta migracao somente uma vez por banco.
-- 4. Nao executar o schema.sql completo para atualizar
--    uma instalacao existente.
--
-- ==========================================================
USE cantina_honestidade;
-- Verificacao previa:
-- Esta consulta deve retornar zero registros.
-- Se retornar registros, revisar antes de prosseguir.
SELECT id_movimentacao,
    id_produto,
    tipo,
    motivo,
    quantidade,
    descricao
FROM movimentacoes_estoque
WHERE motivo = 'ajuste'
    AND (
        descricao IS NULL
        OR CHAR_LENGTH(TRIM(descricao)) = 0
    );
-- Atualizacao da regra de movimentacao.
-- Preserva reposicao, venda e avaria.
-- Permite entrada e saida por ajuste com justificativa.
ALTER TABLE movimentacoes_estoque DROP CHECK chk_movimentacao_regras,
    ADD CONSTRAINT chk_movimentacao_regras CHECK (
        (
            tipo = 'entrada'
            AND motivo = 'reposicao'
            AND fornecedor IS NOT NULL
            AND CHAR_LENGTH(TRIM(fornecedor)) > 0
            AND valor_compra_unitario_registrado IS NOT NULL
        )
        OR (
            tipo = 'saída'
            AND motivo = 'venda'
            AND id_item_venda IS NOT NULL
        )
        OR (
            tipo = 'saída'
            AND motivo = 'avaria'
            AND id_item_venda IS NULL
        )
        OR (
            tipo IN ('entrada', 'saída')
            AND motivo = 'ajuste'
            AND id_item_venda IS NULL
            AND descricao IS NOT NULL
            AND CHAR_LENGTH(TRIM(descricao)) > 0
        )
    );
-- Verificacao posterior:
-- Confirma que a restricao foi atualizada.
SHOW CREATE TABLE movimentacoes_estoque;