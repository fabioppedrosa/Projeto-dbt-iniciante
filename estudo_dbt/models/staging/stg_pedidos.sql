WITH source AS (
    SELECT * FROM {{ source('raw', 'pedidos') }}
),

renamed AS (
    SELECT
        pedido_id,
        cliente_id,
        valor,
        {{ padronizar_status('status') }}       AS status,
        data_pedido,
        {{ colunas_auditoria() }}
    FROM source
)

SELECT * FROM renamed
