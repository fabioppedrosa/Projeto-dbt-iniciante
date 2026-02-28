-- Esse teste FALHA se retornar qualquer linha
-- ou seja: se existir pedido com valor <= 0, o teste falha
SELECT
    pedido_id,
    valor
FROM {{ ref('stg_pedidos') }}
WHERE valor <0
