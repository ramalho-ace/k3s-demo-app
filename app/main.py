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


  # Redis cache removed — backend uses PostgreSQL only


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
<html lang="pt-br">
  <head>
    <meta charset='utf-8'/>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Click Counter</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body class="bg-gradient-to-br from-sky-50 to-indigo-50 min-h-screen flex items-center justify-center">
    <main class="max-w-xl w-full p-6">
      <div class="bg-white/80 backdrop-blur-md shadow-lg rounded-2xl p-8">
        <header class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-semibold text-slate-800">Contador de Cliques</h1>
          <span class="text-sm text-slate-500">Postgres demo</span>
        </header>

        <section class="text-center">
          <div class="text-6xl font-extrabold text-indigo-600 mb-4" id="count">...</div>
          <p class="text-sm text-slate-500 mb-6">Clique no botão para incrementar o contador persistido no PostgreSQL.</p>
          <div class="flex items-center justify-center gap-4">
            <button id="btn" class="px-6 py-3 rounded-full bg-indigo-600 text-white shadow hover:bg-indigo-700 active:scale-95 transition">Clique</button>
            <button id="reset" class="px-4 py-2 rounded-lg border border-slate-200 text-slate-700 bg-white hover:bg-slate-50">Atualizar</button>
          </div>
        </section>

        <footer class="mt-6 text-xs text-slate-400 text-center">Demo simples — não usar em produção sem ajustes</footer>
      </div>
    </main>

    <script>
      async function refresh() {
        try {
          const res = await fetch('/count');
          const j = await res.json();
          document.getElementById('count').textContent = j.count;
        } catch (err) {
          document.getElementById('count').textContent = '—';
        }
      }

      document.getElementById('btn').addEventListener('click', async () => {
        const btn = document.getElementById('btn');
        btn.disabled = true;
        try {
          const res = await fetch('/inc', {method: 'POST'});
          const j = await res.json();
          document.getElementById('count').textContent = j.count;
        } catch (err) {
          console.error(err);
        } finally {
          btn.disabled = false;
        }
      });

      document.getElementById('reset').addEventListener('click', () => refresh());

      refresh();
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    ensure_table()
    port = int(os.environ.get("PORT", 8090))
    app.run(host='0.0.0.0', port=port)
