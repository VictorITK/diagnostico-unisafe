from flask import Flask, render_template, request, make_response, url_for
import requests
import json
import os

app = Flask(__name__)

# Sua URL oficial do Google Apps Script
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

# MAPEAMENTO DE RISCOS (Para o Laudo na Planilha)
MAPA_RISCOS = {
    "Demanda": {"perigo": "Excesso de demandas (sobrecarga)", "consequencia": "Transtorno mental; DORT", "medida": "Priorização de tarefas; pausas."},
    "Controle": {"perigo": "Baixo controle / Falta de autonomia", "consequencia": "Transtorno mental", "medida": "Aumentar participação na organização."},
    "Suporte": {"perigo": "Falta de suporte/apoio", "consequencia": "Transtorno mental", "medida": "Canais de diálogo com chefia."},
    "Relacionamento": {"perigo": "Maus relacionamentos / Assédio", "consequencia": "Transtorno mental", "medida": "Código de ética; mediação."},
    "Papel": {"perigo": "Baixa clareza de papel/função", "consequencia": "Transtorno mental", "medida": "Definição clara de atribuições."},
    "Mudanca": {"perigo": "Má gestão de mudanças", "consequencia": "Transtorno mental", "medida": "Comunicação antecipada; treinamentos."},
    "Bem-Estar": {"perigo": "Desgaste psicossocial geral", "consequencia": "Adoecimento; Burnout", "medida": "Programa de saúde mental e escuta ativa."}
}

# --- MODELO STANDARD (30 QUESTÕES) ---
QUESTOES_STANDARD = [
    {"id": 1, "texto": "Você precisa trabalhar muito rápido?", "dim": "Demanda", "inv": False},
    {"id": 2, "texto": "Seu trabalho exige muito esforço emocional?", "dim": "Demanda", "inv": False},
    {"id": 3, "texto": "Você tem tempo suficiente para concluir suas tarefas?", "dim": "Demanda", "inv": True},
    {"id": 4, "texto": "O volume de trabalho é excessivo?", "dim": "Demanda", "inv": False},
    {"id": 5, "texto": "Você precisa trabalhar horas extras com frequência?", "dim": "Demanda", "inv": False},
    {"id": 6, "texto": "Você pode influenciar a quantidade de trabalho que recebe?", "dim": "Controle", "inv": True},
    {"id": 7, "texto": "Você tem voz sobre como o trabalho é organizado?", "dim": "Controle", "inv": True},
    {"id": 8, "texto": "Você pode escolher o seu ritmo de trabalho?", "dim": "Controle", "inv": True},
    {"id": 9, "texto": "O trabalho permite que você aprenda coisas novas?", "dim": "Controle", "inv": True},
    {"id": 10, "texto": "Você tem autonomia para tomar decisões importantes?", "dim": "Controle", "inv": True},
    {"id": 11, "texto": "Seus colegas ouvem seus problemas de trabalho?", "dim": "Suporte", "inv": True},
    {"id": 12, "texto": "Você recebe apoio dos colegas quando precisa?", "dim": "Suporte", "inv": True},
    {"id": 13, "texto": "Seu superior direto apoia o seu desenvolvimento?", "dim": "Suporte", "inv": True},
    {"id": 14, "texto": "O supervisor ajuda a planejar bem as tarefas?", "dim": "Suporte", "inv": True},
    {"id": 15, "texto": "A empresa oferece recursos necessários para o trabalho?", "dim": "Suporte", "inv": True},
    {"id": 16, "texto": "Existe colaboração na sua equipe?", "dim": "Relacionamento", "inv": True},
    {"id": 17, "texto": "Você se sente respeitado no ambiente de trabalho?", "dim": "Relacionamento", "inv": True},
    {"id": 18, "texto": "Existem conflitos constantes entre os colegas?", "dim": "Relacionamento", "inv": False},
    {"id": 19, "texto": "Você já presenciou falta de ética no trabalho?", "dim": "Relacionamento", "inv": False},
    {"id": 20, "texto": "A comunicação interna é clara e educada?", "dim": "Relacionamento", "inv": True},
    {"id": 21, "texto": "Você sabe exatamente suas responsabilidades?", "dim": "Papel", "inv": True},
    {"id": 22, "texto": "Seus objetivos de trabalho são claros?", "dim": "Papel", "inv": True},
    {"id": 23, "texto": "Você recebe ordens conflitantes?", "dim": "Papel", "inv": False},
    {"id": 24, "texto": "Você entende como seu trabalho ajuda a empresa?", "dim": "Papel", "inv": True},
    {"id": 25, "texto": "As expectativas sobre seu cargo são bem definidas?", "dim": "Papel", "inv": True},
    {"id": 26, "texto": "A empresa avisa mudanças com antecedência?", "dim": "Mudanca", "inv": True},
    {"id": 27, "texto": "Você é consultado antes de mudanças no seu posto?", "dim": "Mudanca", "inv": True},
    {"id": 28, "texto": "Há treinamento quando algo novo é implementado?", "dim": "Mudanca", "inv": True},
    {"id": 30, "texto": "As mudanças recentes foram bem planejadas?", "dim": "Mudanca", "inv": True},
    {"id": 30, "texto": "Você se sente seguro quanto ao futuro na empresa?", "dim": "Mudanca", "inv": True}
]

