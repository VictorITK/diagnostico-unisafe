from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
from datetime import datetime

# Configuração padrão do Flask (Ele buscará o index.html dentro da pasta /templates)
app = Flask(__name__)

# 30 Questões Humanizadas (Padrão UNISAFE - HSE/COPSOQ/ISO 45003)
QUESTOES = [
    # DEMANDA
    {"id": 1, "texto": "Voce sente que precisa correr ou trabalhar muito rapido para dar conta de tudo?", "dim": "Demanda"},
    {"id": 2, "texto": "No final do dia, voce se sente muito cansado ou 'esgotado' mentalmente pelo servico?", "dim": "Demanda"},
    {"id": 3, "texto": "A chefia te entrega tarefas com prazos que sao impossiveis de cumprir?", "dim": "Demanda"},
    {"id": 4, "texto": "Voce precisa deixar coisas importantes sem fazer porque tem trabalho demais acumulado?", "dim": "Demanda"},
    {"id": 5, "texto": "O seu trabalho exige que voce fique 'ligado' ou concentrado por tempo demais sem parar?", "dim": "Demanda"},
    # CONTROLE
    {"id": 6, "texto": "Voce pode dar sua opiniao sobre como o trabalho do seu setor e organizado?", "dim": "Controle"},
    {"id": 7, "texto": "Voce consegue escolher a ordem das tarefas que vai fazer durante o seu turno?", "dim": "Controle"},
    {"id": 8, "texto": "O seu trabalho te ensina coisas novas ou te ajuda a crescer como profissional?", "dim": "Controle"},
    {"id": 9, "texto": "Se voce precisar de 5 minutos para ir ao banheiro ou tomar agua, voce consegue sair?", "dim": "Controle"},
    {"id": 10, "texto": "A empresa te escuta antes de mudar alguma regra que afeta o seu dia a dia?", "dim": "Controle"},
    # SUPORTE
    {"id": 11, "texto": "Se o bicho pegar no servico, voce sente que seus colegas te ajudam?", "dim": "Suporte"},
    {"id": 12, "texto": "O seu encarregado ou supervisor te ajuda a resolver problemas de trabalho?", "dim": "Suporte"},
    {"id": 13, "texto": "Alguem te avisa se o seu trabalho esta sendo bem feito ou se precisa melhorar?", "dim": "Suporte"},
    {"id": 14, "texto": "As ferramentas, EPIs e materiais que voce precisa estao sempre na mao?", "dim": "Suporte"},
    {"id": 15, "texto": "Voce sente que a empresa valoriza o esforco que voce faz no dia a dia?", "dim": "Suporte"},
    # RELACIONAMENTO
    {"id": 16, "texto": "O pessoal do seu setor trabalha unido e se ajuda de verdade?", "dim": "Relacionamento"},
    {"id": 17, "texto": "Voce sofre alguma pressao chata, fofoca ou falta de respeito de outros colegas?", "dim": "Relacionamento"},
    {"id": 18, "texto": "Quando rola uma briga ou desentendimento, a chefia resolve de um jeito justo?", "dim": "Relacionamento"},
    {"id": 19, "texto": "Existe respeito e educacao entre todo mundo, desde o ajudante ate o chefe?", "dim": "Relacionamento"},
    {"id": 20, "texto": "Voce se sente bem vindo e respeitado pelos seus companheiros de equipe?", "dim": "Relacionamento"},
    # PAPEL
    {"id": 21, "texto": "Voce sabe exatamente o que a empresa espera do seu trabalho?", "dim": "Papel"},
    {"id": 22, "texto": "As suas obrigacoes sao bem explicadas ou voce fica em duvida do que e sua funcao?", "dim": "Papel"},
    {"id": 23, "texto": "Acontece de um chefe mandar uma coisa e outro chefe mandar outra diferente?", "dim": "Papel"},
    {"id": 24, "texto": "Voce entende por que o seu trabalho e importante para o resultado da empresa?", "dim": "Papel"},
    {"id": 25, "texto": "Voce tem permissao para resolver os probleminhas que aparecem na sua frente?", "dim": "Papel"},
    # MUDANÇA
    {"id": 26, "texto": "A empresa te avisa com antecedencia se for mudar seu horario ou sua equipe?", "dim": "Mudanca"},
    {"id": 27, "texto": "A chefia te pergunta o que voce acha antes de mudar o seu jeito de trabalhar?", "dim": "Mudanca"},
    {"id": 28, "texto": "Quando chega uma maquina ou tecnologia nova, explicam bem como usar antes de comecar?", "dim": "Mudanca"},
    {"id": 29, "texto": "Voce sente que seu emprego esta garantido e que nao sera mandado embora logo?", "dim": "Mudanca"},
    {"id": 30, "texto": "Quando muda alguma regra ou ferramenta, a chefia te treina e te ajuda a se adaptar?", "dim": "Mudanca"}
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "As vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    setores = ["Operacional", "Administrativo", "Logistica", "Manutencao", "Embarcado", "Almoxarifado"]
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores)

@app.route('/enviar', methods=['POST'])
def enviar():
    setor_escolhido = request.form.get('setor')
    respostas = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTOES}
    
    # Geração do PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Título e Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "UNISAFE - DIAGNOSTICO PSICOSSOCIAL", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 8, f"Setor Avaliado: {setor_escolhido}")
    pdf.cell(100, 8, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Cálculo e Resultado
    total = sum(int(v) for v in respostas.values() if v)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 12, f"PONTUACAO DE RISCO: {total} / 120", border=1, ln=True, fill=True, align='C')
    pdf.ln(5)
    
    if total >= 60:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("Arial", 'B', 11)
        pdf.multi_cell(0, 8, "[ALERTA] Risco elevado. Recomendada analise ergonomica organizacional e intervencao imediata no setor.")
    else:
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 8, "[STATUS] Nivel de bem-estar dentro dos parâmetros aceitaveis.", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Nota Técnica Obrigatória
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Observacoes Tecnicas:", ln=True)
    pdf.set_font("Arial", 'I', 9)
    nota = ("As questoes foram adaptadas para o vocabulario operacional visando reduzir o vies "
            "de interpretacao, mantendo a correlacao direta com os indicadores de 'Mudanca' "
            "do padrao HSE e ISO 45003.")
    pdf.multi_cell(0, 6, nota)

    nome_arquivo = f"Laudo_SST_{setor_escolhido}.pdf"
    pdf.output(nome_arquivo)
    return send_file(nome_arquivo, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
