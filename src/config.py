from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


output_dir_value = os.getenv("OUTPUT_DIR", "data")
OUTPUT_DIR = Path(output_dir_value)
if not OUTPUT_DIR.is_absolute():
    OUTPUT_DIR = BASE_DIR / OUTPUT_DIR
OUTPUT_DIR = OUTPUT_DIR.resolve()

TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "REPLACE_WITH_YOUR_TUSHARE_TOKEN")
CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN",
    "REPLACE_WITH_YOUR_CLOUDFLARE_API_TOKEN",
)
CLOUDFLARE_ACCOUNT_ID = os.getenv(
    "CLOUDFLARE_ACCOUNT_ID",
    "REPLACE_WITH_YOUR_CLOUDFLARE_ACCOUNT_ID",
)
CLOUDFLARE_D1_DATABASE_ID = os.getenv(
    "CLOUDFLARE_D1_DATABASE_ID",
    "REPLACE_WITH_YOUR_D1_DATABASE_ID",
)
