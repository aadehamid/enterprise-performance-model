"""Build the shareable zip of this project and prove it carries no data or secrets.

The zip is `git archive` of a commit, so only tracked files ship. Every member is then
scanned: forbidden paths (data, env files, databases, dependency folders), secret-shaped
strings, and every value of the local neo4j_instance_credentials.env.

Usage:
    .venv\\Scripts\\python.exe src\\export_shareable_zip.py
    .venv\\Scripts\\python.exe src\\export_shareable_zip.py --ref shareable-snapshot --out dist\\lsc.zip
"""

import argparse
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / "neo4j_instance_credentials.env"
PREFIX = "KG_Data_Lineage_LSC/"

FORBIDDEN_PATH = re.compile(
    r"(^|/)(Data|\.venv|node_modules|synthetic_data|dist|\.e2e)/"
    r"|(^|/)\.env($|\.)(?!example$)"
    r"|credentials\.env$"
    r"|\.(db|sqlite3?|dump|backup|pbix|xlsx|xls|csv|parquet)$",
    re.IGNORECASE,
)
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_\-]{20,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "quoted secret literal": re.compile(
        r"(?i)\b\w*(?:api_?key|password|secret|token)\w*['\"]?\s*[:=]\s*(['\"])(?!<)[^'\"\s]{8,}\1"
    ),
    "env-file secret": re.compile(r"(?m)^[A-Z0-9_]*(?:API_KEY|PASSWORD|SECRET|TOKEN)[A-Z0-9_]*=(?!<|your[-_]|changeme|x{4})[^\s#'\"]{8,}"),
}


def local_secret_values(env_path: Path) -> set[str]:
    if not env_path.exists():
        return set()
    return {v for k, v in dotenv_values(env_path).items() if v and len(v) >= 8 and not k.endswith(("PORT", "DATABASE"))}


def scan(zip_path: Path, secrets: set[str]) -> list[str]:
    problems = []
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            rel = name.removeprefix(PREFIX)
            if FORBIDDEN_PATH.search(rel):
                problems.append(f"forbidden path: {rel}")
                continue
            if name.endswith("/"):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            for value in secrets:
                if value in text:
                    problems.append(f"local credential value in {rel}")
            for label, pattern in SECRET_PATTERNS.items():
                for match in pattern.finditer(text):
                    problems.append(f"{label} in {rel}: {match.group(0)[:12]}...")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", default="HEAD", help="Commit or branch to archive")
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "dist" / f"KG_Data_Lineage_LSC_{date.today():%Y%m%d}.zip")
    args = parser.parse_args()

    sha = subprocess.run(["git", "rev-parse", "--short", args.ref], cwd=PROJECT_ROOT, check=True,
                         capture_output=True, text=True).stdout.strip()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "archive", "--format=zip", f"--prefix={PREFIX}", "-o", str(args.out), args.ref],
                   cwd=PROJECT_ROOT, check=True)

    problems = scan(args.out, local_secret_values(ENV_PATH))
    with zipfile.ZipFile(args.out) as zf:
        files = [n for n in zf.namelist() if not n.endswith("/")]
    if problems:
        args.out.unlink()
        print(f"[FAIL] {len(problems)} problems; zip deleted")
        for p in problems:
            print(f"    {p}")
        return 1
    print(f"[ok] {args.out} from {args.ref} ({sha}): {len(files)} files, "
          f"{args.out.stat().st_size / 1024:.0f} KiB, no data paths, no secrets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
