from flask import Flask, render_template, request, jsonify, session
import json
from datetime import datetime
import os  # Para pegar PORT do ambiente
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "chave_super_secreta"  # Para sessões

ADMIN_USUARIO = "admin"
ADMIN_SENHA = "minhasenha123"

# Tabela fixa de empréstimos
TABELA_EMPRESTIMOS = {
    100: {15: 180, 30: 200},
    150: {15: 280, 30: 300},
    200: {15: 300, 30: 350},
    250: {15: 350, 30: 450},
    300: {15: 430, 30: 500},
    350: {15: 480, 30: 550},
    400: {15: 530, 30: 600},
    450: {15: 600, 30: 700},
    500: {15: 650, 30: 750},
    550: {15: 750, 30: 800},
    600: {15: 730, 30: 800},
    650: {15: 800, 30: 850},
    700: {15: 850, 30: 900},
    750: {15: 930, 30: 980},
    800: {15: 1000, 30: 1100},
    850: {15: 1050, 30: 1200},
    900: {15: 1100, 30: 1300},
    950: {15: 1200, 30: 1400},
    1000: {15: 1300, 30: 1500},
}

# -------------------- Conexão com PostgreSQL --------------------
def get_db():
    url = os.environ.get("DATABASE_URL")
    result = urlparse(url)
    return psycopg2.connect(
        database=result.path[1:],  # remove a barra inicial
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
    )

# Inicializa a tabela se não existir
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes (
            id SERIAL PRIMARY KEY,
            nome TEXT,
            cpf TEXT,
            celular TEXT,
            valor INTEGER,
            dias INTEGER,
            juros INTEGER,
            total INTEGER,
            data TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# -------------------- Funções de salvar e carregar --------------------
def carregar_solicitacoes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nome, cpf, celular, valor, dias, juros, total, data FROM solicitacoes ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "nome": r[0],
            "cpf": r[1],
            "celular": r[2],
            "valor": r[3],
            "dias": r[4],
            "juros": r[5],
            "total": r[6],
            "data": r[7],
        }
        for r in rows
    ]

def salvar_solicitacao(dados):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO solicitacoes (nome, cpf, celular, valor, dias, juros, total, data)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        dados["nome"],
        dados["cpf"],
        dados["celular"],
        dados["valor"],
        dados["dias"],
        dados["juros"],
        dados["total"],
        datetime.now().strftime("%d/%m/%Y %H:%M"),
    ))
    conn.commit()
    cur.close()
    conn.close()

# -------------------- Rota principal --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        acao = request.form.get("acao")

        # LOGIN ADMIN
        if acao == "login":
            usuario = request.form.get("usuario")
            senha = request.form.get("senha")
            if usuario == ADMIN_USUARIO and senha == ADMIN_SENHA:
                session["admin"] = True
                return jsonify(ok=True)
            return jsonify(ok=False, erro="Usuário ou senha incorretos")

        # LOGOUT ADMIN
        elif acao == "logout":
            session.clear()
            return jsonify(ok=True)

        # SIMULAÇÃO (NÃO SALVA)
        elif acao == "solicitar":
            try:
                nome = request.form["nome"]
                cpf = request.form["cpf"]
                celular = request.form["celular"]
                valor = int(float(request.form["valor"]))
                dias = int(request.form["dias"])

                if valor not in TABELA_EMPRESTIMOS or dias not in TABELA_EMPRESTIMOS[valor]:
                    return jsonify({"erro": "Valor ou prazo inválido."})

                total = TABELA_EMPRESTIMOS[valor][dias]
                juros = total - valor

                return jsonify({
                    "nome": nome,
                    "cpf": cpf,
                    "celular": celular,
                    "valor": valor,
                    "dias": dias,
                    "juros": juros,
                    "total": total
                })

            except Exception as e:
                return jsonify({"erro": str(e)})

        # CONFIRMAR SOLICITAÇÃO (SALVA)
        elif acao == "confirmar":
            try:
                dados = json.loads(request.form.get("dados"))
                salvar_solicitacao(dados)
                return jsonify(ok=True)
            except Exception as e:
                return jsonify(ok=False, erro=str(e))

        # EXCLUIR SOLICITAÇÃO
        elif acao == "excluir":
            try:
                index = int(request.form.get("index"))
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT id FROM solicitacoes ORDER BY id DESC")
                ids = [row[0] for row in cur.fetchall()]
                if 0 <= index < len(ids):
                    id_para_excluir = ids[index]
                    cur.execute("DELETE FROM solicitacoes WHERE id = %s", (id_para_excluir,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return jsonify(ok=True)
                return jsonify(ok=False)
            except Exception as e:
                return jsonify(ok=False, erro=str(e))

    # GET -> renderiza página
    solicitacoes = carregar_solicitacoes() if session.get("admin") else []
    return render_template(
        "index.html",
        admin_logado=session.get("admin", False),
        solicitacoes=solicitacoes,
        mostrar_painel=session.get("admin", False)
    )

# === Ajuste para produção (Railway / Render) ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

