# app.py (completo e corrigido)
from flask import Flask, render_template, request, redirect, send_file
import os
import json
import csv
from datetime import datetime

app = Flask(__name__)

DIAS = ["Treino A", "Treino B", "Treino C"]

# Função para carregar os exercícios do dia
def carregar_exercicios(dia):
    caminho = f"dados/{dia.replace(' ', '_')}.json"
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            return json.load(f)
    return []

# Função para salvar os exercícios do dia
def salvar_exercicios(dia, lista):
    with open(f"dados/{dia.replace(' ', '_')}.json", "w") as f:
        json.dump(lista, f, indent=2)

# Função para salvar histórico
def salvar_historico(dia, lista):
    hoje = datetime.now().strftime("%Y-%m-%d")
    historico = {"data": hoje, "exercicios": lista}
    caminho = f"historico/historico_{dia.replace(' ', '_').lower()}.json"
    todos = []
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            todos = json.load(f)
    todos.append(historico)
    with open(caminho, "w") as f:
        json.dump(todos, f, indent=2)

@app.route("/")
def home():
    return render_template("index.html", dias=DIAS)

@app.route("/treino/<dia>", methods=["GET", "POST"])
def treino(dia):
    lista = carregar_exercicios(dia)
    if request.method == "POST":
        if "nova_carga" in request.form:
            index = int(request.form["index"])
            lista[index]["carga"] = request.form["nova_carga"]
        elif "concluido" in request.form:
            index = int(request.form["index"])
            lista[index]["concluido"] = not lista[index].get("concluido", False)
        salvar_exercicios(dia, lista)
        salvar_historico(dia, lista)
    return render_template("treino.html", dia=dia, exercicios=lista)

@app.route("/adicionar/<dia>", methods=["POST"])
def adicionar(dia):
    lista = carregar_exercicios(dia)
    novo = {
        "exercicio": request.form["exercicio"],
        "imagem": request.files["imagem"].filename,
        "series": request.form["series"],
        "carga": request.form["carga"],
        "obs": request.form["obs"],
        "concluido": False
    }
    # Salvar imagem
    imagem = request.files["imagem"]
    if imagem:
        imagem.save(os.path.join("static/imagens", imagem.filename))
    lista.append(novo)
    salvar_exercicios(dia, lista)
    return redirect(f"/treino/{dia}")

@app.route("/historico")
def historico():
    historicos = {}
    for dia in DIAS:
        caminho = f"historico/historico_{dia.replace(' ', '_').lower()}.json"
        if os.path.exists(caminho):
            with open(caminho, "r") as f:
                historicos[dia] = json.load(f)
        else:
            historicos[dia] = []
    return render_template("historico.html", historicos=historicos)

@app.route("/historico/download")
def download_historico():
    caminho_csv = "historico/historico_exportado.csv"
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Treino", "Exercício", "Séries", "Carga", "Obs"])
        for dia in DIAS:
            caminho = f"historico/historico_{dia.replace(' ', '_').lower()}.json"
            if os.path.exists(caminho):
                with open(caminho, "r") as f_json:
                    registros = json.load(f_json)
                    for r in registros:
                        data = r["data"]
                        for e in r["exercicios"]:
                            writer.writerow([data, dia, e["exercicio"], e["series"], e["carga"], e["obs"]])
    return send_file(caminho_csv, as_attachment=True)

if __name__ == "__main__":
    os.makedirs("dados", exist_ok=True)
    os.makedirs("historico", exist_ok=True)
    os.makedirs("static/imagens", exist_ok=True)
    app.run(debug=True)
