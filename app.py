from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')

DATA_PATH = 'data/treinos.json'
HISTORICO_PATH = 'data/historico.json'
IMAGENS_PATH = os.path.join('static', 'imagens')

def carregar_treinos():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_treinos(treinos):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(treinos, f, indent=2, ensure_ascii=False)

def carregar_historico():
    if not os.path.exists(HISTORICO_PATH):
        return []
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
    if request.method == 'POST':
        index = int(request.form['index'])
        if 'nova_carga' in request.form:
            treinos[dia][index]['carga'] = request.form['nova_carga']
        elif 'concluido' in request.form:
            treinos[dia][index]['concluido'] = 'concluido' in request.form
            if treinos[dia][index]['concluido']:
                historico = carregar_historico()
                historico.append({
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'dia': dia,
                    'exercicio': treinos[dia][index]['exercicio'],
                    'carga': treinos[dia][index]['carga']
                })
                salvar_historico(historico)
        salvar_treinos(treinos)
        return redirect(url_for('treino', dia=dia))

    exercicios = treinos.get(dia, [])
    return render_template('treino.html', dia=dia, exercicios=exercicios)

@app.route('/adicionar/<dia>', methods=['POST'])
def adicionar(dia):
    treinos = carregar_treinos()
    imagem = request.files.get('imagem')
    nome_arquivo = ''

    if imagem and imagem.filename:
        nome_arquivo = datetime.now().strftime('%Y%m%d%H%M%S_') + secure_filename(imagem.filename)
        os.makedirs(IMAGENS_PATH, exist_ok=True)
        imagem.save(os.path.join(IMAGENS_PATH, nome_arquivo))

    novo = {
        'exercicio': request.form['exercicio'],
        'imagem': nome_arquivo,
        'series': request.form['series'],
        'carga': request.form['carga'],
        'obs': request.form['obs'],
        'concluido': False
    }

    if dia not in treinos:
        treinos[dia] = []

    treinos[dia].append(novo)
    salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/excluir/<dia>/<int:index>', methods=['POST'])
def excluir(dia, index):
    treinos = carregar_treinos()
    if dia in treinos and 0 <= index < len(treinos[dia]):
        del treinos[dia][index]
        salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/historico')
def historico():
    historico = carregar_historico()
    return render_template('historico.html', historico=historico)

@app.route('/progresso')
def progresso():
    historico = carregar_historico()
    progresso_dict = {}
    for item in historico:
        dia = item['dia']
        if dia not in progresso_dict:
            progresso_dict[dia] = []
        progresso_dict[dia].append({
            'exercicio': item['exercicio'],
            'data': item['data'],
            'carga': item['carga']
        })
    return render_template('progresso.html', progresso=progresso_dict)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
