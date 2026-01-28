from flask import Flask, render_template, request, jsonify, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_super_secreta"  # Para sessões

ADMIN_USUARIO = "admin"
ADMIN_SENHA = "minhasenha123"
ARQUIVO_SOLICITACOES = "solicitacoes.json"

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
    800: {15: 950, 30: 1000},
    850: {15: 1100, 30: 1200},
    900: {15: 1050, 30: 1200},
    950: {15: 1200, 30: 1300},
    1000: {15: 1250, 30: 1400},
}

# Funções auxiliares
def carregar_solicitacoes():
    try:
        with open(ARQUIVO_SOLICITACOES, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_solicitacao(dados):
    dados["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    solicitacoes = carregar_solicitacoes()
    solicitacoes.append(dados)
    with open(ARQUIVO_SOLICITACOES, "w", encoding="utf-8") as f:
        json.dump(solicitacoes, f, ensure_ascii=False, indent=4)

# Rota principal (GET e POST)
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
                solicitacoes = carregar_solicitacoes()
                if 0 <= index < len(solicitacoes):
                    solicitacoes.pop(index)
                    with open(ARQUIVO_SOLICITACOES, "w", encoding="utf-8") as f:
                        json.dump(solicitacoes, f, ensure_ascii=False, indent=4)
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

if __name__ == "__main__":
    app.run(debug=True)
