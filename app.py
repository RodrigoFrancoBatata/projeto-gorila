from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
from datetime import datetime
import csv

app = Flask(__name__, static_url_path='/static', static_folder='static')

TREINO_PATH = 'data/treinos.json'
HISTORICO_PATH = 'data/historico.json'


def carregar_treinos():
    with open(TREINO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_treinos(dados):
    with open(TREINO_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def carregar_historico():
    if not os.path.exists(HISTORICO_PATH):
        return []
    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_historico(dados):
    with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    treinos = carregar_treinos()
    return render_template('index.html', treinos=treinos)


@app.route('/treino/<dia>', methods=['GET', 'POST'])
def treino(dia):
    treinos = carregar_treinos()
    exercicios = treinos.get(dia, [])

    if request.method == 'POST':
        if 'index' in request.form:
            i = int(request.form['index'])

            # Editar carga
            if 'nova_carga' in request.form and request.form['nova_carga']:
                exercicios[i]['carga'] = request.form['nova_carga']

            # Marcar como concluído
            if 'concluido' in request.form:
                exercicios[i]['concluido'] = True
            else:
                exercicios[i]['concluido'] = False

            treinos[dia] = exercicios
            salvar_treinos(treinos)

            # Histórico
            historico = carregar_historico()
            historico.append({
                'data': datetime.now().strftime('%d/%m/%Y'),
                'dia': dia,
                'exercicio': exercicios[i]['exercicio'],
                'carga': exercicios[i]['carga']
            })
            salvar_historico(historico)

        return redirect(url_for('treino', dia=dia))

    return render_template('treino.html', dia=dia, exercicios=exercicios)


@app.route('/adicionar/<dia>', methods=['POST'])
def adicionar(dia):
    treinos = carregar_treinos()
    if dia not in treinos:
        treinos[dia] = []

    treinos[dia].append({
        'exercicio': request.form['exercicio'],
        'imagem': request.form['imagem'],
        'series': request.form['series'],
        'carga': request.form['carga'],
        'obs': request.form['obs'],
        'concluido': False
    })
    salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))


@app.route('/excluir/<dia>/<int:i>', methods=['POST'])
def excluir(dia, i):
    treinos = carregar_treinos()
    if dia in treinos and 0 <= i < len(treinos[dia]):
        del treinos[dia][i]
        salvar_treinos(treinos)
    return redirect(url_for('treino', dia=dia))


@app.route('/historico')
def historico():
    dados = carregar_historico()
    return render_template('historico.html', historico=dados)


@app.route('/historico/download')
def download_historico():
    historico = carregar_historico()
    caminho_csv = 'data/historico.csv'
    with open(caminho_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['data', 'dia', 'exercicio', 'carga'])
        writer.writeheader()
        for linha in historico:
            writer.writerow(linha)
    return send_file(caminho_csv, as_attachment=True)


@app.route('/progresso')
def progresso():
    historico = carregar_historico()
    progresso_dict = {}
    for item in historico:
        nome = item['exercicio']
        if nome not in progresso_dict:
            progresso_dict[nome] = []
        progresso_dict[nome].append({
            'data': item['data'],
            'carga': item['carga']
        })
    return render_template('progresso.html', progresso=progresso_dict)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)





