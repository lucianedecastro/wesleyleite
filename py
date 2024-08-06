from flask import Flask, render_template, request, jsonify
import datetime
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder

app = Flask(__name__, template_folder='templates', static_folder='static')

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
try:
  with open("historico_atleta.json", "r") as f:
    atleta = json.load(f)
except FileNotFoundError:
  pass

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
  atleta["treinos_mar"].append(data)
  gravar_historico()
  return jsonify({"message": "Treino no mar registrado com sucesso."})

@app.route('/registrar-treino-academia', methods=['POST'])
def registrar_treino_academia():
  data = request.form.get("data")
  atleta["treinos_academia"].append(data)
  gravar_historico()
  return jsonify({"message": "Treino na academia registrado com sucesso."})

@app.route('/adicionar-informacoes-etapa', methods=['POST'])
def adicionar_informacoes_etapa():
  etapa = int(request.form.get("etapa"))
  nota = float(request.form.get("nota"))
  colocacao = int(request.form.get("colocacao"))

  atleta["notas_etapas"][etapa - 1] = nota
  atleta["colocacoes_etapas"][etapa - 1] = colocacao
  gravar_historico()
  return jsonify({"message": "Informações da etapa registradas com sucesso."})

@app.route('/obter-prognostico', methods=['POST'])
def obter_prognostico():
  # Obter dados do atleta
  notas = atleta["notas_etapas"]
  colocacoes = atleta["colocacoes_etapas"]
  variaveis_extras = atleta["variaveis_extras"]
  impactos_extras = atleta["impactos_extras"]

  # Criar o modelo de prognóstico
  modelo = criar_modelo_prognostico(notas, colocacoes, variaveis_extras, impactos_extras)

  # Gerar o prognóstico
  prognostico = modelo.predict([[
    colocacoes[-1] if colocacoes[-1] is not None else 0, # última colocação
    len(atleta["treinos_mar"]),
    len(atleta["treinos_academia"]),
    atleta["treino_mar_nota"],
    atleta["treino_academia_nota"]
  ]])[0]

  return jsonify({"prognostico": f"Prognóstico: {prognostico:.2f}"})

# Criar o modelo de prognóstico
def criar_modelo_prognostico(notas, colocacoes, variaveis_extras, impactos_extras):
  X = []
  y = np.array([nota for nota in notas if nota is not None])

  if variaveis_extras:
    encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
    features_extras = encoder.fit_transform([[valor for valor in variaveis_extras.values()]]).toarray()[0]

  for i, (nota, colocacao) in enumerate(zip(notas, colocacoes)):
    if nota is not None:
      features = [
        colocacao,
        len(atleta["treinos_mar"]),
        len(atleta["treinos_academia"]),
        atleta["treino_mar_nota"],
        atleta["treino_academia_nota"]
      ]

      if variaveis_extras:
        features = np.concatenate((features, features_extras), axis=0)
      else:
        features = np.array(features).reshape(1, -1)

      X.append(features)

  X = np.array(X)

  # Aplique o OneHotEncoder primeiro
  if variaveis_extras:
    X[:, 3:] = encoder.transform(X[:, 3:]).toarray() 

  # Depois, aplique o StandardScaler
  X = StandardScaler().fit_transform(X) 

  modelo = LinearRegression()
  modelo.fit(X, y)

  return modelo

if __name__ == "__main__":
  app.run(debug=True)