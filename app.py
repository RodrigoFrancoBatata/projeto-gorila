from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')
DATA_PATH = 'data/treinos.json'
HISTORICO_PATH = 'data/historico.json'

def carregar_treinos():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_treinos(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def carregar_historico():
    if not os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_historico(historico):
    with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    treinos = carregar_treinos()
    return render_template('index.html', treinos=treinos)

@app.route('/treino/<dia>', methods=['GET', 'POST'])
def treino(dia):
    treinos = carregar_treinos()
    historico = carregar_historico()

    if request.method == 'POST':
        index = int(request.form['index'])

        if 'nova_carga' in request.form:
            nova_carga = request.form['nova_carga']
            treinos[dia][index]['carga'] = nova_carga

        elif 'concluido' in request.form or 'index' in request.form:
            foi_concluido = 'concluido' in request.form
            treinos[dia][index]['concluido'] = foi_concluido

            if foi_concluido:
                registro = {
                    "data": datetime.now().strftime("%Y-%m-%d"),
                    "hora": datetime.now().strftime("%H:%M"),
                    "dia": dia,
                    "exercicio": treinos[dia][index]['exercicio']
                }
                if registro not in historico:
                    historico.append(registro)
                    salvar_historico(historico)

        salvar_treinos(treinos)
        return redirect(url_for('treino', dia=dia))

    return render_template('treino.html', dia=dia, exercicios=treinos.get(dia, []))

@app.route('/adicionar/<dia>', methods=['POST'])
def adicionar_exercicio(dia):
    treinos = carregar_treinos()
    novo = {
        "exercicio": request.form['exercicio'],
        "imagem": request.form['imagem'],
        "series": request.form['series'],
        "carga": request.form['carga'],
        "obs": request.form['obs'],
        "concluido": False
    }
    treinos[dia].append(novo)
    salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/historico')
def historico():
    registros = carregar_historico()
    registros_ordenados = sorted(registros, key=lambda x: (x["data"], x["hora"]), reverse=True)
    return render_template('historico.html', registros=registros_ordenados)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

