"""Test a live connection from Databricks to AuraDB (EPM-DEC-001-0109, decision 7), from this machine:

    uv run python -m pricing_demo.aura_test     # writes the secret scope, runs the probe in Databricks, prints the result

It writes the AuraDB login from the file EPM_AURA_ENV names (as in projection/rebuild_stores.py; by default
~/.config/neo4j/aura.env) into the Databricks secret scope epm-neo4j (keys uri, username, password) without printing a value, uploads aura_probe.py to the workspace, and runs it as a one-time serverless job
with the neo4j driver. The probe's JSON line goes to out/tech/aura-test.json. Free Edition limits outbound access, so
a failed step is a result, not an error here.
Sources: Databricks, "Secret management" (updated 2026-09-11: Databricks-backed scopes, dbutils.secrets.get, values
shown as [REDACTED]); "Run your Lakeflow Jobs with serverless compute for workflows" (updated 2026-10-09) and
"Configure the serverless environment" (updated 2026-10-22: a job task's dependencies, in requirements.txt form).
"""
import json
import os
import time

from .config import OUT, ROOT, databricks_env

SCOPE = "epm-neo4j"
AURA_ENV = "~/.config/neo4j/aura.env"  # the default login file; EPM_AURA_ENV names another
KEYS = {"uri": "NEO4J_URI", "username": "NEO4J_USERNAME", "password": "NEO4J_PASSWORD"}
NEO4J_DRIVER = "neo4j==5.28.1"
RESULT = os.path.join(OUT, "tech", "aura-test.json")


def aura_env():
    """The AuraDB login file: the one EPM_AURA_ENV names, or the default."""
    return os.path.expanduser(os.environ.get("EPM_AURA_ENV") or AURA_ENV)


def read_env(path):
    values = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def probe_line(logs):
    """The probe's result from the job's output: the one line it prints after AURA_PROBE."""
    for line in (logs or "").splitlines():
        if line.startswith("AURA_PROBE "):
            return json.loads(line[len("AURA_PROBE "):])
    raise SystemExit("the probe printed no result line")


def main():
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service import compute, jobs, workspace
    e = databricks_env()
    w = WorkspaceClient(host=e["DATABRICKS_HOST"], token=e["DATABRICKS_TOKEN"])
    login = read_env(aura_env())
    if SCOPE not in {s.name for s in w.secrets.list_scopes()}:
        w.secrets.create_scope(scope=SCOPE)
    for key, name in KEYS.items():
        w.secrets.put_secret(scope=SCOPE, key=key, string_value=login[name])
    print(f"secret scope {SCOPE}: wrote {', '.join(KEYS)} (values not printed)")

    folder = f"/Workspace/Users/{w.current_user.me().user_name}/pricing-demo"
    w.workspace.mkdirs(folder)
    path = f"{folder}/aura_probe.py"
    with open(os.path.join(ROOT, "pricing_demo", "aura_probe.py"), "rb") as f:
        w.workspace.upload(path, f, format=workspace.ImportFormat.RAW, overwrite=True)

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run = w.jobs.submit_and_wait(
        run_name="pricing-demo aura test",
        tasks=[jobs.SubmitTask(task_key="aura_probe", environment_key="probe",
                               spark_python_task=jobs.SparkPythonTask(python_file=path, source=jobs.Source.WORKSPACE))],
        environments=[jobs.JobEnvironment(environment_key="probe",
                                          spec=compute.Environment(environment_version="2", dependencies=[NEO4J_DRIVER]))])
    task_run = run.tasks[0].run_id
    output = w.jobs.get_run_output(task_run)
    result = {"started": started, "run_id": run.run_id, "state": str(run.state.result_state),
              "probe": probe_line(output.logs) if output.logs else None, "error": output.error}
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
