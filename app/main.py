import os
import time
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_HOST = os.environ.get("POSTGRES_HOST", "postgres")
DB_NAME = os.environ.get("POSTGRES_DB", "demo")
DB_USER = os.environ.get("POSTGRES_USER", "demo")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "demo")


def get_conn():
    attempts = 0
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
            return conn
        except Exception:
            attempts += 1
            if attempts > 30:
                raise
            time.sleep(1)


def ensure_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clicks (
            id integer PRIMARY KEY,
            count bigint NOT NULL
        )
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.route("/count", methods=["GET"])
def get_count():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT count FROM clicks WHERE id = 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"count": row["count"] if row else 0})


@app.route("/inc", methods=["POST"])
def inc_count():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT count FROM clicks WHERE id = 1 FOR UPDATE")
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO clicks (id, count) VALUES (1, 1)")
        new = 1
    else:
        new = row[0] + 1
        cur.execute("UPDATE clicks SET count = %s WHERE id = 1", (new,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"count": new})


@app.route("/", methods=["GET"])
def index():
    return """
<!doctype html>
<html>
  <head>
    <meta charset='utf-8'/>
    <title>Click Counter</title>
  </head>
  <body>
    <h1>Click Counter (Postgres)</h1>
    <div>
      <button id="btn">Click me</button>
      <span id="count">...</span>
    </div>
    <script>
      async function refresh() {
        const res = await fetch('/count');
        const j = await res.json();
        document.getElementById('count').textContent = j.count;
      }
      document.getElementById('btn').addEventListener('click', async () => {
        const res = await fetch('/inc', {method: 'POST'});
        const j = await res.json();
        document.getElementById('count').textContent = j.count;
      });
      refresh();
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    ensure_table()
    port = int(os.environ.get("PORT", 8090))
    app.run(host='0.0.0.0', port=port)
