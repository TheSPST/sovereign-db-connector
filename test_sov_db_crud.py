#!/usr/bin/env python3
"""
================================================================================
  SOVEREIGN BYTE TECHNOLOGY — PROPRIETARY & CONFIDENTIAL TRADE SECRET
  Copyright (c) 2026 Sovereign Byte Technology. All Rights Reserved.
  Protected under 18 U.S.C. § 1836 (DTSA), UTSA, and International Treaties.
  Reverse engineering, unauthorized decompilation, or disclosure is prohibited.
================================================================================
  SOVEREIGN DATABASE CONNECTOR: CRUD & VACUUM TEST SUITE
  Verifies:
    1. Base Compressed SPST Container Loading
    2. Zero-Decompression ANSI SELECT Queries
    3. Low-Latency INSERT Mutations via Write-Ahead Log (WAL)
    4. Mutable UPDATE Mutations & Tombstone Deletion Vectors
    5. Soft DELETE Mutations & Deletion Vector Validation
    6. Online Compaction & VACUUM (WAL Consolidation & Recompression)
    7. Post-VACUUM Query Integrity
    8. Command-Line Interface (CLI) End-to-End Execution
================================================================================
"""

import os
import sys
import tempfile
import shutil
import zlib
import json
import subprocess
import unittest

# Ensure plugins/database-connector is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from sov_db_query import query_vault_engine, inflate_spst_vault

