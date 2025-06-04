from flask import Flask, render_template, request, redirect, send_file
import os
import json
import csv
from datetime import datetime

app = Flask(__name__)

DIAS = ["Treino A", "Treino B", "Treino C"]

def carregar_exercicios(dia):
    caminho = f"data/treinos.json"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados.get(dia, [])
    return []

def salvar_exercicios(dia, lista):
    caminho = f"data/treinos.json"
    dados = {}
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    dados[dia] = lista
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def salvar_historico(dia, lista):
    hoje = datetime.now().strftime("%Y-%m-%d")
    caminho = "data/historico.json"
    historico = {}
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            historico = json.load(f)
    if dia not in historico:
        historico[dia] = []
    historico[dia].append({"data": hoje, "exercicios": lista})
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

@app.route("/")
def home():
    return render_template("index.html", dias=DIAS)

@app.route("/treino/<dia>", methods=["GET", "POST"])
def treino(dia):
    lista = carregar_exercicios(dia)

    if request.method == "POST":
        index = int(request.form["index"])

        # Atualiza carga
        if "nova_carga" in request.form:
            lista[index]["carga"] = request.form["nova_carga"]

        # Atualiza imagem
        if "nova_imagem" in request.files:
            nova_imagem = request.files["nova_imagem"]
            if nova_imagem and nova_imagem.filename:
                nome_arquivo = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + nova_imagem.filename.replace(" ", "_")
                caminho = os.path.join("static/imagens", nome_arquivo)
                nova_imagem.save(caminho)
                lista[index]["imagem"] = nome_arquivo

        # Alterna concluído
        if "concluido" in request.form:
            lista[index]["concluido"] = not lista[index].get("concluido", False)

        salvar_exercicios(dia, lista)
        salvar_historico(dia, lista)

    return render_template("treino.html", dia=dia, exercicios=lista)

@app.route("/adicionar/<dia>", methods=["POST"])
def adicionar(dia):
    lista = carregar_exercicios(dia)
    imagem = request.files["imagem"]
    nome_arquivo = ""

    if imagem and imagem.filename:
        nome_arquivo = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + imagem.filename.replace(" ", "_")
        imagem.save(os.path.join("static/imagens", nome_arquivo))

    novo = {
        "exercicio": request.form["exercicio"],
        "imagem": nome_arquivo,
        "series": request.form["series"],
        "carga": request.form["carga"],
        "obs": request.form.get("obs", ""),
        "concluido": False
    }

    lista.append(novo)
    salvar_exercicios(dia, lista)
    return redirect(f"/treino/{dia}")

@app.route("/historico")
def historico():
    historicos = {}
    caminho = "data/historico.json"
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            historicos = json.load(f)
    return render_template("historico.html", historicos=historicos)

@app.route("/historico/download")
def download_historico():
    caminho_csv = "data/historico_exportado.csv"
    with open(caminho_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Treino", "Exercício", "Séries", "Carga", "Obs"])
        if os.path.exists("data/historico.json"):
            with open("data/historico.json", "r", encoding="utf-8") as f_json:
                registros = json.load(f_json)
                for dia, entradas in registros.items():
                    for r in entradas:
                        data = r["data"]
                        for e in r["exercicios"]:
                            writer.writerow([data, dia, e["exercicio"], e["series"], e["carga"], e["obs"]])
    return send_file(caminho_csv, as_attachment=True)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("static/imagens", exist_ok=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)

