from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from flask_assets import Environment, Bundle
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
        features_extras = encoder.fit_transform([[valor for valor em variaveis_extras.values()]]).toarray()[0]

    for i, (nota, colocacao) em enumerate(zip(notas, colocacoes)):
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

class Atleta:
    def __init__(self, nome):
        self.nome = nome
        self.treinos_mar = []
        self.treinos_academia = []
        self.notas_etapas = [None] * 4 # Lista para armazenar notas das 4 etapas
        self.colocacoes_etapas = [None] * 4 # Lista para armazenar colocações das 4 etapas
        self.variaveis_extras = {}
        self.impactos_extras = {} # Dicionário para armazenar impactos das variáveis extras
        self.modelo_prognostico = None
        self.encoder = None  # Armazena o encoder para uso posterior
        self.features_extras_names = []  # Armazena os nomes das features extras
        self.scaler = StandardScaler()  # Cria o StandardScaler aqui
        self.treino_mar_nota = 1 # Inicializa a nota do treino no mar
        self.treino_academia_nota = 1 # Inicializa a nota do treino na academia

    def registrar_treino_mar(self):
        resposta = input("Realizou treino no mar hoje? (sim/não): ")
        if resposta.lower() == "sim":
            self.treino_mar_nota = 5
            self.treinos_mar.append(datetime.date.today().strftime("%Y-%m-%d"))
            print("Treino no mar registrado com nota 5.")
        else:
            self.treinos_mar.append(input("Descreva o treino no mar: "))
            print("Treino no mar registrado com nota 1.")
        self.treinar_modelo_prognostico()

    def registrar_treino_academia(self):
        resposta = input("Realizou treino na academia hoje? (sim/não): ")
        if resposta.lower() == "sim":
            self.treino_academia_nota = 5
            self.treinos_academia.append(datetime.date.today().strftime("%Y-%m-%d"))
            print("Treino na academia registrado com nota 5.")
        else:
            self.treinos_academia.append(input("Descreva o treino na academia: "))
            print("Treino na academia registrado com nota 1.")
        self.treinar_modelo_prognostico()

    def adicionar_nota_etapa(self, etapa, nota, colocacao):
        if 1 <= etapa <= 4:
            self.notas_etapas[etapa - 1] = nota
            self.colocacoes_etapas[etapa - 1] = colocacao
            print(f"Nota da etapa {etapa} registrada: {nota}")
            print(f"Colocação na etapa {etapa} registrada: {colocacao}")
            self.treinar_modelo_prognostico()
        else:
            print("Etapa inválida. Digite um número de etapa entre 1 e 4.")

    def adicionar_variavel_extra(self, nome, impacto):
        if 1 <= impacto <= 5:
            self.variaveis_extras[nome] = " " # Adiciona um espaço para a variável (opcional)
            self.impactos_extras[nome] = impacto
            print(f"Variável extra '{nome}' com impacto {impacto} registrada.")
            self.treinar_modelo_prognostico()
        else:
            print("Impacto inválido. Digite um valor entre 1 e 5.")

    def treinar_modelo_prognostico(self):
        # Preparar os dados para o modelo
        X = []
        y = []

        for i, nota in enumerate(self.notas_etapas):
            if nota is not None:
                colocacao = self.colocacoes_etapas[i] or 0
                variaveis_extras_valores = list(self.variaveis_extras.values()) if self.variaveis_extras else []
                impacto_extras_valores = list(self.impactos_extras.values()) if self.impactos_extras else []

                # Construir o vetor de features
                features = [colocacao, len(self.treinos_mar), len(self.treinos_academia), self.treino_mar_nota, self.treino_academia_nota] + variaveis_extras_valores + impacto_extras_valores
                X.append(features)
                y.append(nota)

        if not X or not y:
            print("Dados insuficientes para treinar o modelo.")
            return

        # Ajustar o tamanho das listas
        X = np.array(X)
        y = np.array(y)

        # Aplicar o StandardScaler aos dados
        X_scaled = self.scaler.fit_transform(X)

        # Treinar o modelo de regressão linear
        self.modelo_prognostico = LinearRegression()
        self.modelo_prognostico.fit(X_scaled, y)
        print("Modelo de prognóstico treinado com sucesso.")

    def gerar_prognostico(self):
        if not self.modelo_prognostico:
            print("Modelo não treinado. Treine o modelo antes de gerar prognósticos.")
            return

        # Obter as features atuais
        colocacao_atual = self.colocacoes_etapas[-1] or 0
        variaveis_extras_valores = list(self.variaveis_extras.values()) if self.variaveis_extras else []
        impacto_extras_valores = list(self.impactos_extras.values()) if self.impactos_extras else []

        features = [colocacao_atual, len(self.treinos_mar), len(self.treinos_academia), self.treino_mar_nota, self.treino_academia_nota] + variaveis_extras_valores + impacto_extras_valores

        # Ajustar o tamanho da lista
        X_scaled = self.scaler.transform([features])

        # Gerar o prognóstico
        prognostico = self.modelo_prognostico.predict(X_scaled)[0]
        print(f"Prognóstico: {prognostico:.2f}")
        return prognostico

# Configurar Flask-Assets
assets = Environment(app)
scss = Bundle('scss/style.scss', filters='pyscss', output='css/style.css')
assets.register('scss_all', scss)

# Criar uma rota para build dos assets
@app.route('/build-assets')
def build_assets():
    # Build os assets scss_all
    assets['scss_all'].build()
    return 'Assets built successfully.'

if __name__ == '__main__':
    app.run(debug=True)
