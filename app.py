from flask import Flask, render_template, request, send_file, redirect, url_for
from fpdf import FPDF
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

# CONFIGURAÇÕES TÉCNICAS
URL_PLANILHA = "https://script.google.com/macros/s/AKfycbyappk_wCjT8uP_ZX_Bsm6b52oBQz8RgcnjMCa1-T6ya_Au0pqVetf3OId58cUelOLg/exec"
SENHA_ADMIN = "unisafe2026" # Mude sua senha aqui!

# O Dicionário começa com os que você já tem
CONFIG_CLIENTES = {
    "Moveis_Conforto": ["Marcenaria", "Pintura", "Vendas", "Administrativo"],
    "GBK_Power": ["Manutencao", "Operacional", "Engenharia"],
    "Intertek": ["Inspecao", "Laboratorio", "Campo"]
}

QUESTOES = [
    {"id": 1, "texto": "Voce sente que precisa correr ou trabalhar muito rapido?", "dim": "Demanda"},
    # ... (Mantenha as 30 questões aqui exatamente como estão no seu arquivo atual)
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "As vezes"), ("3", "Sempre")]

# --- ROTA DO FORMULÁRIO (PARA O CLIENTE) ---
@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'UNISAFE')
    setores = CONFIG_CLIENTES.get(cliente_id, ["Geral", "Administrativo"])
    nome_exibicao = cliente_id.replace("_", " ")
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=nome_exibicao)

# --- ROTA DO PAINEL ADMIN (SÓ PARA VOCÊ) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    mensagem = ""
    link_gerado = ""
    
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == SENHA_ADMIN:
            novo_cliente = request.form.get('nome_cliente').replace(" ", "_")
            novos_setores = request.form.get('setores').split(",") # Separa por vírgula
            
            # Adiciona ao dicionário temporário
            CONFIG_CLIENTES[novo_cliente] = [s.strip() for s in novos_setores]
            
            link_gerado = f"{request.url_root}?cliente={novo_cliente}"
            mensagem = f"Cliente {novo_cliente} cadastrado com sucesso!"
        else:
            mensagem = "Senha incorreta!"

    return render_template('admin.html', mensagem=mensagem, link=link_gerado, clientes=CONFIG_CLIENTES)

# --- ROTA DE ENVIO (PDF + GOOGLE SHEETS) ---
@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    setor = request.form.get('setor')
    respostas = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTOES}
    total = sum(int(v) for v in respostas.values() if v)
    
    # Envio Planilha
    try:
        requests.post(URL_PLANILHA, data=json.dumps({"cliente": cliente_final, "setor": setor, "pontuacao": total}), timeout=5)
    except: pass

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"LAUDO SST - {cliente_final}", ln=True, align='C')
    pdf.output("laudo.pdf")
    return send_file("laudo.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
