{% macro centavos_para_reais(coluna) %}
    ROUND({{ coluna }} / 100.0, 2)
{% endmacro %}
