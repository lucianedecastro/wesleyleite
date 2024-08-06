from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configurar o logger
logging.basicConfig(level=logging.INFO)

# Criar uma estrutura de dados (simulando um banco de dados)
atleta = {
    "nome": "Wesley Leite",
    "treinos_mar": [],
    "treinos_academia": [],
    "notas_etapas": [None, None, None, None],
    "colocacoes_etapas": [None, None, None, None],
    "variaveis_extras": {},
    "impactos_extras": {}
}

# Carregar histórico do arquivo JSON (se existir)
def carregar_historico():
    global atleta
    try:
        with open("historico_atleta.json", "r") as f:
            atleta = json.load(f)
    except FileNotFoundError:
        pass

carregar_historico()

# Função para gravar o histórico no arquivo JSON
def gravar_historico():
    with open("historico_atleta.json", "w") as f:
        json.dump(atleta, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar-treino-mar', methods=['POST'])
def registrar_treino_mar():
    data = request.form.get("data")
    logging.info(f'Registrando treino no mar: {data}')
    if not data:
        return jsonify({"error": "Data não fornecida."}), 400

    atleta["treinos_mar"].append(data)
    gravar_historico()
    return jsonify({"message": "Treino no mar registrado com sucesso."})

@app.route('/registrar-treino-academia', methods=['POST'])
def registrar_treino_academia():
    data = request.form.get("data")
    logging.info(f'Registrando treino na academia: {data}')
    if not data:
        return jsonify({"error": "Data não fornecida."}), 400

    atleta["treinos_academia"].append(data)
    gravar_historico()
    return jsonify({"message": "Treino na academia registrado com sucesso."})

@app.route('/adicionar-informacoes-etapa', methods=['POST'])
def adicionar_informacoes_etapa():
    try:
        etapa = int(request.form.get("etapa"))
        nota = float(request.form.get("nota"))
        colocacao = int(request.form.get("colocacao"))
        logging.info(f'Adicionando informações da etapa: {etapa}, nota: {nota}, colocacao: {colocacao}')

        if etapa < 1 or etapa > len(atleta["notas_etapas"]):
            return jsonify({"error": "Etapa inválida."}), 400

        atleta["notas_etapas"][etapa - 1] = nota
        atleta["colocacoes_etapas"][etapa - 1] = colocacao
        gravar_historico()
        return jsonify({"message": "Informações da etapa registradas com sucesso."})
    except ValueError:
        return jsonify({"error": "Dados inválidos."}), 400

@app.route('/obter-prognostico', methods=['POST'])
def obter_prognostico():
    notas = atleta["notas_etapas"]
    colocacoes = atleta["colocacoes_etapas"]
    variaveis_extras = atleta["variaveis_extras"]
    impactos_extras = atleta["impactos_extras"]

    X, y = preparar_dados_prognostico(notas, colocacoes, variaveis_extras, impactos_extras)
    modelo = criar_modelo_prognostico(X, y)

    prognostico = modelo.predict([[
        colocacoes[-1] if colocacoes[-1] is not None else 0,
        len(atleta["treinos_mar"]),
        len(atleta["treinos_academia"]),
        atleta.get("treino_mar_nota", 0),
        atleta.get("treino_academia_nota", 0)
    ]])[0]

    logging.info(f'Prognóstico gerado: {prognostico}')
    return jsonify({"prognostico": f"Prognóstico: {prognostico:.2f}"})

# Preparar dados para o modelo de prognóstico
def preparar_dados_prognostico(notas, colocacoes, variaveis_extras, impactos_extras):
    X = []
    y = np.array([nota for nota in notas if nota is not None])

    encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
    features_extras = []
    if variaveis_extras:
        features_extras = encoder.fit_transform([[valor for valor in variaveis_extras.values()]]).toarray()[0]

    for i, (nota, colocacao) in enumerate(zip(notas, colocacoes)):
        if nota is not None:
            features = [
                colocacao,
                len(atleta["treinos_mar"]),
                len(atleta["treinos_academia"]),
                atleta.get("treino_mar_nota", 0),
                atleta.get("treino_academia_nota", 0)
            ]

            if variaveis_extras:
                features = np.concatenate((features, features_extras), axis=0)
            X.append(features)

    X = np.array(X)
    if variaveis_extras:
        # Aplicar OneHotEncoder apenas nas features extras
        X[:, 3:] = encoder.transform(X[:, 3:])
    # Aplicar StandardScaler
    X = StandardScaler().fit_transform(X)

    return X, y

# Criar o modelo de prognóstico
def criar_modelo_prognostico(X, y):

    modelo = LinearRegression()
    modelo.fit(X, y)

    return modelo

if __name__ == "__main__":
    app.run(debug=True)