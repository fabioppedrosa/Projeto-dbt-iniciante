{% macro padronizar_status(coluna) %}
    CASE LOWER({{ coluna }})
        WHEN 'concluido'  THEN 'Concluído'
        WHEN 'pendente'   THEN 'Pendente'
        WHEN 'cancelado'  THEN 'Cancelado'
        ELSE 'Desconhecido'
    END
{% endmacro %}
