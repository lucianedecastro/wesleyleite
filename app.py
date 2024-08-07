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
            print("Impacto inválido. Digite um número entre 1 e 5.")

    def treinar_modelo_prognostico(self):
        """Treina um modelo de regressão linear para prever a próxima nota."""

        # Verifica se há dados suficientes para treinar o modelo
        if self.notas_etapas.count(None) > 2:
            print("Precisa de pelo menos 2 notas de etapas para treinar o modelo.")
            return

        # Prepara os dados para treinamento
        X = []  # Lista para armazenar as features
        y = np.array([nota for nota in self.notas_etapas if nota is not None])  # Notas

        # Obter nomes de variáveis extras
        self.features_extras_names = list(self.variaveis_extras.keys())

        # Cria o OneHotEncoder aqui, apenas uma vez
        if self.encoder is None and self.variaveis_extras:
            self.encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
            # Aplica o fit_transform no encoder para criar o esquema de codificação
            features_extras = self.encoder.fit_transform([[valor for valor in self.variaveis_extras.values()]]).toarray() 

        for i, (nota, colocacao) in enumerate(zip(self.notas_etapas, self.colocacoes_etapas)):
            if nota is not None:
                # Extrai informações de treino
                treinos_mar_etapa = len([data for data in self.treinos_mar if data == i + 1])
                treinos_academia_etapa = len([data for data in self.treinos_academia if data == i + 1])

                # Cria a lista de features para cada etapa
                features = [
                    colocacao,
                    treinos_mar_etapa,
                    treinos_academia_etapa,
                    self.treino_mar_nota,
                    self.treino_academia_nota
                ]

                # Adiciona as features para a variável extra (usando One-Hot Encoding)
                if self.variaveis_extras:
                    features_extras = self.encoder.transform([[valor for valor in self.variaveis_extras.values()]]).toarray()[0]
                    features = np.concatenate((features, features_extras), axis=0)  # Concatenar na linha (axis=0)
                else:
                    features = np.array(features).reshape(1, -1)

                X.append(features)

        # Transforma a lista de features 'X' em uma matriz NumPy 2D
        X = np.array(X)

        # Normaliza os dados para melhorar o desempenho do modelo
        # Aplique o OneHotEncoder primeiro
        if self.encoder is not None:
            X[:, 3:] = self.encoder.transform(X[:, 3:])

        # Depois, aplique o StandardScaler APENAS nas features das etapas
        X[:, :3] = self.scaler.fit_transform(X[:, :3]) # Aplica o StandardScaler nas 3 primeiras colunas

        # Cria o modelo de regressão linear
        self.modelo_prognostico = LinearRegression()
        self.modelo_prognostico.fit(X, y)

    def obter_prognostico(self):
        """Calcula o prognóstico da próxima nota."""

        # Verifica se o modelo está treinado
        if self.modelo_prognostico is None:
            print("O modelo de prognóstico ainda não foi treinado.")
            return

        # Prepara os dados para a previsão
        ultima_etapa = len(self.notas_etapas)

        # Cria a lista de features para a próxima etapa
        features = [
            self.colocacoes_etapas[ultima_etapa - 1] if ultima_etapa > 0 else 0,  # Última colocação
            len([data for data in self.treinos_mar if data == ultima_etapa]),
            len([data for data in self.treinos_academia if data == ultima_etapa]),
            self.treino_mar_nota,
            self.treino_academia_nota
        ]

        # Adiciona as features para a variável extra (usando One-Hot Encoding)
        if self.variaveis_extras:
            features_extras = self.encoder.transform([[valor for valor in self.variaveis_extras.values()]]).toarray()[0]
            features = np.concatenate((features, features_extras), axis=0)  # Concatenar na linha (axis=0)

        # Normaliza as features
        features = self.scaler.transform(features)

        # Utiliza o modelo para prever a próxima nota
        prognostico = self.modelo_prognostico.predict(features)[0]
        
        # Formata e exibe o prognóstico
        print(f"Prognóstico da próxima nota: {prognostico:.2f}")
        return prognostico

def main():
    atleta = Atleta("Wesley Leite")

    while True:
        print("\nMenu:")
        print("1. Registrar treino no mar")
        print("2. Registrar treino na academia")
        print("3. Adicionar informações da etapa:") # Menu 3 modificado
        print("4. Obter prognóstico") # Menu 4 reajustado
        print("5. Sair") # Menu 5 reajustado

        opcao = input("Digite a opção desejada: ")

        if opcao == "1":
            atleta.registrar_treino_mar()
        elif opcao == "2":
            atleta.registrar_treino_academia()
        elif opcao == "3":
            while True:
                etapa = input("Digite o número da etapa (1-4) ou 'sair' para voltar ao menu: ")
                if etapa == "sair": # Corrigido para comparar com a string 'sair'
                    break
                etapa = int(etapa) # Converter para inteiro após a comparação
                nota = float(input("Digite a nota: "))
                colocacao = input("Digite a colocação: ") # Recebe a colocação como string
                if colocacao.isdigit() and int(colocacao) >= 1: # Valida se a colocação é um número válido
                    colocacao = int(colocacao) # Converte para inteiro após a validação
                    atleta.adicionar_nota_etapa(etapa, nota, colocacao)
                else:
                    print("Colocação inválida. Digite um número inteiro maior ou igual a 1.")
                while True:
                    adicionar_variavel = input("Deseja adicionar variável extra? (sim/não): ")
                    if adicionar_variavel.lower() == "sim":
                        nome = input("Digite o nome da variável extra: ")
                        impacto = int(input("Digite o impacto (1-5): "))
                        atleta.adicionar_variavel_extra(nome, impacto)
                    elif adicionar_variavel.lower() == "não":
                        break
                    else:
                        print("Opção inválida. Digite 'sim' ou 'não'.")
        elif opcao == "4":
            atleta.obter_prognostico()
        elif opcao == "5":
            break
        else:
            print("Opção inválida!")

# Criar o ambiente Flask-Assets
assets = Environment(app)
css = Bundle('style.css', output='build/style.css')
assets.register('all_css', css)

@app.cli.command('build')
def build():
    assets.build('all_css')

if __name__ == "__main__":
    app.run(debug=True)