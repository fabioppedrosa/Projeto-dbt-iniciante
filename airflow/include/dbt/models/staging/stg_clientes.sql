WITH source AS (
    SELECT * FROM {{ source('raw', 'clientes') }}
),

renamed AS (
    SELECT
        cliente_id,
        UPPER(nome)                         AS nome,
        LOWER(email)                        AS email,
        cidade,
        data_cadastro,
        ativo,
        CURRENT_TIMESTAMP()                 AS _loaded_at
    FROM source
)

SELECT * FROM renamed
