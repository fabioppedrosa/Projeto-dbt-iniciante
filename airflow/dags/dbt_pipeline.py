from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from datetime import datetime

DBT_PROJECT_DIR = "/usr/local/airflow/include/dbt"
DBT_PROFILES_DIR = "/usr/local/airflow/include/dbt"

@dag(
    dag_id="dbt_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["dbt", "snowflake"],
)
def dbt_pipeline():

    dbt_run_staging = BashOperator(
        task_id="dbt_run_staging",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select staging --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_run_marts = BashOperator(
        task_id="dbt_run_marts",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --select marts --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt snapshot --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_run_staging >> dbt_run_marts >> dbt_test >> dbt_snapshot

dbt_pipeline()
