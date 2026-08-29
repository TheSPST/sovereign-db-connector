# Sovereign Database Connector & Backup Streamer (.spst)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![AWS Marketplace](https://img.shields.io/badge/AWS-Marketplace%20Compatible-orange.svg)](https://aws.amazon.com/marketplace)

> **In-flight streaming compression and zero-decompression SQL query engine for PostgreSQL, MySQL, Supabase, and Oracle.** Slashes database backup storage bills by **85–90%** on Amazon S3.

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

## 🔍 Zero-Decompression SQL Querying
Query your historical `.spst` cold storage vaults without decompressing to disk:

```bash
curl -X POST "https://a3pme2hx4v.us-east-1.awsapprunner.com/v1/search" \
     -F "api_key=YOUR_API_KEY" \
     -F "query=FAILED_403" \
     -F "file=@postgres_2026.spst"
```

---

## 📊 Benchmark (100,000-Row SQL Table Dump)
* **Raw SQL Dump:** 9.20 MB
* **Sovereign `.spst` Vault:** 0.90 MB (**90.15% Slashed!**)
* **Compression Throughput:** 84.9 MB/second
* **Query Latency:** 2.08 Milliseconds!
