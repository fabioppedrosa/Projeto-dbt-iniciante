WITH clientes AS (
    SELECT
        cliente_id,
        nome,           -- já vem tratado do staging
        email,          -- já vem tratado do staging
        cidade,
        data_cadastro
    FROM {{ ref('stg_clientes') }}
    WHERE ativo = TRUE
),

pedidos AS (
    SELECT
        cliente_id,
        SUM(valor)          AS valor_total,
        AVG(valor)          AS valor_medio,
        COUNT(*)            AS total_pedidos,
        MIN(data_pedido)    AS data_primeiro_pedido,
        MAX(data_pedido)    AS data_ultimo_pedido
    FROM {{ ref('stg_pedidos') }}
    GROUP BY cliente_id
),

final AS (
    SELECT
        c.cliente_id,
        c.nome,
        c.email,
        c.cidade,
        c.data_cadastro,
        COALESCE(p.total_pedidos, 0)        AS total_pedidos,
        COALESCE(p.valor_total, 0)          AS valor_total,
        COALESCE(p.valor_medio, 0)          AS valor_medio,
        p.data_primeiro_pedido,
        p.data_ultimo_pedido
    FROM clientes c
    LEFT JOIN pedidos p ON c.cliente_id = p.cliente_id
)

SELECT * FROM final
