# 🏗️ Modern Data Stack — dbt + Snowflake + Airflow

Projeto de estudo de engenharia de dados construindo uma stack moderna com **Snowflake** como data warehouse, **dbt** para transformação de dados e **Apache Airflow** (via Astronomer Cosmos) para orquestração de pipelines.

---

## 📐 Arquitetura

```
Fontes de Dados
      ↓
  Airflow (Orquestração)
      ↓
Snowflake RAW (Dados Brutos)
      ↓
dbt via Cosmos (Transformação)
      ↓
Snowflake Analytics (Dados Prontos para BI)
```

### Camadas do projeto dbt

```
RAW (Snowflake)
├── clientes          ← tabela bruta
└── pedidos           ← tabela bruta
        ↓
STAGING (views)
├── stg_clientes      ← limpeza e padronização
└── stg_pedidos       ← limpeza e padronização
        ↓
MARTS (tables)
├── fct_pedidos       ← fatos com pivot de valores por status
├── dim_clientes      ← dimensão com agregações de pedidos
└── dim_clientes_historico ← SCD Type 2 via snapshot
        ↓
SNAPSHOTS
└── snp_clientes      ← histórico de mudanças (SCD Type 2)
```

---

## 🛠️ Stack Tecnológica

| Ferramenta | Versão | Função |
|---|---|---|
| Snowflake | Standard | Cloud Data Warehouse |
| dbt Core | 1.7.x | Transformação de dados |
| Apache Airflow | 2.x (Astro Runtime 11.x) | Orquestração de pipelines |
| Astronomer Cosmos | 1.6.0 | Integração nativa dbt + Airflow |
| Docker + WSL | - | Ambiente local |
| Python | 3.12 | Runtime |

---

## 📁 Estrutura do Projeto

```
dbt_estudo/
├── estudo_dbt/                  ← projeto dbt
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_clientes.sql
│   │   │   ├── stg_pedidos.sql
│   │   │   ├── schema.yml
│   │   │   └── sources.yml
│   │   └── marts/
│   │       ├── fct_pedidos.sql
│   │       ├── dim_clientes.sql
│   │       ├── dim_clientes_historico.sql
│   │       └── schema.yml
│   ├── macros/
│   │   ├── padronizar_status.sql
│   │   ├── colunas_auditoria.sql
│   │   ├── centavos_para_reais.sql
│   │   └── valor_por_status.sql
│   ├── snapshots/
│   │   └── snp_clientes.sql
│   ├── tests/
│   │   └── assert_valor_pedido_positivo.sql
│   └── dbt_project.yml
│
└── airflow/                     ← projeto Airflow
    ├── dags/
    │   ├── dbt_pipeline.py           ← DAG com BashOperator
    │   ├── dbt_cosmos_pipeline.py    ← DAG com Cosmos
    │   └── pipeline_completo.py      ← DAG completo ingestão + dbt
    ├── include/
    │   └── dbt/                      ← cópia do projeto dbt
    ├── requirements.txt
    └── Dockerfile
```

---

## ⚙️ Configuração do Ambiente

### Pré-requisitos

