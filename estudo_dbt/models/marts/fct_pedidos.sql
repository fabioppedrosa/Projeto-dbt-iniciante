WITH pedidos AS (
    SELECT * FROM {{ ref('stg_pedidos') }}
),

clientes AS (
    SELECT * FROM {{ ref('stg_clientes') }}
),

final AS (
    SELECT
        p.pedido_id,
        p.cliente_id,
        c.nome                                          AS nome_cliente,
        c.cidade,
        p.status,
        p.valor,
        p.data_pedido,
        DATEDIFF('day', p.data_pedido, CURRENT_DATE()) AS dias_desde_pedido
    FROM pedidos p
    LEFT JOIN clientes c ON p.cliente_id = c.cliente_id
),

agregado AS (
    SELECT
        cliente_id,
        nome_cliente,
        cidade,
        {{ valor_por_status('valor', 'status') }}   -- macro gerando 3 colunas
    FROM final
    GROUP BY cliente_id, nome_cliente, cidade
)

SELECT * FROM agregado
