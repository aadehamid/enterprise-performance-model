"""The export copies the allowlist, rewrites text, keeps binaries byte for byte, and reports outside the release."""
import json
import os

os.environ["EPM_RELEASE_OWNER_NAMES"] = "Ada Lovelace,Ada,adalove"  # a stand-in: no test names a person
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import export  # noqa: E402


def make_tree(root, files):
    for path, data in files.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        mode = "wb" if isinstance(data, bytes) else "w"
        with open(full, mode) as f:
            f.write(data)


def test_export_rewrites_copies_and_reports(tmp_path):
    epm = tmp_path / "epm"
    make_tree(str(epm), {
        "business_architecture/ontology/README.md": "See [EPM-DEC-001-0044](x.md) at https://w3id.org/lsc/ontology/.\n",
        "business_architecture/ontology/releases/core/2.4.0/core.ttl": "<https://w3id.org/lsc/ontology/modules/core/> a owl:Ontology .\n",
        "business_architecture/ontology/releases/core/2.3.0/core.ttl": "old\n",
        "business_architecture/ontology/releases/core/1.0.0/core.ttl": "older\n",
        "business_architecture/reference/downstream-peers/kpi.md": "Valero reports it.\n",
        "business_architecture/reference/APQC.xlsx": b"PK\x03\x04binary",
        "business_architecture/domain/decisions/EPM-DEC-001-0044-x.md": "| Date | 2026-10-18 |\n",
        "AGENTS.md": "agent rules\n",
    })
    skills = tmp_path / "skills"
    make_tree(str(skills), {"skills/data/ontology/SKILL.md": "By Ada.\n",
                            "skills/writing/clear-writing/calibration.md": "personal\n"})
    out = tmp_path / "release"
    report = export.export(str(epm), str(skills), str(out))
    assert (out / "business_architecture/ontology/README.md").read_text() == "See the decision of 2026-10-18 at https://w3id.org/mpc/ontology/.\n"
    assert (out / "business_architecture/ontology/releases/core/2.4.0/core.ttl").read_text().startswith("<https://w3id.org/mpc/")
    assert (out / "business_architecture/ontology/releases/previous/core/2.3.0/core.ttl").exists()
    assert not (out / "business_architecture/ontology/releases/core/1.0.0").exists()
    assert (out / "business_architecture/reference/industry-view/kpi.md").read_text() == "A U.S. refining peer reports it.\n"
    assert (out / "business_architecture/reference/APQC.xlsx").read_bytes() == b"PK\x03\x04binary"
    assert not (out / "business_architecture/domain/decisions").exists()
    assert not (out / "AGENTS.md").exists()
    assert (out / "skills/ontology/SKILL.md").read_text() == "By the author.\n"
    assert not (out / "skills/clear-writing/calibration.md").exists()
    assert not (out / "share-release-report.json").exists()
    with open(str(out) + "-report.json") as f:
        saved = json.load(f)
    assert saved["files"]["business_architecture/ontology/README.md"]["rules"] == {"iri": 1, "records": 1}
    assert saved["files"]["business_architecture/reference/APQC.xlsx"]["binary"] is True
    assert saved["epm"] == "epm" and "/" not in saved["epm"]
    assert report["rule_totals"]["iri"] >= 2


def test_export_refuses_an_existing_output(tmp_path):
    (tmp_path / "out").mkdir()
    r = subprocess.run([sys.executable, os.path.join(HERE, "export.py"), "--epm", str(tmp_path), "--out", str(tmp_path / "out")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "exists" in r.stderr


def test_remove_internal_option_leaves_the_internal_folder_out(tmp_path):
    epm = tmp_path / "epm"
    make_tree(str(epm), {"business_architecture/reference/internal/crack.md": "internal\n",
                         "business_architecture/reference/README.md": "notice\n"})
    export.export(str(epm), "", str(tmp_path / "a"))
    assert (tmp_path / "a/business_architecture/reference/internal/crack.md").exists()
    export.export(str(epm), "", str(tmp_path / "b"), remove_internal=True)
    assert not (tmp_path / "b/business_architecture/reference/internal").exists()
    assert (tmp_path / "b/business_architecture/reference/README.md").exists()


def test_every_kind_of_file_keeps_its_mode(tmp_path):
    import stat
    import zipfile
    epm = tmp_path / "epm"
    make_tree(str(epm), {"business_architecture/ontology/projection/run_local.sh": "#!/bin/sh\necho hi\n",
                         "business_architecture/reference/logo.png": b"\x89PNG\0\0"})
    with zipfile.ZipFile(str(epm / "business_architecture" / "reference" / "book.xlsx"), "w") as z:
        z.writestr("xl/sharedStrings.xml", "<sst/>")
    os.chmod(str(epm / "business_architecture/ontology/projection/run_local.sh"), 0o755)
    os.chmod(str(epm / "business_architecture/reference/logo.png"), 0o640)
    os.chmod(str(epm / "business_architecture/reference/book.xlsx"), 0o640)
    out = tmp_path / "release"
    export.export(str(epm), "", str(out))
    mode = lambda rel: stat.S_IMODE(os.stat(str(out / rel)).st_mode)
    assert mode("business_architecture/ontology/projection/run_local.sh") == 0o755
    assert mode("business_architecture/reference/logo.png") == 0o640
    assert mode("business_architecture/reference/book.xlsx") == 0o640


def test_export_refuses_a_link_on_a_shipped_path(tmp_path):
    outside = tmp_path / "outside.json"
    outside.write_text("SECRET-OUTSIDE-TREE\n")
    epm = tmp_path / "epm"
    make_tree(str(epm), {"business_architecture/ontology/README.md": "text\n"})
    folder = epm / "business_architecture/business_process"
    folder.mkdir(parents=True)
    (folder / "map.json").symlink_to(outside)
    out = tmp_path / "out"
    (tmp_path / "skills").mkdir()
    with pytest.raises(SystemExit, match="the release ships no links"):
        export.export(str(epm), str(tmp_path / "skills"), str(out))
    assert "SECRET-OUTSIDE-TREE" not in "".join(p.read_text() for p in out.rglob("*.json") if p.is_file())
