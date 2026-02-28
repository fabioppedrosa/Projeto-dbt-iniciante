{% snapshot snp_clientes %}

{{
    config(
        target_schema='snapshots',
        unique_key='cliente_id',
        strategy='check',
        check_cols=['cidade', 'email', 'ativo']
    )
}}

SELECT
    cliente_id,
    nome,
    email,
    cidade,
    ativo,
    data_cadastro
FROM {{ source('raw', 'clientes') }}

{% endsnapshot %}
