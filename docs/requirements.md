# SupplyX Requirements Checklist & Implementation Matrix

| ID | Requirement | Category | Target File(s) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Inspect files & genuine schema (verify absent fields: shipping cost, inventory, supplier, lead times, warehouse capacity) | Architecture / Schema | `src/profiling.py`, `docs/data_dictionary.md` | Completed (Verified Absent) |
| **REQ-02** | Python data profiling: types, nulls, duplicates, date validity, status categories, row checks | Data Quality | `src/profiling.py`, `src/cleaning.py` | Completed (180,519 rows clean) |
| **REQ-03** | Standardized data output & automated cleaning unit tests | Pipeline / Testing | `data/cleaned_supply_chain.csv`, `tests/test_cleaning.py` | Completed (5/5 tests passed) |
| **REQ-04** | Formulate KPIs mapped to actual columns; disclose unavailable shipping cost | Metrics / Strategy | `src/kpis.py`, `docs/kpi_definitions.md`, `tests/test_kpis.py` | Completed (6/6 tests passed) |
| **REQ-05** | Normalized SQLite schema (`supplyx.db`) with star schema dimensions & facts | Data Engineering | `sql/schema.sql`, `sql/load_data.py` | Completed (180,519 rows loaded) |
| **REQ-06** | 15 documented analytical SQL queries for delivery, mode, category, and trends | Analytics / SQL | `sql/queries.sql`, `tests/test_sql.py` | Completed (5/5 tests passed) |
| **REQ-07** | Exploratory Data Analysis & Causal vs. Correlation insights | Data Science / EDA | `src/eda.py`, `reports/eda_insights.md`, `tests/test_eda.py` | Completed (2/2 tests passed) |
| **REQ-08** | Time-series demand forecasting with chronological holdout split & baseline comparison | Machine Learning | `src/forecasting.py`, `tests/test_forecasting.py` | Completed (4/4 tests passed) |
| **REQ-09** | User-friendly Power BI specification & DAX measures (plain-English labels, visual cues) | BI & Reporting | `reports/power_bi_spec.md`, `tests/test_dashboard.py` | Completed (2/2 tests passed) |
| **REQ-10** | Standalone interactive executive dashboard viewer (`reports/dashboard.html`) | BI & Executive UI | `reports/dashboard.html` | Completed (Interactive Browser UI) |
| **REQ-11** | Documented extension: separate inventory & supplier reorder analytics | Extension Layer | `src/extension_inventory.py`, `data/extension_supplier_inventory.csv`, `tests/test_extension.py` | Completed (3/3 tests passed) |
| **REQ-12** | Requirements.txt, .gitignore, README, data dictionary, run guide, dashboard checklist | Packaging & Delivery | `README.md`, `docs/*`, `requirements.txt`, `.gitignore` | Completed |