# --- MODELO PREMIUM (40 QUESTÕES - 20 DOMÍNIOS) ---
QUESTOES_PREMIUM = [
    {"id": 1, "texto": "Você tem tempo suficiente para suas tarefas?", "dim": "Demanda", "inv": True},
    {"id": 2, "texto": "O volume de trabalho é excessivo?", "dim": "Demanda", "inv": False},
    {"id": 3, "texto": "Seu trabalho exige que você tome decisões difíceis?", "dim": "Demanda", "inv": False},
    {"id": 4, "texto": "Seu trabalho é emocionalmente desgastante?", "dim": "Demanda", "inv": False},
    {"id": 5, "texto": "Você pode influenciar as decisões do seu setor?", "dim": "Controle", "inv": True},
    {"id": 6, "texto": "Você tem voz sobre como o trabalho é organizado?", "dim": "Controle", "inv": True},
    {"id": 7, "texto": "Você aprende coisas novas no seu trabalho?", "dim": "Controle", "inv": True},
    {"id": 8, "texto": "Você sente que seu trabalho é importante?", "dim": "Papel", "inv": True},
    {"id": 9, "texto": "Você se sente orgulhoso de trabalhar aqui?", "dim": "Bem-Estar", "inv": True},
    {"id": 10, "texto": "Você sabe exatamente quais são suas tarefas?", "dim": "Papel", "inv": True},
    {"id": 11, "texto": "Você recebe pedidos contraditórios?", "dim": "Papel", "inv": False},
    {"id": 12, "texto": "Seu chefe planeja bem o trabalho da equipe?", "dim": "Suporte", "inv": True},
    {"id": 13, "texto": "Seu chefe ouve suas sugestões?", "dim": "Suporte", "inv": True},
    {"id": 14, "texto": "Seus colegas te ajudam quando você precisa?", "dim": "Suporte", "inv": True},
    {"id": 15, "texto": "A empresa informa seu desempenho?", "dim": "Suporte", "inv": True},
    {"id": 16, "texto": "Seu trabalho é reconhecido e valorizado?", "dim": "Suporte", "inv": True},
    {"id": 17, "texto": "As mudanças são informadas com antecedência?", "dim": "Mudanca", "inv": True},
    {"id": 18, "texto": "Os problemas são resolvidos de forma justa?", "dim": "Relacionamento", "inv": True},
    {"id": 19, "texto": "Você tem medo de perder o emprego?", "dim": "Mudanca", "inv": False},
    {"id": 20, "texto": "O trabalho atrapalha sua vida familiar?", "dim": "Demanda", "inv": False},
    {"id": 21, "texto": "Você se sente esgotado ao final do dia?", "dim": "Bem-Estar", "inv": False},
    {"id": 22, "texto": "Trabalha mesmo quando se sente doente?", "dim": "Bem-Estar", "inv": False},
    {"id": 23, "texto": "Existe fofoca ou rumores no seu setor?", "dim": "Relacionamento", "inv": False},
    {"id": 24, "texto": "O ambiente é de cooperação mútua?", "dim": "Relacionamento", "inv": True},
    {"id": 25, "texto": "A empresa valoriza sua saúde?", "dim": "Bem-Estar", "inv": True},
    {"id": 26, "texto": "Você é tratado com respeito por todos?", "dim": "Relacionamento", "inv": True},
    {"id": 27, "texto": "Seu cargo tem metas realistas?", "dim": "Demanda", "inv": True},
    {"id": 28, "texto": "O ritmo de trabalho é puxado demais?", "dim": "Demanda", "inv": False},
    {"id": 29, "texto": "Você tem as ferramentas que precisa?", "dim": "Suporte", "inv": True},
    {"id": 30, "texto": "Sua liderança é presente e acessível?", "dim": "Suporte", "inv": True},
    {"id": 31, "texto": "Você sente que seu esforço é recompensado?", "dim": "Suporte", "inv": True},
    {"id": 32, "texto": "A comunicação da empresa é honesta?", "dim": "Relacionamento", "inv": True},
    {"id": 33, "texto": "O trabalho exige muita concentração?", "dim": "Demanda", "inv": False},
    {"id": 34, "texto": "Sua função é variada e desafiadora?", "dim": "Controle", "inv": True},
    {"id": 35, "texto": "Você confia na gerência da empresa?", "dim": "Suporte", "inv": True},
    {"id": 36, "texto": "As promoções são dadas por mérito?", "dim": "Relacionamento", "inv": True},
    {"id": 37, "texto": "Você sente que faz parte de um time?", "dim": "Relacionamento", "inv": True},
    {"id": 38, "texto": "Seu trabalho afeta seu sono?", "dim": "Bem-Estar", "inv": False},
    {"id": 39, "texto": "A empresa investe no seu treinamento?", "dim": "Controle", "inv": True},
    {"id": 40, "texto": "Você indicaria esta empresa para um amigo?", "dim": "Bem-Estar", "inv": True}
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "Às vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'unisafe').strip().lower()
    
    if request.cookies.get(f'participou_{cliente_id}'):
        return render_template('bloqueado.html', cliente=cliente_id.title())
        
    try:
        r = requests.get(f"{URL_GOOGLE}?cliente={cliente_id}", timeout=15)
        dados = r.json()
        setores = dados.get('setores', ["Geral"])
        modo_cliente = dados.get('modo', 'individual').lower().strip()
        servico = dados.get('servico', 'standard').lower().strip() # Pega o tipo da Planilha Mestra
    except:
        setores, modo_cliente, servico = ["Geral"], "individual", "standard"

    # ESCOLHE O QUESTIONÁRIO COM BASE NO SERVIÇO NA PLANILHA MESTRA
    questoes = QUESTOES_PREMIUM if servico == "premium" else QUESTOES_STANDARD
    
    return render_template('index.html', questoes=questoes, opcoes=OPCOES, setores=setores, cliente=cliente_id.title(), modo=modo_cliente, servico=servico)

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'unisafe').lower()
    servico_final = request.form.get('servico_escondido', 'standard')
    setor_escolhido = request.form.get('setor')
    
    questoes_ativas = QUESTOES_PREMIUM if servico_final == "premium" else QUESTOES_STANDARD
    
    total_risco = 0
    pontos_por_dim = {d: 0 for d in MAPA_RISCOS.keys()}
    
    for q in questoes_ativas:
        resposta = int(request.form.get(f"q{q['id']}", 0))
        pontos = (4 - resposta) if q['inv'] else resposta
        pontos_por_dim.get(q['dim'], 0) # Segurança para dimensões não mapeadas
        if q['dim'] in pontos_por_dim:
            pontos_por_dim[q['dim']] += pontos
        total_risco += pontos

    # Pontuação máxima muda se for 40 questões
    max_pontos = len(questoes_ativas) * 4
    porcentagem = (total_risco / max_pontos) * 100

    if porcentagem <= 33: status_texto = "BAIXO"
    elif porcentagem <= 66: status_texto = "MODERADO (ALERTA)"
    else: status_texto = "CRÍTICO (URGENTE)"

    dim_critica = max(pontos_por_dim, key=pontos_por_dim.get)
    info_risco = MAPA_RISCOS.get(dim_critica, MAPA_RISCOS["Bem-Estar"])

    try:
        dados_envio = {
            "cliente": cliente_final, "setor": setor_escolhido, "pontuacao": total_risco,
            "status": status_texto, "perigo": info_risco["perigo"],
            "consequencia": info_risco["consequencia"], "medida": info_risco["medida"]
        }
        requests.post(URL_GOOGLE, data=json.dumps(dados_envio), timeout=15)
        
        resp = make_response(f"<div style='text-align:center; padding:50px; font-family:sans-serif;'><h1>Sucesso!</h1><p>Diagnóstico <strong>{servico_final.upper()}</strong> registrado.</p></div>")
        
        if request.form.get('modo_escondido') != "totem":
            resp.set_cookie(f'participou_{cliente_final}', 'sim', max_age=60*60*24*30, path='/')
        return resp
    except:
        return "<h1>Erro de envio.</h1>"

if __name__ == '__main__':
    app.run(debug=True)
