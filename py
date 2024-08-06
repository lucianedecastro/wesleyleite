from flask import Flask, render_template, request, jsonify
import datetime
import json

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
  # Aqui você deve implementar a lógica para gerar o prognóstico
  # usando os dados de 'atleta'
  # ... 
  # Retornar o prognóstico como string
  return jsonify({"prognostico": "Prognóstico: ... "})

if __name__ == "__main__":
  app.run(debug=True)