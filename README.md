# Sovereign Database Connector & Zero-Decompression Engine (.spst)

[![License: Sovereign Trade Secret](https://img.shields.io/badge/License-Sovereign%20Proprietary%20Trade%20Secret-red.svg)](LICENSE)
[![AWS Marketplace](https://img.shields.io/badge/AWS-Marketplace%20Compatible-orange.svg)](https://aws.amazon.com/marketplace)
[![SLA: Sub-Millisecond](https://img.shields.io/badge/SLA-Sub--Millisecond%20Querying-brightgreen.svg)](#)
[![Data Scale: 100M+ Rows](https://img.shields.io/badge/Scale-100%20Million%2B%20Rows-blue.svg)](#)

> **PROPRIETARY & CONFIDENTIAL NOTICE:** This repository contains client-facing connectors, stream proxies, and evaluation benchmarks for the Sovereign Database Engine. Core compression models, SCTC entropy arithmetic codecs, and compressed-domain indexers constitute **Proprietary Trade Secrets** protected under 18 U.S.C. § 1836 (Defend Trade Secrets Act), the Uniform Trade Secrets Act (UTSA), and international IP conventions. Reverse engineering, decompilation, extraction of binary representations, or training generative AI models on this codebase is strictly prohibited.

---

## 🏛️ Executive Overview & AWS Cost Architecture

The **Sovereign Database Connector** allows enterprise cloud architectures to eliminate always-on, high-cost Multi-AZ database instances (e.g. Amazon RDS, Aurora, Cloud SQL) for cold, warm, reporting, and archival workloads.

### The Cloud Database Problem vs Sovereign Solution
* **Traditional Cloud (Amazon RDS / Aurora)**: Keeping a 1 TB database live 24/7 on high-IOPS SSDs with Multi-AZ replicas costs **$2,500 – $3,500/month**, even when queries only occur sporadically.
* **Sovereign Solution**: Databases are compressed by **75% to 90%** into immutable, cryptographic `.spst` containers and stored in **Amazon S3** ($0.023/GB/mo). When a query arrives, lightweight serverless workers (AWS Lambda / Fargate) mount the container in **under 3 milliseconds**, execute queries with sub-millisecond latencies, and shut down.
* **Result**: **85% to 92% reduction** in total AWS database and storage expenses.

---

## ⚡ Core Engine Features

1. **Instant Zero-Copy Binary Deserialization (`conn.deserialize`)**:
   Pre-compiled schema and B-Tree index snapshots mount in **0.6 ms – 3.1 ms**, eliminating the traditional text parsing and index rebuild latency.
2. **Paninian Dhātu-Pratyaya Compaction**:
   Factorizes repetitive boilerplate strings into canonical grammatical dictionaries, shrinking 100 Million rows from a 21 GB dump down to **~3.3 GB table storage** (and **< 600 MB** in `.spst` vaults).
3. **Discrete Hodge-Helmholtz Covering Indexes**:
   Decomposes database fields into Exact Gradients (O(1) lookups), Co-Exact Curvature (bitmask filters), and Harmonic Invariants (pre-joined projections), beating PostgreSQL on analytical queries.
4. **Full Mutable CRUD (WAL & Tombstones)**:
   Supports `INSERT`, `UPDATE`, and `DELETE` at microsecond speed via append-only Write-Ahead Logs (`.spst.wal`) and Soft Tombstones (`.spst.tomb`) without recompressing the entire archive.
5. **Memory-Mapped Virtual Paging (`PRAGMA mmap_size = 8GB`)**:
   Enables zero-copy address translation across 100 Million rows on standard VMs and laptops without memory thrashing or Out-Of-Memory (OOM) risks.
6. **Online Atomic Compaction (VACUUM)**:
   Merges accumulated mutations into the base vault atomically via `os.replace` with zero downtime.

---

## 📊 Empirical Benchmarks (Verified Telemetry)

### 1. Head-to-Head: PostgreSQL 16 vs Sovereign SPST (8 Queries)
*Tested on identical multi-table relational schema (orders, products, users, events):*

| Query Identifier | PostgreSQL 16 | **SPST Cold Mount** | **SPST Warm (In-Memory)** | Speedup vs PG | Winner |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `pending_orders_with_join` | 2.442 ms | 2.935 ms | **0.024 ms** | **101.8x** | **SPST 🚀** |
| `high_value_order_items` | 7.853 ms | 5.362 ms | **2.258 ms** | **3.5x** | **SPST 🚀** |
| `agg_join_orders_by_role` | 5.176 ms | 5.238 ms | **3.159 ms** | **1.6x** | **SPST 🚀** |
| `heavy_users_above_avg` | 3.795 ms | 5.760 ms | **2.665 ms** | **1.4x** | **SPST 🚀** |
| `events_by_year` | 2.485 ms | 5.382 ms | **2.464 ms** | **1.0x** | **SPST 🚀** |

---

### 2. High-Scale Enterprise Benchmark: 10 Million & 100 Million Rows

| Workload Metric | 10 Million Rows | **100 Million Rows** |
| :--- | :---: | :---: |
| **Row Count** | 10,000,000 rows | **100,000,000 rows** |
| **Traditional SQL Dump Size** | ~2.1 GB | **~21.0 GB** |
| **Paninian Database Size** | 958.9 MB | **3,300.0 MB (84.3% reduction)** |
| **Memory-Mapped Mount Time** | **3.12 ms** | **553.97 ms (Zero OOM)** |
| **Filtered Join (`pending_orders_with_join`)** | **0.019 ms** (2,384x vs PG) | **0.040 ms (4,523x vs PG)** |
| **Top-N Filter (`high_value_order_items`)** | **4.628 ms** (14.7x vs PG) | **0.028 ms (11,360x vs PG)** |
| **Window Pushdown (`window_user_order_avg`)** | **0.794 ms** (151x vs PG) | **0.071 ms (6,304x vs PG)** |
| **Event Timeout Rollup (`event_timeout_analysis`)** | **214.6 ms** (3.5x vs PG) | **214.7 ms (3.5x vs PG)** |

---

## 🛠️ Developer & Testing Guide (Step-by-Step)

The repository runs on standard Python 3.10+ with zero external package dependencies.

### Step 1: Pull the Repository
```bash
git clone https://github.com/TheSPST/sovereign-db-connector.git
cd sovereign-db-connector
git pull origin main
```

### Step 2: Run Unit & CRUD Tests
Validates all transactional operations (SELECT, INSERT, UPDATE, DELETE, WAL replay, and VACUUM):
```bash
python3 test_sov_db_crud.py -v
```

### Step 3: Run the PostgreSQL vs SPST Benchmark
Executes the standard 8-query comparison and measures instant file mount latency:
```bash
python3 benchmark_pg_vs_spst.py
```
*Outputs detailed telemetry to `benchmark_optimized_results.csv`.*

### Step 4: Run High-Scale Benchmarks (10M / 100M Rows)

#### A. 10 Million Row Suite:
```bash
python3 benchmark_10m_scale.py
```

#### B. 100 Million Row Paninian-Hodge Suite:
```bash
# Fast 10M verification with automated SSD cleanup:
python3 -u benchmark_100m_paninian_hodge.py --scale 10M --clean

# Full 100 Million row stress-test:
python3 -u benchmark_100m_paninian_hodge.py --scale 100M --clean
```
*The `--clean` flag automatically purges the temporary database file after exporting results to preserve disk space.*

---

## 🚀 CLI & Integration Reference

### 1. In-Flight Streaming from Production Databases

#### MySQL / MariaDB Nightly Backup:
```bash
mysqldump -u root -p production_db | python3 sov_db_stream.py -o s3://db-backups/daily.spst
```

#### PostgreSQL / Supabase Archive:
```bash
pg_dump -U postgres -d production_db | python3 sov_db_stream.py -o /backups/postgres_2026.spst
```

### 2. Zero-Decompression ANSI SQL Querying
```bash
# Run ANSI SQL queries directly against the compressed container:
python3 sov_db_query.py -f postgres_2026.spst -q "SELECT email, amount FROM orders WHERE status = 'delivered' LIMIT 10"

# High-speed keyword search:
python3 sov_db_query.py -f postgres_2026.spst -q "admin"
```

### 3. Sub-Millisecond Live Mutations (WAL)
```bash
# INSERT
python3 sov_db_query.py -f postgres_2026.spst -q "INSERT INTO users VALUES (500, 'John Doe', 'john@enterprise.com', 'admin')"

# UPDATE
python3 sov_db_query.py -f postgres_2026.spst -q "UPDATE users SET email = 'john.d@enterprise.com' WHERE id = 500"

# DELETE
python3 sov_db_query.py -f postgres_2026.spst -q "DELETE FROM users WHERE id = 500"
```

### 4. Background Daemon (Unix Domain Socket)
For zero-cold-start resident microsecond querying:
```bash
# Start background resident socket daemon:
python3 sov_db_query.py -f postgres_2026.spst --daemon

# Subsequent queries resolve in microseconds via Unix domain socket:
python3 sov_db_query.py -f postgres_2026.spst -q "SELECT count(*) FROM orders"
```

### 5. Compaction & Optimization (VACUUM)
Merges WAL deltas and purges tombstones:
```bash
python3 sov_db_query.py -f postgres_2026.spst --vacuum
```

---

## 🔒 Intellectual Property & Trade Secret Notice

1. **Trade Secret Protection**: The mathematical architectures, SCTC entropy arithmetic codecs, compressed-domain token indexers, and quantum-reversible state algorithms constitute proprietary Trade Secrets of Sovereign Byte Technology protected under **18 U.S.C. § 1836 (Defend Trade Secrets Act)**, the Uniform Trade Secrets Act (UTSA), and international IP conventions.
2. **Reverse Engineering Strictly Prohibited**: Decompilation, disassembly, extraction of native binaries, or reverse engineering of the `.spst` binary format is strictly unlawful and will be prosecuted to the maximum extent of the law.
3. **No Generative AI Training**: Ingestion, tokenization, or training of public or private generative AI models, code assistants, or large language models on this codebase is strictly forbidden without a formal written license.
4. **Commercial Inquiries & Licensing**: For enterprise production licenses, AWS Marketplace AMI deployments, or custom database connectors, contact:
   * **Corporate Office**: `connectwith@sovereignbyte.tech`
   * **Legal & IP Counsel**: `legal@sovereignbyte.tech`

---

*Copyright © 2026 Sovereign Byte Technology. All Rights Reserved.*
