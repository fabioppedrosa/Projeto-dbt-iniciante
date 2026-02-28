from airflow.decorators import dag
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
    dag_id="dbt_cosmos_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["dbt", "cosmos", "snowflake"],
)
def dbt_cosmos_pipeline():

    dbt_tasks = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            dbt_executable_path="/usr/local/bin/dbt",
        ),
        default_args={"retries": 2},
    )

    dbt_tasks

dbt_cosmos_pipeline()
