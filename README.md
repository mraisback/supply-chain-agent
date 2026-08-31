# Supply Chain Intelligence Agent

A multi-agent AI system for supply chain optimization, combining deep domain expertise with technical execution. Built with Python, Llama, and autonomous agent architecture.

## Overview

This system implements a **Supply Chain Intelligence Agent** that operates across:
- **Demand Planning & Forecasting** (time series, ML models, accuracy metrics)
- **Inventory Management** (EOQ, safety stock, multi-echelon optimization)
- **Procurement & Sourcing** (Kraljic Matrix, TCO, supplier risk)
- **Network Design & Logistics** (facility location, transportation optimization)
- **Warehouse & Distribution Operations** (WMS data, OTIF, labor planning)
- **S&OP / IBP** (demand-supply balancing, scenario planning)
- **Risk & Resilience** (supply chain mapping, business continuity)

## Architecture

### Multi-Agent System
- **Coordinator Agent** — orchestrates workflows, breaks down goals into sub-tasks
- **Demand Planning Agent** — forecasting, demand sensing, new-product analysis
- **Inventory Agent** — EOQ, safety stock, ABC-XYZ segmentation
- **Procurement Agent** — sourcing strategy, supplier scoring, spend analysis
- **Network Agent** — facility location, transportation, cost-to-serve
- **Operations Agent** — WMS/ERP data, warehouse performance, OTIF
- **Risk Agent** — supply chain resilience, risk mapping, dual-sourcing

### Core Components
1. **Agent Runtime** — ReAct loop (Reasoning → Acting → Observing)
2. **Tool System** — code execution, API calls, database access, file I/O
3. **Domain Models** — forecasting, optimization, segmentation algorithms
4. **Data Layer** — pandas-based ETL, ERP/WMS parsing
5. **LLM Integration** — Llama-based reasoning and planning

## Tech Stack

- **Language**: Python 3.10+
- **LLM**: Llama (via Ollama or API)
- **Core Libraries**:
  - `langchain` or `crewai` — agent orchestration
  - `pandas`, `numpy` — data processing
  - `statsmodels`, `prophet`, `scikit-learn` — forecasting & ML
  - `pulp`, `google-or-tools` — optimization
  - `sqlalchemy` — database abstraction
  - `requests` — HTTP/API integration
  - `streamlit` or `dash` — dashboards

## Project Structure

```
supply-chain-agent/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── config/
│   ├── agent_config.yaml
│   └── domain_models.yaml
├── src/
│   ├── __init__.py
│   ├── coordinator.py           # Main orchestrator
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # Base agent class
│   │   ├── demand_planning.py
│   │   ├── inventory.py
│   │   ├── procurement.py
│   │   ├── network.py
│   │   ├── operations.py
│   │   └── risk.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── code_executor.py     # Execute Python code
│   │   ├── api_client.py        # HTTP/API calls
│   │   ├── database.py          # DB connections
│   │   ├── file_system.py       # File I/O
│   │   └── registry.py          # Tool registration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── forecasting.py       # ARIMA, Prophet, etc.
│   │   ├── optimization.py      # EOQ, network MILP, etc.
│   │   ├── segmentation.py      # ABC-XYZ, clustering
│   │   └── risk.py              # Risk scoring, simulation
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py            # CSV, Excel, ERP ingestion
│   │   ├── transformer.py       # ETL, cleaning, pivoting
│   │   └── profiler.py          # Data quality, profiling
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py            # Llama integration
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── messages.py          # Agent message types
│   │   └── domain.py            # Supply chain entities
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── validation.py
├── examples/
│   ├── demand_forecast.py
│   ├── inventory_optimization.py
│   ├── network_design.py
│   ├── procurement_analysis.py
│   └── end_to_end_workflow.py
├── dashboards/
│   ├── streamlit_app.py
│   └── assets/
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_models.py
└── data/
    ├── samples/                 # Example datasets
    └── exports/                 # Output files
```

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/mraisback/supply-chain-agent.git
cd supply-chain-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and set:
```
LLAMA_API_BASE=http://localhost:11434  # or remote Llama endpoint
LLAMA_MODEL=llama2  # or your preferred model
DATABASE_URL=sqlite:///supply_chain.db
```

### 3. Run Example

```bash
python examples/demand_forecast.py --data data/samples/demand.csv
```

### 4. Launch Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

## Core Workflows

### Demand Planning
```python
from src.agents.demand_planning import DemandPlanningAgent

agent = DemandPlanningAgent(llm_client)
forecast = await agent.forecast_demand(
    sku="SKU001",
    history_file="demand_history.csv",
    forecast_horizon=12,
    include_promotions=True
)
```

### Inventory Optimization
```python
from src.agents.inventory import InventoryAgent

agent = InventoryAgent(llm_client)
results = await agent.optimize_inventory(
    skus_file="skus.csv",
    annual_demand="demand.csv",
    service_level=0.95
)
# Returns: EOQ, reorder point, safety stock, ABC-XYZ classification
```

### Network Design
```python
from src.agents.network import NetworkAgent

agent = NetworkAgent(llm_client)
network = await agent.design_network(
    facilities_file="current_facilities.csv",
    demand_points="customer_locations.csv",
    cost_model="transportation_costs.csv"
)
# Returns: recommended facility locations, allocation, cost comparison
```

## Agent Communication Protocol

Agents use a structured message format for reasoning and tool calls:

```json
{
  "agent": "DemandPlanningAgent",
  "step": 1,
  "action": "reasoning",
  "content": "I need to analyze the demand history and select the appropriate forecasting model...",
  "tools_requested": [
    {
      "tool": "code_executor",
      "function": "load_and_profile_data",
      "params": {"file": "demand.csv"}
    }
  ]
}
```

## Tool System

All agents have access to:
- **code_executor** — run Python code, compute models, simulations
- **api_client** — call external APIs, webhooks, integrations
- **database** — query/insert data, access ERP systems
- **file_system** — read/write Excel, CSV, JSON, Parquet
- **visualization** — generate charts, build dashboards

## Data Handling

The system is built to handle real-world messy data:
- **Ingestion**: Excel exports, CSV, ERP dumps (SAP, Oracle, generic WMS)
- **Cleaning**: Handle blanks, duplicates, unit mismatches, date formats
- **Profiling**: Automatic data quality reporting before analysis
- **Transformation**: Pivots, aggregations, ETL pipelines
- **Export**: Write results back to Excel with formulas for auditability

## Examples

See `examples/` for:
- `demand_forecast.py` — Time-series forecasting with ARIMA/Prophet, accuracy metrics
- `inventory_optimization.py` — EOQ, safety stock, ABC-XYZ segmentation
- `network_design.py` — Facility location MILP, cost-to-serve
- `procurement_analysis.py` — Kraljic Matrix, TCO, supplier scoring
- `end_to_end_workflow.py` — Multi-agent orchestration on a complex scenario

## Documentation

- **Domain Models**: See `docs/domain_models.md` for formulas, metrics, and frameworks
- **Agent API**: See `docs/agent_api.md` for agent interfaces and methods
- **Tool API**: See `docs/tool_api.md` for available tools and examples
- **Examples**: See `examples/` for runnable workflows

## Contributing

1. Create a branch: `git checkout -b feature/agent-x`
2. Implement agent or tool
3. Add tests in `tests/`
4. Open a PR with example usage

## License

MIT

## Contact

Built by the Supply Chain Optimization team.
