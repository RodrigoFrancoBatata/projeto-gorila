from flask import Flask, render_template, request, redirect, send_file
import json
import os
import csv
from collections import Counter

app = Flask(__name__)

# Utilitários
def carregar_treinos():
    with open('treinos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_historico():
    if os.path.exists('historico.json'):
        with open('historico.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Home
@app.route('/')
def index():
    treinos = carregar_treinos()
    return render_template('index.html', treinos=treinos)

# Página de treino por dia
@app.route('/treino/<dia>', methods=['GET', 'POST'])
def treino(dia):
    treinos = carregar_treinos().get(dia, [])
    if request.method == 'POST':
        historico = carregar_historico()
        concluido = request.form.getlist('concluido')
        for i in concluido:
            exercicio = treinos[int(i)]
            historico.append({
                'dia': dia,
                'exercicio': exercicio['exercicio']
            })
        with open('historico.json', 'w', encoding='utf-8') as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
        return redirect('/')
    return render_template('treino.html', dia=dia, treinos=treinos)

# Histórico com filtro
@app.route('/historico')
def historico():
    historico = carregar_historico()
    dia_filtro = request.args.get('dia')
    if dia_filtro:
        historico = [h for h in historico if h['dia'] == dia_filtro]
    dias_unicos = sorted(set(h['dia'] for h in carregar_historico()))
    return render_template('historico.html', historico=historico, dias=dias_unicos, dia_filtro=dia_filtro)

# Download CSV
@app.route('/historico/download')
def download_historico():
    historico = carregar_historico()
    with open('historico_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['dia', 'exercicio'])
        writer.writeheader()
        writer.writerows(historico)
    return send_file('historico_export.csv', as_attachment=True)

# Página de progresso
@app.route('/progresso')
def progresso():
    historico = carregar_historico()
    total = len(historico)
    dados_por_dia = Counter([h['dia'] for h in historico])
    dados_por_exercicio = Counter([h['exercicio'] for h in historico])
    dias_unicos = list(set(h['dia'] for h in historico))
    return render_template('progresso.html',
                           total=total,
                           dias_unicos=dias_unicos,
                           dados_por_dia=dados_por_dia,
                           dados_por_exercicio=dados_por_exercicio)

if __name__ == '__main__':
    app.run(debug=True)

