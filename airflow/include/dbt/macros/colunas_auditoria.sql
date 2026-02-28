{% macro colunas_auditoria() %}
    CURRENT_TIMESTAMP()                     AS _loaded_at,
    '{{ invocation_id }}'                   AS _dbt_run_id,
    '{{ target.name }}'                     AS _ambiente
{% endmacro %}
