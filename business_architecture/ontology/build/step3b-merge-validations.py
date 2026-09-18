#!/usr/bin/env python3
"""Step 3b merge: combine EIA glossary + web validator results into adoptions.

Reads:
  step3b-definition-review.csv        (all 503 rows, with APQC candidates)
  eia-glossary.json                   (2,641 cached EIA terms)
  step3b-web-validations*.json        (one or more files; slug -> validator record)

Writes:
  step3b-adoptions.json               (slug -> {definition, apqc, validators})
  updates step3b-definition-review.csv in place with Decision/Notes columns

Adoption rule (unchanged, locked):
  strong LSC->APQC match (score >= 0.6) AND a validator definition that
  agrees with the APQC description (recall of validator content terms in
  the APQC text >= 0.4) -> ADOPTED.
Validators are recorded with exact provenance: kind, label, url, agreement.
"""
import csv
import glob
import json
import re
from pathlib import Path

HERE = Path(__file__).parent

STOP = {
    "a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "by",
    "on", "as", "is", "are", "was", "were", "be", "been", "it", "its",
    "that", "this", "these", "those", "at", "from", "into", "which",
    "will", "can", "may", "including", "include", "includes", "such",
    "their", "they", "them", "we", "our", "you", "your", "i", "he",
    "she", "his", "her", "has", "have", "had", "do", "does", "did",
    "not", "no", "but", "if", "then", "than", "so", "up", "out", "over",
    "under", "between", "through", "during", "each", "other", "more",
    "most", "all", "any", "both", "either", "while", "where", "when",
    "how", "what", "who", "whom", "whose", "also", "within", "without",
    "about", "against", "among", "per", "via", "etc", "eg", "ie",
}

VERBS = {
    "maintain", "manage", "perform", "develop", "define", "operate",
    "monitor", "plan", "schedule", "analyze", "analyse", "create",
    "establish", "implement", "execute", "coordinate", "review",
    "assess", "evaluate", "track", "report", "communicate", "provide",
    "ensure", "support", "conduct", "process", "handle", "resolve",
    "design", "build", "prepare", "administer", "oversee", "direct",
    "lead", "facilitate", "deliver", "distribute", "collect", "gather",
    "capture", "store", "retain", "dispose", "archive", "update",
    "improve", "optimize", "identify", "determine", "select", "choose",
    "approve", "authorize", "negotiate", "procure", "purchase", "sell",
    "market", "promote", "price", "invoice", "bill", "collect",
    "reconcile", "audit", "inspect", "test", "validate", "verify",
    "certify", "accredit", "train", "educate", "coach", "mentor",
    "hire", "recruit", "onboard", "terminate", "compensate", "reward",
    "deploy", "install", "configure", "integrate", "migrate", "backup",
    "restore", "secure", "protect", "comply", "enforce", "investigate",
    "respond", "recover", "remediate", "clean", "decommission",
    "retire", "forecast", "budget", "allocate", "control", "measure",
}


