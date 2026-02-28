from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping
from datetime import datetime

DBT_PROJECT_PATH = "/usr/local/airflow/include/dbt"

profile_config = ProfileConfig(
    profile_name="estudo_dbt",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id="snowflake_default",
        profile_args={
            "account": "prirzub-dgc78146",
            "database": "ESTUDO_DB",
            "schema": "ANALYTICS",
            "warehouse": "ESTUDO_WH",
            "role": "SYSADMIN",
        }
    )
)

@dag(
    dag_id="pipeline_completo",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ingestao", "dbt", "snowflake"],
)
def pipeline_completo():

    # ── ETAPA 1: Ingestão ──────────────────────────────────────────
    # Simula novos pedidos chegando todo dia
    ingerir_pedidos = SnowflakeOperator(
        task_id="ingerir_pedidos",
        snowflake_conn_id="snowflake_default",
        sql="""
            INSERT INTO ESTUDO_DB.RAW.pedidos 
                (cliente_id, valor, status, data_pedido)
            VALUES
                (1, 320.00, 'concluido', CURRENT_DATE()),
                (2, 150.50, 'pendente',  CURRENT_DATE()),
                (3, 890.00, 'concluido', CURRENT_DATE()),
                (4, 45.00,  'cancelado', CURRENT_DATE()),
                (5, 670.00, 'concluido', CURRENT_DATE());
        """,
    )

    # Simula atualização de clientes
    ingerir_clientes = SnowflakeOperator(
        task_id="ingerir_clientes",
        snowflake_conn_id="snowflake_default",
        sql="""
            UPDATE ESTUDO_DB.RAW.clientes
            SET cidade = 'Brasília'
            WHERE cliente_id = 2;
        """,
    )

    # ── ETAPA 2: Validação pós ingestão ────────────────────────────
    validar_ingestao = SnowflakeOperator(
        task_id="validar_ingestao",
        snowflake_conn_id="snowflake_default",
        sql="""
            SELECT COUNT(*) as total
            FROM ESTUDO_DB.RAW.pedidos
            WHERE data_pedido = CURRENT_DATE()
            HAVING COUNT(*) = 0;
        """,
    )

    # ── ETAPA 3: Transformação com dbt via Cosmos ──────────────────
    transformacao_dbt = DbtTaskGroup(
        group_id="transformacao_dbt",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/bin/dbt",
        ),
        default_args={"retries": 1},
    )

    # ── ETAPA 4: Snapshot histórico ────────────────────────────────
    snapshot = SnowflakeOperator(
        task_id="verificar_snapshot",
        snowflake_conn_id="snowflake_default",
        sql="""
            SELECT COUNT(*) as versoes_historicas
            FROM ESTUDO_DB.SNAPSHOTS.snp_clientes;
        """,
    )

    # ── Definindo o fluxo ──────────────────────────────────────────
    [ingerir_pedidos, ingerir_clientes] >> validar_ingestao >> transformacao_dbt >> snapshot

pipeline_completo()