class TestSovereignDBCRUD(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sov_db_test_")
        self.vault_path = os.path.join(self.test_dir, "test_users.spst")
        self.wal_path = f"{self.vault_path}.wal"
        self.tomb_path = f"{self.vault_path}.tomb"

        # Create initial sample database dump
        init_sql = (
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, role TEXT);\n"
            "INSERT INTO users VALUES (1, 'Alice', 'alice@cyber.gov', 'admin');\n"
            "INSERT INTO users VALUES (2, 'Bob', 'bob@cyber.gov', 'analyst');\n"
            "INSERT INTO users VALUES (3, 'Charlie', 'charlie@cyber.gov', 'engineer');\n"
        )
        compressed_payload = zlib.compress(init_sql.encode("utf-8"), level=9)
        spst_bytes = b"SPST_V6\x00\x00" + compressed_payload

        with open(self.vault_path, "wb") as f:
            f.write(spst_bytes)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_select_baseline(self):
        """Verify baseline SELECT reads 3 initial records directly from SPST vault."""
        res = query_vault_engine(self.vault_path, "SELECT * FROM users")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["row_count"], 3)
        self.assertEqual(len(res["records"]), 3)
        names = [r["name"] for r in res["records"]]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)
        self.assertFalse(os.path.exists(self.wal_path))

    def test_02_insert_mutation_and_wal(self):
        """Verify INSERT creates .spst.wal and is instantly reflected in subsequent SELECT."""
        insert_query = "INSERT INTO users VALUES (4, 'Dave', 'dave@cyber.gov', 'auditor')"
        res_mut = query_vault_engine(self.vault_path, insert_query)
        self.assertEqual(res_mut["status"], "success")
        self.assertEqual(res_mut["mode"], "RELATIONAL_SQL_MUTATION")
        self.assertEqual(res_mut["operation"], "INSERT")
        self.assertEqual(res_mut["affected_rows"], 1)

        # Verify WAL file created and non-empty
        self.assertTrue(os.path.exists(self.wal_path))
        self.assertGreater(os.path.getsize(self.wal_path), 0)

        # Verify SELECT includes the newly inserted record
        res_sel = query_vault_engine(self.vault_path, "SELECT * FROM users")
        self.assertEqual(res_sel["row_count"], 4)
        names = [r["name"] for r in res_sel["records"]]
        self.assertIn("Dave", names)

    def test_03_update_mutation(self):
        """Verify UPDATE modifies existing record and records tombstone metadata."""
        # Insert first
        query_vault_engine(self.vault_path, "INSERT INTO users VALUES (4, 'Dave', 'dave@cyber.gov', 'auditor')")

        # Update email
        update_query = "UPDATE users SET email = 'david.d@cyber.gov' WHERE id = 4"
        res_upd = query_vault_engine(self.vault_path, update_query)
        self.assertEqual(res_upd["status"], "success")
        self.assertEqual(res_upd["affected_rows"], 1)

        # Tombstone file should exist
        self.assertTrue(os.path.exists(self.tomb_path))
        with open(self.tomb_path, "r", encoding="utf-8") as tf:
            tdata = json.load(tf)
            self.assertGreaterEqual(tdata["tombstone_count"], 1)

        # Query updated row
        res_sel = query_vault_engine(self.vault_path, "SELECT email FROM users WHERE id = 4")
        self.assertEqual(res_sel["row_count"], 1)
        self.assertEqual(res_sel["records"][0]["email"], "david.d@cyber.gov")

    def test_04_delete_mutation(self):
        """Verify DELETE removes record from query visibility without modifying base container."""
        # Delete Alice (id 1)
        delete_query = "DELETE FROM users WHERE id = 1"
        res_del = query_vault_engine(self.vault_path, delete_query)
        self.assertEqual(res_del["status"], "success")
        self.assertEqual(res_del["affected_rows"], 1)

        # Base .spst container remains untouched
        with open(self.vault_path, "rb") as f:
            raw = f.read()
        raw_text = inflate_spst_vault(raw).decode("utf-8")
        self.assertIn("Alice", raw_text)  # Immutability preserved in base

        # In-memory query reflects deletion
        res_sel = query_vault_engine(self.vault_path, "SELECT * FROM users")
        self.assertEqual(res_sel["row_count"], 2)
        names = [r["name"] for r in res_sel["records"]]
        self.assertNotIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)

    def test_05_vacuum_compaction(self):
        """Verify VACUUM consolidates WAL delta into a fresh .spst container and purges WAL & tombstones."""
        # Perform INSERT and DELETE
        query_vault_engine(self.vault_path, "INSERT INTO users VALUES (4, 'Dave', 'dave@cyber.gov', 'auditor')")
        query_vault_engine(self.vault_path, "DELETE FROM users WHERE id = 1")

        self.assertTrue(os.path.exists(self.wal_path))
        self.assertTrue(os.path.exists(self.tomb_path))

        # Run VACUUM
        res_vac = query_vault_engine(self.vault_path, vacuum=True)
        self.assertEqual(res_vac["status"], "success")
        self.assertEqual(res_vac["mode"], "RELATIONAL_SQL_VACUUM")
        self.assertEqual(res_vac["operation"], "VACUUM_COMPACT")
        self.assertGreater(res_vac["purged_wal_bytes"], 0)

        # Verify WAL and tombstone files are purged
        self.assertFalse(os.path.exists(self.wal_path))
        self.assertFalse(os.path.exists(self.tomb_path))

        # Verify compacted .spst container is clean and valid
        with open(self.vault_path, "rb") as f:
            raw = f.read()
        self.assertTrue(raw.startswith(b"SPST_V6\x00\x00"))
        compacted_text = inflate_spst_vault(raw).decode("utf-8")
        self.assertNotIn("Alice", compacted_text)  # Purged completely
        self.assertIn("Dave", compacted_text)   # Consolidated into base table

        # Query after vacuum
        res_sel = query_vault_engine(self.vault_path, "SELECT * FROM users ORDER BY id ASC")
        self.assertEqual(res_sel["row_count"], 3)
        ids = [int(r["id"]) for r in res_sel["records"]]
        self.assertEqual(ids, [2, 3, 4])

    def test_06_cli_execution(self):
        """Verify sov_db_query.py CLI handles --query (SELECT & MUTATION) and --vacuum flags."""
        cli_script = os.path.join(CURRENT_DIR, "sov_db_query.py")

        # 1. CLI Query
        cmd_sel = [sys.executable, cli_script, "-f", self.vault_path, "-q", "SELECT count(*) as total FROM users", "--format", "json"]
        out_sel = subprocess.check_output(cmd_sel, text=True)
        data_sel = json.loads(out_sel)
        self.assertEqual(int(data_sel["records"][0]["total"]), 3)

        # 2. CLI Insert
        cmd_ins = [sys.executable, cli_script, "-f", self.vault_path, "-q", "INSERT INTO users VALUES (10, 'Zoe', 'zoe@cyber.gov', 'ciso')", "--format", "json"]
        out_ins = subprocess.check_output(cmd_ins, text=True)
        data_ins = json.loads(out_ins)
        self.assertEqual(data_ins["status"], "success")
        self.assertEqual(data_ins["affected_rows"], 1)

        # 3. CLI Vacuum
        cmd_vac = [sys.executable, cli_script, "-f", self.vault_path, "--vacuum", "--format", "json"]
        out_vac = subprocess.check_output(cmd_vac, text=True)
        data_vac = json.loads(out_vac)
        self.assertEqual(data_vac["operation"], "VACUUM_COMPACT")

        # 4. Final verification via CLI
        cmd_fin = [sys.executable, cli_script, "-f", self.vault_path, "-q", "SELECT name FROM users WHERE id = 10", "--format", "json"]
        out_fin = subprocess.check_output(cmd_fin, text=True)
        data_fin = json.loads(out_fin)
        self.assertEqual(data_fin["records"][0]["name"], "Zoe")

if __name__ == "__main__":
    unittest.main()
