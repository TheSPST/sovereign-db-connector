#!/usr/bin/env python3
"""
================================================================================
  SOVEREIGN BYTE TECHNOLOGY — PROPRIETARY & CONFIDENTIAL TRADE SECRET
  Copyright (c) 2026 Sovereign Byte Technology. All Rights Reserved.
  Protected under 18 U.S.C. § 1836 (DTSA), UTSA, and International Treaties.
  Reverse engineering, unauthorized decompilation, or disclosure is prohibited.
================================================================================
Sovereign Database Streamer CLI (sov-db-stream)
Streams database dumps (mysqldump, pg_dump, Supabase) in real-time to Sovereign Vault (.spst)
"""

import sys
import os
import argparse
import urllib.request
import json

def main():
    parser = argparse.ArgumentParser(description="Sovereign In-Flight Database Dump Streamer (.spst)")
    parser.add_argument("--output", "-o", default="database_backup.spst", help="Output .spst file path")
    parser.add_argument("--api-url", default=os.getenv("SOVEREIGN_API_GATEWAY", "https://api.sovereignbyte.tech"), help="Sovereign API Gateway URL")
    parser.add_argument("--api-key", default=os.getenv("SOVEREIGN_API_KEY", "sov_trial_key"), help="Sovereign Enterprise / AWS Marketplace API Key")
    args = parser.parse_args()

    print(f"🗄️ Sovereign DB Streamer: Ingesting database dump from stdin...")
    
    raw_bytes = sys.stdin.buffer.read()
    if not raw_bytes:
        print("Error: No database stream received from stdin.")
        sys.exit(1)

    raw_mb = len(raw_bytes) / (1024.0 * 1024.0)
    print(f"📥 Received {raw_mb:.2f} MB uncompressed database stream. Compressing to .spst...")

    boundary = '----SovereignDBBoundary123'
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"api_key\"\r\n\r\n{args.api_key}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{os.path.basename(args.output)}\"\r\nContent-Type: application/octet-stream\r\n\r\n"
    ).encode('utf-8') + raw_bytes + f"\r\n--{boundary}--\r\n".encode('utf-8')

    req = urllib.request.Request(
        f"{args.api_url}/v1/compress",
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get('status') == 'success':
                download_url = f"{args.api_url}{res_data['download_url']}"
                urllib.request.urlretrieve(download_url, args.output)
                out_size = os.path.getsize(args.output)
                out_mb = out_size / (1024.0 * 1024.0)
                reduction = (1.0 - (out_size / len(raw_bytes))) * 100.0

                print(f"\n✅ BACKUP COMPLETED:")
                print(f"   -> Raw Dump Size:     {raw_mb:.2f} MB")
                print(f"   -> Sealed .spst Vault: {out_mb:.2f} MB")
                print(f"   -> Storage Slashed:   {reduction:.2f}% Reduction!")
                print(f"   -> Output File:       {args.output}")
            else:
                print(f"❌ Server Error: {res_data}")
    except Exception as e:
        print(f"❌ Network / Pipeline Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
