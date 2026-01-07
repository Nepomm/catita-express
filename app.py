from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Função para validar CPF (simples, apenas formato básico)
def validar_cpf(cpf):
    return len(cpf) == 14 and cpf[3] == '.' and cpf[7] == '.' and cpf[11] == '-'

# Função para validar o formato do celular (simples, apenas formato básico)
def validar_celular(celular):
    return len(celular) == 15 and celular[0] == '(' and celular[3] == ')'

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Recebe os dados do formulário
            nome = request.form["nome"]
            cpf = request.form["cpf"]
            celular = request.form["celular"]
            valor = float(request.form["valor"])
            dias = int(request.form["dias"])

            # Validação CPF e Celular
            if not validar_cpf(cpf):
                return jsonify({"erro": "CPF inválido. Formato esperado: xxx.xxx.xxx-xx."})

            if not validar_celular(celular):
                return jsonify({"erro": "Celular inválido. Formato esperado: (xx) xxxxx-xxxx."})

            if valor <= 0 or dias <= 0:
                return jsonify({"erro": "Por favor, insira valores positivos para valor e dias."})

            # Taxa de juros: 5% a cada 3 dias
            taxa_3_dias = 0.05
            periodos = dias / 3

            # Cálculo dos juros simples
            juros = valor * taxa_3_dias * periodos
            total = valor + juros

            # Cria dicionário com resultado para enviar ao HTML
            resultado = {
                "nome": nome,
                "cpf": cpf,
                "celular": celular,
                "valor": valor,
                "dias": dias,
                "juros": round(juros, 2),
                "total": round(total, 2)
            }

            # Retorna os dados no formato JSON para o frontend
            return jsonify(resultado)

        except Exception as e:
            return jsonify({"erro": str(e)})

    # Caso a requisição seja GET, renderiza o template
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
