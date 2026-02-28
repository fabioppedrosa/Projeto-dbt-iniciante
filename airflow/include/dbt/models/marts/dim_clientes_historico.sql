WITH historico AS (
    SELECT * FROM {{ ref('snp_clientes') }}
)

SELECT
    cliente_id,
    nome,
    cidade,
    ativo,
    dbt_valid_from                          AS valido_desde,
    COALESCE(dbt_valid_to, '9999-12-31')   AS valido_ate,
    CASE
        WHEN dbt_valid_to IS NULL THEN TRUE
        ELSE FALSE
    END                                     AS is_current
FROM historico
ORDER BY cliente_id, dbt_valid_from
