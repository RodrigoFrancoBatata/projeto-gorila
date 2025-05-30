from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
DATA_PATH = 'data/treinos.json'

def carregar_treinos():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_treinos(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    treinos = carregar_treinos()
    return render_template('index.html', treinos=treinos)

@app.route('/treino/<dia>', methods=['GET', 'POST'])
def treino(dia):
    treinos = carregar_treinos()

    if request.method == 'POST':
        index = int(request.form['index'])
        if 'nova_carga' in request.form:
            nova_carga = request.form['nova_carga']
            treinos[dia][index]['carga'] = nova_carga
        elif 'concluido' in request.form:
            treinos[dia][index]['concluido'] = request.form.get('concluido') == 'on'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