- WSL2 (Ubuntu 24)
- Docker Desktop
- Python 3.12+
- Conta Snowflake (trial gratuito em [signup.snowflake.com](https://signup.snowflake.com))
- Astro CLI

### 1. Instalação do dbt

```bash
# Cria ambiente virtual
mkdir ~/dbt_estudo && cd ~/dbt_estudo
python3 -m venv venv
source venv/bin/activate

# Instala dbt com versões compatíveis
pip install \
  "dbt-snowflake==1.7.4" \
  "agate>=1.7.0,<1.10" \
  "isodate>=0.6,<0.7" \
  "importlib-metadata>=6.0,<7"

# Verifica
dbt --version
```

### 2. Inicialização do projeto dbt

```bash
dbt init estudo_dbt
cd estudo_dbt
```

O `profiles.yml` é gerado em `~/.dbt/profiles.yml`:

```yaml
estudo_dbt:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: 'ORG-ACCOUNT'        # formato: org-account em minúsculas
      user: seu_usuario
      password: sua_senha
      role: SYSADMIN
      warehouse: ESTUDO_WH
      database: ESTUDO_DB
      schema: ANALYTICS
      threads: 4
```

> **Como achar o account identifier:**
> ```sql
> SELECT CURRENT_ORGANIZATION_NAME() AS org,
>        CURRENT_ACCOUNT_NAME() AS account;
> -- Resultado: org-account (ex: prirzub-dgc78146)
> ```

### 3. Instalação do Airflow com Astro CLI

```bash
# Instala Astro CLI
curl -sSL install.astronomer.io | sudo bash -s

# Cria projeto
mkdir ~/dbt_estudo/airflow && cd ~/dbt_estudo/airflow
astro dev init
```

`requirements.txt`:

```
astronomer-cosmos==1.6.0
dbt-snowflake==1.7.4
agate>=1.7.0,<1.10
isodate>=0.6,<0.7
importlib-metadata>=6.0,<7
apache-airflow-providers-snowflake==5.8.0
protobuf>=4.0.0,<5.0.0
```

`Dockerfile` — usar runtime estável:

```dockerfile
FROM quay.io/astronomer/astro-runtime:11.3.0
```

```bash
# Copia projeto dbt para o include
cp -r ~/dbt_estudo/estudo_dbt ~/dbt_estudo/airflow/include/dbt

# Corrige permissões
chmod -R 777 ~/dbt_estudo/airflow/include/dbt

# Sobe o Airflow
astro dev start
```

Acessa em `http://localhost:8080` (user: `admin`, pass: `admin`)

---

## 🚀 Como Executar

### Rodando o dbt

```bash
cd ~/dbt_estudo/estudo_dbt
source ~/dbt_estudo/venv/bin/activate

# Roda todos os modelos
dbt run

# Roda por camada
dbt run --select staging
dbt run --select marts

# Roda testes
dbt test

# Roda snapshots
dbt snapshot

# Gera documentação
dbt docs generate && dbt docs serve
```

### Rodando via Airflow

Três DAGs disponíveis:

| DAG | Descrição |
|---|---|
| `dbt_pipeline` | Executa dbt via BashOperator (staging → marts → test → snapshot) |
| `dbt_cosmos_pipeline` | Executa dbt via Cosmos (1 task por modelo, com dependências automáticas) |
| `pipeline_completo` | Pipeline completo: ingestão → validação → dbt → snapshot |

---

## 📊 Modelos dbt

### Staging

**`stg_clientes`** — Padroniza dados de clientes
- Nome em maiúsculas, email em minúsculas
- Adiciona coluna de auditoria `_loaded_at`

**`stg_pedidos`** — Padroniza dados de pedidos
- Status padronizado via macro `padronizar_status()`
- Adiciona colunas de auditoria via macro `colunas_auditoria()`

### Marts

**`fct_pedidos`** — Fatos de pedidos agregados por cliente
- Pivot de valores por status usando macro `valor_por_status()`
- Colunas: `valor_concluido`, `valor_pendente`, `valor_cancelado`

**`dim_clientes`** — Dimensão de clientes ativos
- Agrega métricas de pedidos por cliente
- Total de pedidos, valor total, valor médio, primeira e última compra

**`dim_clientes_historico`** — Histórico SCD Type 2
- Baseado no snapshot `snp_clientes`
- Rastreia mudanças de cidade, email e status ativo

---

## 🧪 Testes

### Testes Genéricos (declarados nos `.yml`)

```yaml
# Exemplos de testes configurados
- unique
- not_null
- accepted_values:
    values: ['Concluído', 'Pendente', 'Cancelado', 'Desconhecido']
- relationships:
    to: ref('stg_clientes')
    field: cliente_id
```

### Testes Singulares

**`assert_valor_pedido_positivo`** — Falha se existir pedido com `valor <= 0`

```bash
# Rodar todos os testes
dbt test

# Rodar teste específico
dbt test --select assert_valor_pedido_positivo
```

---

## 🔧 Macros

| Macro | Descrição |
|---|---|
| `padronizar_status(coluna)` | Padroniza status para Concluído/Pendente/Cancelado |
| `colunas_auditoria()` | Adiciona `_loaded_at`, `_dbt_run_id`, `_ambiente` |
| `centavos_para_reais(coluna)` | Converte centavos para reais |
| `valor_por_status(valor, status)` | Gera colunas de pivot por status dinamicamente |

---

## 📸 Snapshots (SCD Type 2)

O snapshot `snp_clientes` rastreia mudanças históricas nos campos `cidade`, `email` e `ativo`.

```sql
-- Consulta histórico de um cliente
SELECT
    cliente_id,
    cidade,
    dbt_valid_from,
    dbt_valid_to
FROM ESTUDO_DB.SNAPSHOTS.snp_clientes
WHERE cliente_id = 1
ORDER BY dbt_valid_from;
```

---

## 🔗 Lineage Graph

Para visualizar o DAG completo de dependências:

```bash
dbt docs generate && dbt docs serve
# Acessa http://localhost:8080 → clica em "View Lineage Graph"
```

```
source:raw.clientes ──┐
                      ├──► stg_clientes ──┬──► dim_clientes
source:raw.pedidos  ──┘                   │
                      ├──► stg_pedidos  ──┼──► fct_pedidos
                      │                  └──► dim_clientes_historico
                      └──► snp_clientes ──────► dim_clientes_historico
```

---

## 📝 Conceitos Snowflake Abordados

- **Virtual Warehouses** — separação de compute e storage
- **Stages e COPY INTO** — carregamento batch de dados
- **VARIANT e FLATTEN** — dados semi-estruturados (JSON)
- **Time Travel** — consulta e recuperação de dados históricos
- **Zero-Copy Cloning** — clonagem instantânea sem duplicar storage
- **Snowpipe** — ingestão contínua e automática

---

## 🤝 Contribuições

Projeto desenvolvido para fins educacionais. Sinta-se à vontade para abrir issues ou pull requests.

---

## 📄 Licença

MIT
# Projeto-ShadowTraffic-dbt
# Projeto-ShadowTraffic-dbt
