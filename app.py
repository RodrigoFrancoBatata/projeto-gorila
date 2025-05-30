from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')

DATA_PATH = 'data/treinos.json'
HISTORICO_PATH = 'data/historico.json'
IMAGENS_PATH = 'static/imagens'

# ---------- Funções utilitárias ----------
def carregar_treinos():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_treinos(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def salvar_historico(item):
    historico = []
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    historico.append(item)
    with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

# ---------- Rotas ----------
@app.route('/')
def index():
    treinos = carregar_treinos()
    return render_template('index.html', treinos=treinos)

@app.route('/treino/<dia>', methods=['GET', 'POST'])
def treino(dia):
    treinos = carregar_treinos()
    if request.method == 'POST':
        index = int(request.form['index']) if 'index' in request.form else None
        if 'nova_carga' in request.form:
            nova_carga = request.form['nova_carga']
            if nova_carga:
                treinos[dia][index]['carga'] = nova_carga
                salvar_historico({
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'dia': dia,
                    'exercicio': treinos[dia][index]['exercicio'],
                    'carga': nova_carga
                })
        elif 'concluido' in request.form:
            treinos[dia][index]['concluido'] = not treinos[dia][index].get('concluido', False)
        salvar_treinos(treinos)
    return render_template('treino.html', dia=dia, exercicios=treinos.get(dia, []))

@app.route('/adicionar/<dia>', methods=['POST'])
def adicionar(dia):
    treinos = carregar_treinos()
    exercicio = request.form['exercicio']
    imagem = request.files['imagem']
    series = request.form['series']
    carga = request.form['carga']
    obs = request.form['obs']

    if imagem:
        nome_arquivo = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{imagem.filename}")
        imagem.save(os.path.join(IMAGENS_PATH, nome_arquivo))
    else:
        nome_arquivo = ''

    novo_exercicio = {
        'exercicio': exercicio,
        'imagem': nome_arquivo,
        'series': series,
        'carga': carga,
        'obs': obs,
        'concluido': False
    }
    treinos.setdefault(dia, []).append(novo_exercicio)
    salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/excluir/<dia>/<int:index>', methods=['POST'])
def excluir(dia, index):
    treinos = carregar_treinos()
    if dia in treinos and index < len(treinos[dia]):
        del treinos[dia][index]
        salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/historico')
def historico():
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    else:
        historico = []
    return render_template('historico.html', historico=historico)

@app.route('/historico/download')
def download():
    import csv
    from flask import make_response
    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    csv_content = 'Data,Dia,Exercício,Carga\n'
    for item in dados:
        csv_content += f"{item['data']},{item['dia']},{item['exercicio']},{item['carga']}\n"

    response = make_response(csv_content)
    response.headers['Content-Disposition'] = 'attachment; filename=historico.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/progresso')
def progresso():
    if not os.path.exists(HISTORICO_PATH):
        return render_template('progresso.html', progresso={})

    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        historico = json.load(f)

    progresso_dict = {}
    for item in historico:
        chave = (item['dia'], item['exercicio'])
        progresso_dict.setdefault(chave, []).append({
            'data': item['data'],
            'carga': item['carga']
        })
    return render_template('progresso.html', progresso=progresso_dict)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


