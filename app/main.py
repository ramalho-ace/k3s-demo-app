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
    <title>Contador de clicks</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
      }
      
      @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
      }
      
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3), 0 0 40px rgba(99, 102, 241, 0.1); }
        50% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.5), 0 0 60px rgba(99, 102, 241, 0.2); }
      }
      
      @keyframes scale-in {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
      
      @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
      }
      
      body {
        background: linear-gradient(-45deg, #e0f2fe, #dbeafe, #e0e7ff, #ede9fe);
        background-size: 400% 400%;
        animation: gradient-shift 15s ease infinite;
      }
      
      .card {
        animation: scale-in 0.5s ease-out;
      }
      
      .count-display {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
        transition: all 0.3s ease;
      }
      
      .count-display.bump {
        animation: bump 0.4s ease;
      }
      
      @keyframes bump {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2) rotate(5deg); }
      }
      
      .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        background-size: 200% 200%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
      }
      
      .btn-primary:hover {
        background-position: 100% 0;
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
      }
      
      .btn-primary:active {
        transform: translateY(0) scale(0.95);
      }
      
      .btn-primary::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
      }
      
      .btn-primary:active::before {
        width: 300px;
        height: 300px;
      }
      
      .btn-secondary {
        position: relative;
        background: white;
        transition: all 0.3s ease;
      }
      
      .btn-secondary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      }
      
      .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1), 
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
      }
      
      .floating-badge {
        animation: float 3s ease-in-out infinite;
      }
      
      .shimmer-text {
        background: linear-gradient(90deg, #64748b 0%, #94a3b8 50%, #64748b 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
      }
      
      .particle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.8) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: particle-float 4s linear infinite;
      }
      
      @keyframes particle-float {
        0% { transform: translateY(100vh) scale(0); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100vh) scale(1); opacity: 0; }
      }
    </style>
  </head>
  <body class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Partículas de fundo -->
    <div id="particles"></div>
    
    <main class="max-w-xl w-full p-6 relative z-10">
      <div class="glass-card rounded-3xl p-8 card">
        <header class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold text-slate-800" style="letter-spacing: -0.02em;">Contador de Cliques</h1>
          <span class="text-xs px-3 py-1 rounded-full bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 font-medium floating-badge">Postgres demo</span>
        </header>

        <section class="text-center">
          <div class="count-display text-7xl font-black mb-6" id="count" style="letter-spacing: -0.03em;">...</div>
          <p class="shimmer-text text-sm font-medium mb-8">Clique no botão para incrementar o contador persistido no PostgreSQL</p>
          <div class="flex items-center justify-center gap-4">
            <button id="btn" class="btn-primary px-8 py-4 rounded-2xl text-white font-semibold shadow-lg relative z-10">
              ✨ Clique Aqui
            </button>
            <button id="reset" class="btn-secondary px-5 py-3 rounded-xl border-2 border-slate-200 text-slate-700 font-medium">
              🔄 Atualizar
            </button>
          </div>
        </section>

        <footer class="mt-8 text-xs text-slate-400 text-center opacity-75">
          Demo simples — não usar em produção sem ajustes
        </footer>
      </div>
    </main>

    <script>
      // Criar partículas de fundo
      const particlesContainer = document.getElementById('particles');
      for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 4 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        particlesContainer.appendChild(particle);
      }
      
      async function refresh() {
        try {
          const res = await fetch('/count');
          const j = await res.json();
          const countEl = document.getElementById('count');
          countEl.textContent = j.count;
          countEl.classList.remove('bump');
        } catch (err) {
          document.getElementById('count').textContent = '—';
        }
      }

      document.getElementById('btn').addEventListener('click', async () => {
        const btn = document.getElementById('btn');
        const countEl = document.getElementById('count');
        btn.disabled = true;
        try {
          const res = await fetch('/inc', {method: 'POST'});
          const j = await res.json();
          countEl.textContent = j.count;
          countEl.classList.add('bump');
          setTimeout(() => countEl.classList.remove('bump'), 400);
          
          // Efeito de confete
          createConfetti(btn);
        } catch (err) {
          console.error(err);
        } finally {
          btn.disabled = false;
        }
      });
      
      function createConfetti(element) {
        const colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'];
        const rect = element.getBoundingClientRect();
        
        for (let i = 0; i < 15; i++) {
          const confetti = document.createElement('div');
          confetti.style.position = 'fixed';
          confetti.style.left = rect.left + rect.width / 2 + 'px';
          confetti.style.top = rect.top + rect.height / 2 + 'px';
          confetti.style.width = '8px';
          confetti.style.height = '8px';
          confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
          confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
          confetti.style.pointerEvents = 'none';
          confetti.style.zIndex = '9999';
          document.body.appendChild(confetti);
          
          const angle = (Math.PI * 2 * i) / 15;
          const velocity = 100 + Math.random() * 100;
          const tx = Math.cos(angle) * velocity;
          const ty = Math.sin(angle) * velocity;
          
          confetti.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${tx}px, ${ty}px) scale(0) rotate(${Math.random() * 360}deg)`, opacity: 0 }
          ], {
            duration: 800,
            easing: 'cubic-bezier(0, .9, .57, 1)'
          }).onfinish = () => confetti.remove();
        }
      }

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
