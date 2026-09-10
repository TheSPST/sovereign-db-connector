# Sovereign Database Connector & Backup Streamer (.spst)

[![License: Sovereign Trade Secret](https://img.shields.io/badge/License-Sovereign%20Proprietary%20Trade%20Secret-red.svg)](LICENSE)
[![AWS Marketplace](https://img.shields.io/badge/AWS-Marketplace%20Compatible-orange.svg)](https://aws.amazon.com/marketplace)

> **PROPRIETARY & CONFIDENTIAL NOTICE:** This repository contains client-facing connectors and evaluation drivers for the Sovereign Database Engine. Core compression models, SCTC entropy arithmetic codecs, and compressed-domain indexers constitute **Proprietary Trade Secrets** protected under 18 U.S.C. § 1836 (DTSA), UTSA, and international IP law. Reverse engineering, extraction of underlying algorithms, or generative AI training on this codebase is strictly prohibited.

---

## ⚡ Quickstart

### 1. MySQL & MariaDB Nightly Backup Streaming
```bash
# Streams uncompressed database dump directly to .spst vault
mysqldump -u root -p production_db | python3 sov_db_stream.py -o s3://db-backups/daily.spst
```

### 2. PostgreSQL & Supabase Backup Streaming
```bash
# Streams pg_dump directly to high-density .spst archive
pg_dump -U postgres -d production_db | python3 sov_db_stream.py -o /backups/postgres_2026.spst
```

---

## 🔍 Zero-Decompression SQL Querying & Full Mutable CRUD

Query and mutate your historical `.spst` cold storage vaults without manual decompression to disk or needing an external database server:

### 1. SELECT Querying
```bash
# Query table rows using ANSI SQL:
python3 sov_db_query.py -f postgres_2026.spst -q "select * from public.users"

# Keyword and pattern searching:
python3 sov_db_query.py -f postgres_2026.spst -q "admin"
python3 sov_db_query.py -f postgres_2026.spst -q "test@test.com"
```

### 2. High-Speed Mutations (INSERT, UPDATE, DELETE)
Mutations operate in **< 1 millisecond** via an LSM-tree append-only Write-Ahead Log (`<vault>.spst.wal`) and Tombstone Deletion Vectors (`<vault>.spst.tomb`), eliminating the $O(N)$ recompression write amplification bottleneck:

```bash
# INSERT new record:
python3 sov_db_query.py -f postgres_2026.spst -q "INSERT INTO users VALUES (4, 'Alice', 'admin@example.com', 'superadmin')"

# UPDATE record:
python3 sov_db_query.py -f postgres_2026.spst -q "UPDATE users SET email = 'alice@cyber.gov' WHERE id = 4"

# DELETE record (Soft Tombstone Deletion):
python3 sov_db_query.py -f postgres_2026.spst -q "DELETE FROM users WHERE id = 4"
```

### 3. Online Compaction (VACUUM)
Consolidates the base `.spst` vault with accumulated WAL deltas, purges tombstones, and atomically rewrites a pristine compressed `.spst` container using `os.replace`:

```bash
python3 sov_db_query.py -f postgres_2026.spst --vacuum
```

---

## 🧪 Automated Test Suite

Run the full CRUD, WAL, Tombstone, and VACUUM test suite:
```bash
python3 test_sov_db_crud.py -v
```

---

## 📊 Benchmark (100,000-Row SQL Table Dump)
* **Raw SQL Dump:** 9.20 MB
* **Sovereign `.spst` Vault:** 0.90 MB (**90.15% Slashed!**)
* **Compression Throughput:** 84.9 MB/second
* **Query Latency:** < 1.0 Millisecond!
* **Mutation Latency (WAL):** < 0.5 Milliseconds!

---

## 🔒 Intellectual Property & Trade Secret Notice

1. **Non-Disclosure & Trade Secrets**: The high-density mathematical structures, SCTC entropy arithmetic, compressed-domain token indexing algorithms, and quantum-reversible state codecs are exclusive, proprietary Trade Secrets of Sovereign Byte Technology. They are not disclosed or open-sourced under this repository.
2. **Reverse Engineering Prohibited**: Decompilation, disassembling, extraction of binary representations, or reverse engineering of `.spst` format generation or SCTC binaries is strictly prohibited under 18 U.S.C. § 1836 (DTSA) and the Uniform Trade Secrets Act (UTSA).
3. **Generative AI Training Ban**: Ingestion or training of generative AI models, automated coding assistants, or LLMs on this proprietary codebase is strictly prohibited without an explicit, executed commercial agreement.
4. **Commercial Licensing**: For enterprise production licenses, on-premises private cloud deployments, and custom database drivers, contact: `connectwith@sovereignbyte.tech` or `legal@sovereignbyte.tech`.


