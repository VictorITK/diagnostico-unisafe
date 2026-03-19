from flask import Flask, render_template, request, send_file, redirect, url_for, session
from fpdf import FPDF
import sqlite3
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "unisafe_chave_mestra" # Segurança para o login

URL_PLANILHA = "https://script.google.com/macros/s/AKfycbyappk_wCjT8uP_ZX_Bsm6b52oBQz8RgcnjMCa1-T6ya_Au0pqVetf3OId58cUelOLg/exec"
SENHA_MESTRA = "unisafe2026"

# --- FUNÇÕES DO BANCO DE DATOS ---
def init_db():
    conn = sqlite3.connect('unisafe.db')
    cursor = conn.cursor()
    # Tabela de Empresas
    cursor.execute('''CREATE TABLE IF NOT EXISTS empresas 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, setores TEXT)''')
    conn.commit()
    conn.close()

# Inicializa o banco ao ligar o site
init_db()

QUESTOES = [
    {"id": 1, "texto": "Voce sente que precisa correr ou trabalhar muito rapido para dar conta de tudo?", "dim": "Demanda"},
    # ... (Mantenha todas as suas 30 questões aqui exatamente como no código anterior)
    # Por favor, Victor, garanta que todas as 30 questões estejam aqui dentro quando for colar!
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "As vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

# --- ROTAS DO SISTEMA ---

@app.route('/')
def index():
    cliente_nome = request.args.get('cliente', 'UNISAFE')
    
    # Busca setores no Banco de Dados
    conn = sqlite3.connect('unisafe.db')
    cursor = conn.cursor()
    cursor.execute("SELECT setores FROM empresas WHERE nome = ?", (cliente_nome,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        setores = resultado[0].split(",")
    else:
        setores = ["Geral", "Administrativo", "Operacional"]

    nome_exibicao = cliente_nome.replace("_", " ")
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=nome_exibicao)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('senha') == SENHA_MESTRA:
            session['logado'] = True
            return redirect(url_for('admin'))
    return '''<form method="post">Senha: <input type="password" name="senha"><button>Entrar</button></form>'''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('unisafe.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form.get('nome_cliente').strip().replace(" ", "_")
        setores = request.form.get('setores').strip()
        cursor.execute("INSERT INTO empresas (nome, setores) VALUES (?, ?)", (nome, setores))
        conn.commit()

    cursor.execute("SELECT * FROM empresas")
    empresas = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', empresas=empresas, host=request.host_url)

@app.route('/deletar/<int:id>')
def deletar(id):
    if session.get('logado'):
        conn = sqlite3.connect('unisafe.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empresas WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    setor = request.form.get('setor')
    respostas = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTOES}
    total = sum(int(v) for v in respostas.values() if v)
    status = "ALERTA" if total >= 60 else "OK"

    try:
        requests.post(URL_PLANILHA, data=json.dumps({"cliente": cliente_final, "setor": setor, "pontuacao": total, "status": status}), timeout=5)
    except: pass

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"LAUDO PSICOSSOCIAL - {cliente_final}", ln=True, align='C')
    pdf.output("laudo.pdf")
    return send_file("laudo.pdf", as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
