from flask import Flask, render_template, request, send_file, redirect, url_for
from fpdf import FPDF
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)

# CONFIGURAÇÕES TÉCNICAS
URL_PLANILHA = "https://script.google.com/macros/s/AKfycbyappk_wCjT8uP_ZX_Bsm6b52oBQz8RgcnjMCa1-T6ya_Au0pqVetf3OId58cUelOLg/exec"
SENHA_ADMIN = "unisafe2026"

# DICIONÁRIO DE CLIENTES (Pode ser editado via Painel Admin durante a sessão)
CONFIG_CLIENTES = {
    "Moveis_Conforto": ["Marcenaria", "Pintura", "Vendas", "Administrativo"],
    "GBK_Power": ["Manutencao", "Operacional", "Engenharia"],
    "Intertek": ["Inspecao", "Laboratorio", "Campo"]
}

QUESTOES = [
    {"id": 1, "texto": "Voce sente que precisa correr ou trabalhar muito rapido para dar conta de tudo?", "dim": "Demanda"},
    {"id": 2, "texto": "No final do dia, voce se sente muito cansado ou 'esgotado' mentalmente pelo servico?", "dim": "Demanda"},
    {"id": 3, "texto": "A chefia te entrega tarefas com prazos que sao impossiveis de cumprir?", "dim": "Demanda"},
    {"id": 4, "texto": "Voce precisa deixar coisas importantes sem fazer porque tem trabalho demais acumulado?", "dim": "Demanda"},
    {"id": 5, "texto": "O seu trabalho exige que voce fique 'ligado' ou concentrado por tempo demais sem parar?", "dim": "Demanda"},
    {"id": 6, "texto": "Voce pode dar sua opiniao sobre como o trabalho do seu setor e organizado?", "dim": "Controle"},
    {"id": 7, "texto": "Voce consegue escolher a ordem das tarefas que vai fazer durante o seu turno?", "dim": "Controle"},
    {"id": 8, "texto": "O seu trabalho te ensina coisas novas ou te ajuda a crescer como profissional?", "dim": "Controle"},
    {"id": 9, "texto": "Se voce precisar de 5 minutos para ir ao banheiro ou tomar agua, voce consegue sair?", "dim": "Controle"},
    {"id": 10, "texto": "A empresa te escuta antes de mudar alguma regra que afeta o seu dia a dia?", "dim": "Controle"},
    {"id": 11, "texto": "Se o bicho pegar no servico, voce sente que seus colegas te ajudam?", "dim": "Suporte"},
    {"id": 12, "texto": "O seu encarregado ou supervisor te ajuda a resolver problemas de trabalho?", "dim": "Suporte"},
    {"id": 13, "texto": "Alguem te avisa se o seu trabalho esta sendo bem feito ou se precisa melhorar?", "dim": "Suporte"},
    {"id": 14, "texto": "As ferramentas, EPIs e materiais que voce precisa estao sempre na mao?", "dim": "Suporte"},
    {"id": 15, "texto": "Voce sente que a empresa valoriza o esforco que voce faz no dia a dia?", "dim": "Suporte"},
    {"id": 16, "texto": "O pessoal do seu setor trabalha unido e se ajuda de verdade?", "dim": "Relacionamento"},
    {"id": 17, "texto": "Voce sofre alguma pressao chata, fofoca ou falta de respeito de outros colegas?", "dim": "Relacionamento"},
    {"id": 18, "texto": "Quando rola uma briga ou desentendimento, a chefia resolve de um jeito justo?", "dim": "Relacionamento"},
    {"id": 19, "texto": "Existe respeito e educacao entre todo mundo, desde o ajudante ate o chefe?", "dim": "Relacionamento"},
    {"id": 20, "texto": "Voce se sente bem vindo e respeitado pelos seus companheiros de equipe?", "dim": "Relacionamento"},
    {"id": 21, "texto": "Voce sabe exatamente o que a empresa espera do seu trabalho?", "dim": "Papel"},
    {"id": 22, "texto": "As suas obrigacoes sao bem explicadas ou voce fica em duvida do que e sua funcao?", "dim": "Papel"},
    {"id": 23, "texto": "Acontece de um chefe mandar uma coisa e outro chefe mandar outra diferente?", "dim": "Papel"},
    {"id": 24, "texto": "Voce entende por que o seu trabalho e importante para o resultado da empresa?", "dim": "Papel"},
    {"id": 25, "texto": "Voce tem permissao para resolver os probleminhas que aparecem na sua frente?", "dim": "Papel"},
    {"id": 26, "texto": "A empresa te avisa com antecedencia se for mudar seu horario ou sua equipe?", "dim": "Mudanca"},
    {"id": 27, "texto": "A chefia te pergunta o que voce acha antes de mudar o seu jeito de trabalhar?", "dim": "Mudanca"},
    {"id": 28, "texto": "Quando chega uma maquina ou tecnologia nova, explicam bem como usar antes de comecar?", "dim": "Mudanca"},
    {"id": 29, "texto": "Voce sente que seu emprego esta garantido e que nao sera mandado embora logo?", "dim": "Mudanca"},
    {"id": 30, "texto": "Quando muda alguma regra ou ferramenta, a chefia te treina e te ajuda a se adaptar?", "dim": "Mudanca"}
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "As vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

# --- ROTA DO FORMULÁRIO (CLIENTE) ---
@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'UNISAFE')
    setores = CONFIG_CLIENTES.get(cliente_id, ["Geral", "Administrativo", "Operacional"])
    nome_exibicao = cliente_id.replace("_", " ")
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=nome_exibicao)

# --- ROTA DO PAINEL ADMIN ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    mensagem = ""
    link_gerado = ""
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == SENHA_ADMIN:
            novo_cliente = request.form.get('nome_cliente').replace(" ", "_")
            setores_txt = request.form.get('setores')
            CONFIG_CLIENTES[novo_cliente] = [s.strip() for s in setores_txt.split(",")]
            link_gerado = f"{request.url_root}?cliente={novo_cliente}"
            mensagem = f"Sucesso! Link para {novo_cliente} gerado."
        else:
            mensagem = "Senha incorreta!"
    return render_template('admin.html', mensagem=mensagem, link=link_gerado, clientes=CONFIG_CLIENTES)

# --- ROTA DE ENVIO ---
@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    setor = request.form.get('setor')
    respostas = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTOES}
    total = sum(int(v) for v in respostas.values() if v)
    
    # Google Sheets
    try:
        requests.post(URL_PLANILHA, data=json.dumps({"cliente": cliente_final, "setor": setor, "pontuacao": total}), timeout=5)
    except: pass

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"LAUDO SST - {cliente_final}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Setor: {setor}", ln=True)
    pdf.cell(0, 10, f"Score: {total} / 120", ln=True)
    pdf.output("laudo.pdf")
    return send_file("laudo.pdf", as_attachment=True)

# --- CORREÇÃO DA PORTA PARA O RENDER ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
