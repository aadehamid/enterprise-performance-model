import zipfile
from pathlib import Path

from export_shareable_zip import PREFIX, scan

TEMPLATE = Path(__file__).resolve().parents[1] / "neo4j_instance_credentials.env.example"


def _zip(tmp_path, files: dict[str, str]) -> Path:
    path = tmp_path / "probe.zip"
    with zipfile.ZipFile(path, "w") as zf:
        for name, text in files.items():
            zf.writestr(PREFIX + name, text)
    return path


def test_placeholder_template_and_env_lookups_pass(tmp_path):
    files = {
        "neo4j_instance_credentials.env.example": TEMPLATE.read_text(encoding="utf-8"),
        "app/config.py": 'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")\nself.driver = d(uri, password=NEO4J_PASSWORD)\n',
    }
    assert scan(_zip(tmp_path, files), secrets=set()) == []


def test_flags_keys_local_credentials_and_data_paths(tmp_path):
    files = {
        "notes.md": "use " + "sk-" + "proj-abcdefghijklmnopqrstuvwx1234 for now",
        "app/settings.py": "api_key = " + '"hunter2hunter2"\n',
        "run.env.example": "AZURE_OPENAI_API_KEY=0123456789abcdef\n",
        "docs/setup.md": "server pass is CorrectHorse42",
        "Data/sttm/source.xlsx": "",
        "neo4j_instance_credentials.env": "",
    }
    problems = scan(_zip(tmp_path, files), secrets={"CorrectHorse42"})
    assert any(p.startswith("OpenAI-style key in notes.md") for p in problems)
    assert any(p.startswith("quoted secret literal in app/settings.py") for p in problems)
    assert any(p.startswith("env-file secret in run.env.example") for p in problems)
    assert "local credential value in docs/setup.md" in problems
    assert "forbidden path: Data/sttm/source.xlsx" in problems
    assert "forbidden path: neo4j_instance_credentials.env" in problems
