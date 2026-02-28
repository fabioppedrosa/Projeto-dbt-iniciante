{% macro valor_por_status(coluna_valor, coluna_status) %}
    {% set status_list = ['concluido', 'pendente', 'cancelado'] %}
    {% for status in status_list %}
        SUM(CASE WHEN {{ coluna_status }} = '{{ status }}' 
            THEN {{ coluna_valor }} ELSE 0 END) AS valor_{{ status }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}
