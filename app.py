from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
import csv
from datetime import datetime

app = Flask(__name__, static_url_path='/static', static_folder='static')

DATA_PATH = 'data/treinos.json'
HISTORICO_PATH = 'data/historico.json'

def carregar_treinos():
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
    exercicios = treinos.get(dia, [])

    if request.method == 'POST':
        index = int(request.form['index'])
        if 'nova_carga' in request.form:
            nova_carga = request.form['nova_carga']
            exercicios[index]['carga'] = nova_carga
        elif 'concluido' in request.form:
            exercicios[index]['concluido'] = True
            historico = carregar_historico()
            historico.append({
                'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'dia': dia,
                'exercicio': exercicios[index]['exercicio'],
                'carga': exercicios[index]['carga']
            })
            salvar_historico(historico)
        else:
            exercicios[index]['concluido'] = False
        salvar_treinos(treinos)

    return render_template('treino.html', dia=dia, exercicios=exercicios)

@app.route('/adicionar/<dia>', methods=['POST'])
def adicionar_exercicio(dia):
    treinos = carregar_treinos()
    novo = {
        'exercicio': request.form['exercicio'],
        'imagem': request.form['imagem'],
        'series': request.form['series'],
        'carga': request.form['carga'],
        'obs': request.form['obs'],
        'concluido': False
    }
    treinos.setdefault(dia, []).append(novo)
    salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/excluir/<dia>/<int:index>', methods=['POST'])
def excluir(dia, index):
    treinos = carregar_treinos()
    if dia in treinos and 0 <= index < len(treinos[dia]):
        treinos[dia].pop(index)
        salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))

@app.route('/historico')
def historico():
    dados = carregar_historico()
    return render_template('historico.html', historico=dados)

@app.route('/historico/download')
def download():
    historico = carregar_historico()
    caminho = 'historico_export.csv'
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Data', 'Dia', 'Exercicio', 'Carga'])
        for item in historico:
            writer.writerow([item['data'], item['dia'], item['exercicio'], item['carga']])
    return send_file(caminho, as_attachment=True)

@app.route('/progresso')
def progresso():
    treinos = carregar_treinos()
    progresso_dict = {}

    for dia, lista in treinos.items():
        total = len(lista)
        concluidos = sum(1 for e in lista if e.get('concluido'))
        porcentagem = round((concluidos / total) * 100) if total > 0 else 0
        progresso_dict[dia] = {
            'total': total,
            'concluidos': concluidos,
            'porcentagem': porcentagem
        }

    return render_template('progresso.html', progresso=progresso_dict)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)


