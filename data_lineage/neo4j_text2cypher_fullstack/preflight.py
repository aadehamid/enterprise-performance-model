#!/usr/bin/env python3
"""
preflight.py  --  READ-ONLY connectivity check for the Text2Cypher build.

This build needs no vector index / lexical graph -- it runs read-only
Text2Cypher against whatever existing Neo4j you point it at. So preflight
only verifies:
  1. Bolt connectivity + auth using backend/.env
  2. The database actually has data (some nodes exist)
  3. The connecting user is READ-ONLY (a test write is attempted and MUST
     fail; if it succeeds you're using a read/write account -- switch to a
     read-only one before exposing the app)

    python preflight.py            # uses ./backend/.env
    python preflight.py path/to/.env
"""
import os
import sys

try:
    from dotenv import load_dotenv
    from neo4j import GraphDatabase
except ImportError:
    sys.exit("Missing deps. Run:  pip install neo4j python-dotenv")

G, R, Y, X = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
def ok(m):   print(f"{G}  PASS{X}  {m}")
def bad(m):  print(f"{R}  FAIL{X}  {m}")
def warn(m): print(f"{Y}  WARN{X}  {m}")


def main():
    env_path = sys.argv[1] if len(sys.argv) > 1 else "backend/.env"
    if not os.path.exists(env_path):
        sys.exit(f"No env file at {env_path!r}. "
                 "Run this from the project root (where backend/ is).")
    load_dotenv(env_path)

    uri  = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    pwd  = os.getenv("NEO4J_PASSWORD")

    print(f"\nReading {env_path}")
    for name, val in (("NEO4J_URI", uri), ("NEO4J_USERNAME", user),
                       ("NEO4J_PASSWORD", pwd)):
        if not val:
            bad(f"{name} is empty")
        else:
            ok(f"{name} = {'*'*8 if name=='NEO4J_PASSWORD' else val}")
    if not all([uri, user, pwd]):
        sys.exit("\nFill in the blanks in backend/.env, then re-run.")

    print(f"\nConnecting to {uri} ...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        driver.verify_connectivity()
        ok("Bolt connectivity / auth")
    except Exception as e:
        bad(f"Could not connect: {e}")
        sys.exit("\nFor Aura the URI is neo4j+s://xxxxxxxx.databases.neo4j.io")

    failures = 0
    with driver.session() as s:
        try:
            n = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            (ok if n > 0 else bad)(f"Database has {n} nodes")
            if n == 0:
                warn("Empty DB -- the chatbot will connect but have "
                     "nothing to answer from.")
        except Exception as e:
            bad(f"Could not count nodes: {e}")
            failures += 1

        try:
            labels = [r["label"] for r in
                      s.run("CALL db.labels() YIELD label RETURN label")]
            ok(f"Labels Text2Cypher will see: {labels[:12]}"
               + (" ..." if len(labels) > 12 else ""))
        except Exception as e:
            warn(f"Could not list labels: {e}")

        # READ-ONLY enforcement: this write SHOULD fail.
        try:
            s.run("CREATE (:_preflight_should_never_exist) RETURN 1").consume()
            bad("Test write SUCCEEDED -- the configured user has WRITE access.")
            print(f"{R}  Use a READ-ONLY Neo4j user. Aura: a user with the "
                  f"'reader' role.{X}")
            try:
                s.run("MATCH (x:_preflight_should_never_exist) "
                      "DELETE x").consume()
                warn("Cleaned up the test node, but fix the credentials.")
            except Exception:
                warn("Could NOT clean up test node -- remove "
                     ":_preflight_should_never_exist manually.")
            failures += 1
        except Exception:
            ok("Test write correctly REJECTED -- user is read-only")

    driver.close()
    print()
    if failures:
        print(f"{R}{failures} issue(s) to fix before running.{X}")
        sys.exit(1)
    print(f"{G}Ready. Start with: docker compose up --build{X}")


if __name__ == "__main__":
    main()