def tokens(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def norm(t):
    # naive singularization so "benefits" matches "benefit"
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        return t[:-1]
    return t


def content_tokens(s):
    return {norm(t) for t in tokens(s) if t not in STOP and len(t) > 2}


def agreement(validator_def, apqc_desc):
    """Recall of the validator definition's content terms in the APQC text."""
    v = content_tokens(validator_def)
    if not v:
        return 0.0
    a = content_tokens(apqc_desc)
    return len(v & a) / len(v)


def eia_keys(apqc_name):
    """Candidate EIA glossary keys: exact, naive singular, verb-stripped."""
    name = apqc_name.strip().lower()
    keys = {name}
    if name.endswith("s"):
        keys.add(name[:-1])
    words = name.split()
    if words and words[0] in VERBS:
        keys.add(" ".join(words[1:]))
        stripped = " ".join(words[1:])
        if stripped.endswith("s"):
            keys.add(stripped[:-1])
    return keys


AGREE_MIN = 0.4


def main():
    rows = list(csv.DictReader(
        open(HERE / "step3b-definition-review.csv", encoding="utf-8")))
    eia = json.loads((HERE / "eia-glossary.json").read_text(encoding="utf-8"))

    web = {}
    for path in sorted(glob.glob(str(HERE / "step3b-web-validations*.json"))):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        web.update(data)
    # Human gate: manual verdicts (reject/approve notes) override automated records
    manual_path = HERE / "step3b-web-validations-manual.json"
    if manual_path.exists():
        for slug, mrec in json.loads(manual_path.read_text(encoding="utf-8")).items():
            if slug in web and mrec.get("verdict"):
                web[slug]["verdict"] = mrec["verdict"]
                web[slug]["verdict_reason"] = mrec.get("verdict_reason", "")
    print(f"web validator records loaded: {len(web)}")

    # APQC descriptions for the strong rows (CSV column may be empty)
    web_input = {}
    p = HERE / "step3b-web-input.json"
    if p.exists():
        for r in json.loads(p.read_text(encoding="utf-8")):
            web_input[r["slug"]] = r.get("apqc_description", "")

    adoptions = {}
    for r in rows:
        slug = r["slug"]
        apqc_id = (r.get("apqc_id") or "").strip()
        apqc_name = (r.get("apqc_name") or "").strip()
        apqc_desc = (r.get("apqc_desc") or "").strip() or web_input.get(slug, "")
        triage = (r.get("triage") or "").strip()
        validators = []
        r.setdefault("web_validator", "")
        r.setdefault("web_agreement", "")

        if triage == "STRONG" and apqc_id and apqc_desc:
            # --- EIA check ---
            for k in eia_keys(apqc_name):
                if k in eia:
                    term = eia[k]
                    agr = agreement(term["definition"], apqc_desc)
                    if agr >= AGREE_MIN:
                        validators.append({
                            "kind": "eia",
                            "label": f"EIA Glossary: '{term['term']}'",
                            "url": term["url"],
                            "agreement": round(agr, 3),
                        })
                    break
            # --- web check ---
            w = web.get(slug)
            if w and w.get("definition"):
                if w.get("verdict") == "reject":
                    r["Decision"] = "REJECTED"
                    r["Notes"] = w.get("verdict_reason", "manual reject")
                    continue
                agr = agreement(w["definition"], apqc_desc)
                if agr >= AGREE_MIN:
                    validators.append({
                        "kind": "web",
                        "label": w.get("validator_name", "web source"),
                        "url": w.get("validator_url", ""),
                        "agreement": round(agr, 3),
                    })
                else:
                    r["web_validator"] = w.get("validator_name", "")
                    r["web_agreement"] = str(round(agr, 3))

        if validators:
            adoptions[slug] = {
                "definition": apqc_desc,
                "apqc": {"id": apqc_id, "name": apqc_name},
                "validators": validators,
            }
            r["Decision"] = "ADOPTED"
            r["Notes"] = ("adopted APQC description; validators agree: "
                          + "; ".join(
                              f"{v['label']} ({v['agreement']})"
                              for v in validators))
        elif triage == "STRONG":
            r["Decision"] = "NO SOURCE"
            r["Notes"] = "strong APQC candidate but no validator agreed"
        elif triage == "WEAK":
            r["Decision"] = "REVIEW LINK"
            r["Notes"] = "weak APQC candidate; manual review needed"
        else:
            r["Decision"] = "NO CANDIDATE"
            r["Notes"] = "no meaningful APQC candidate"

    with open(HERE / "step3b-adoptions.json", "w",
              encoding="utf-8") as f:
        json.dump(adoptions, f, indent=2, ensure_ascii=False)

    with open(HERE / "step3b-definition-review.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"adoptions: {len(adoptions)} of {len(rows)} rows")
    print("wrote step3b-adoptions.json + updated step3b-definition-review.csv")


if __name__ == "__main__":
    main()
