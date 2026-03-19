from flask import Flask, render_template, request, make_response
import requests
import json

app = Flask(__name__)

URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

MAPA_RISCOS = {
    "Demanda": {"perigo": "Sobrecarga física/mental", "consequencia": "Burnout; DORT", "medida": "Redimensionar tarefas."},
    "Controle": {"perigo": "Baixa autonomia", "consequencia": "Estresse crônico", "medida": "Permitir participação nas decisões."},
    "Suporte": {"perigo": "Isolamento/Falta de apoio", "consequencia": "Depressão; Ansiedade", "medida": "Treinamento de liderança."},
    "Relacionamento": {"perigo": "Conflitos/Assédio", "consequencia": "Adoecimento mental", "medida": "Código de ética e mediação."},
    "Bem-Estar": {"perigo": "Desgaste geral", "consequencia": "Afastamento", "medida": "Programa de saúde mental."}
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
    {"id": 29, "texto": "As mudanças recentes foram bem planejadas?", "dim": "Mudanca", "inv": True},
    {"id": 30, "texto": "Você se sente seguro quanto ao futuro na empresa?", "dim": "Mudanca", "inv": True}
]

# --- MODELO PREMIUM (62 QUESTÕES COMPLETAS - COPSOQ III) ---
QUESTOES_PREMIUM = [
    # Demandas (1-10)
    {"id": 1, "texto": "Você precisa trabalhar muito rápido?", "dim": "Demanda", "inv": False},
    {"id": 2, "texto": "Seu trabalho exige um ritmo intenso?", "dim": "Demanda", "inv": False},
    {"id": 3, "texto": "Você fica atrás no trabalho por excesso de tarefas?", "dim": "Demanda", "inv": False},
    {"id": 4, "texto": "Você tem tempo para completar suas tarefas?", "dim": "Demanda", "inv": True},
    {"id": 5, "texto": "Seu trabalho exige muita concentração?", "dim": "Demanda", "inv": False},
    {"id": 6, "texto": "Você precisa lidar com muitas informações ao mesmo tempo?", "dim": "Demanda", "inv": False},
    {"id": 7, "texto": "Seu trabalho é emocionalmente desgastante?", "dim": "Demanda", "inv": False},
    {"id": 8, "texto": "Você precisa esconder suas emoções no trabalho?", "dim": "Demanda", "inv": False},
    {"id": 9, "texto": "Você precisa lidar com clientes/pessoas difíceis?", "dim": "Demanda", "inv": False},
    {"id": 10, "texto": "Suas exigências do trabalho atrapalham sua vida familiar?", "dim": "Demanda", "inv": False},
    # Controle e Autonomia (11-20)
    {"id": 11, "texto": "Você tem voz sobre como seu trabalho é organizado?", "dim": "Controle", "inv": True},
    {"id": 12, "texto": "Você pode influenciar a quantidade de trabalho que recebe?", "dim": "Controle", "inv": True},
    {"id": 13, "texto": "Você tem autonomia para tomar decisões?", "dim": "Controle", "inv": True},
    {"id": 14, "texto": "Você pode escolher seu próprio ritmo de trabalho?", "dim": "Controle", "inv": True},
    {"id": 15, "texto": "Seu trabalho permite aprender coisas novas?", "dim": "Controle", "inv": True},
    {"id": 16, "texto": "Você pode usar suas habilidades no trabalho?", "dim": "Controle", "inv": True},
    {"id": 17, "texto": "Seu trabalho tem sentido para você?", "dim": "Controle", "inv": True},
    {"id": 18, "texto": "Você sente que seu trabalho é importante?", "dim": "Controle", "inv": True},
    {"id": 19, "texto": "Você se sente orgulhoso de sua empresa?", "dim": "Controle", "inv": True},
    {"id": 20, "texto": "Você se sente comprometido com seu local de trabalho?", "dim": "Controle", "inv": True},
    # Suporte e Liderança (21-35)
    {"id": 21, "texto": "Você sabe exatamente quais são suas responsabilidades?", "dim": "Suporte", "inv": True},
    {"id": 22, "texto": "Seus objetivos de trabalho são claros?", "dim": "Suporte", "inv": True},
    {"id": 23, "texto": "Você recebe ordens contraditórias?", "dim": "Suporte", "inv": False},
    {"id": 24, "texto": "Você recebe informações necessárias antecipadamente?", "dim": "Suporte", "inv": True},
    {"id": 25, "texto": "Seu chefe planeja bem o trabalho?", "dim": "Suporte", "inv": True},
    {"id": 26, "texto": "Seu chefe apoia o seu desenvolvimento?", "dim": "Suporte", "inv": True},
    {"id": 27, "texto": "Sua liderança trata todos com justiça?", "dim": "Suporte", "inv": True},
    {"id": 28, "texto": "Você recebe feedback sobre seu desempenho?", "dim": "Suporte", "inv": True},
    {"id": 29, "texto": "Seu esforço é reconhecido pela empresa?", "dim": "Suporte", "inv": True},
    {"id": 30, "texto": "Você sente que é tratado com respeito?", "dim": "Suporte", "inv": True},
    {"id": 31, "texto": "Seus colegas te ouvem quando você precisa?", "dim": "Suporte", "inv": True},
    {"id": 32, "texto": "Seus colegas te ajudam nas tarefas difíceis?", "dim": "Suporte", "inv": True},
    {"id": 33, "texto": "Você sente que faz parte de uma equipe?", "dim": "Suporte", "inv": True},
    {"id": 34, "texto": "Você confia na gerência da empresa?", "dim": "Suporte", "inv": True},
    {"id": 35, "texto": "A empresa investe no bem-estar dos funcionários?", "dim": "Suporte", "inv": True},
    # Relacionamento e Justiça (36-45)
    {"id": 36, "texto": "Existe cooperação mútua entre os setores?", "dim": "Relacionamento", "inv": True},
    {"id": 37, "texto": "Conflitos são resolvidos de forma construtiva?", "dim": "Relacionamento", "inv": True},
    {"id": 38, "texto": "Existe fofoca ou rumores negativos no setor?", "dim": "Relacionamento", "inv": False},
    {"id": 39, "texto": "Você presencia falta de ética profissional?", "dim": "Relacionamento", "inv": False},
    {"id": 40, "texto": "As promoções são dadas de forma justa?", "dim": "Relacionamento", "inv": True},
    {"id": 41, "texto": "A comunicação interna é honesta?", "dim": "Relacionamento", "inv": True},
    {"id": 42, "texto": "Você se sente seguro contra discriminação?", "dim": "Relacionamento", "inv": True},
    {"id": 43, "texto": "A empresa valoriza a diversidade?", "dim": "Relacionamento", "inv": True},
    {"id": 44, "texto": "Existe transparência nas decisões da chefia?", "dim": "Relacionamento", "inv": True},
    {"id": 45, "texto": "Você é consultado antes de mudanças no seu posto?", "dim": "Relacionamento", "inv": True},
    # Saúde, Bem-Estar e Insegurança (46-62)
    {"id": 46, "texto": "Você tem medo de perder o emprego?", "dim": "Bem-Estar", "inv": False},
    {"id": 47, "texto": "Você teme ser transferido contra sua vontade?", "dim": "Bem-Estar", "inv": False},
    {"id": 48, "texto": "Sente-se inseguro quanto ao futuro da empresa?", "dim": "Bem-Estar", "inv": False},
    {"id": 49, "texto": "Você se sente satisfeito com seu trabalho?", "dim": "Bem-Estar", "inv": True},
    {"id": 50, "texto": "Como você avalia sua saúde mental geral?", "dim": "Bem-Estar", "inv": True},
    {"id": 51, "texto": "Você se sente esgotado fisicamente?", "dim": "Bem-Estar", "inv": False},
    {"id": 52, "texto": "Você se sente esgotado mentalmente?", "dim": "Bem-Estar", "inv": False},
    {"id": 53, "texto": "Sente dificuldade para dormir por causa do trabalho?", "dim": "Bem-Estar", "inv": False},
    {"id": 54, "texto": "Sente-se tenso ou ansioso frequentemente?", "dim": "Bem-Estar", "inv": False},
    {"id": 55, "texto": "Sente-se irritado com facilidade?", "dim": "Bem-Estar", "inv": False},
    {"id": 56, "texto": "Você trabalha mesmo quando se sente doente?", "dim": "Bem-Estar", "inv": False},
    {"id": 57, "texto": "Sente que seu trabalho afeta negativamente sua saúde?", "dim": "Bem-Estar", "inv": False},
    {"id": 58, "texto": "Você recomendaria sua empresa para um amigo?", "dim": "Bem-Estar", "inv": True},
    {"id": 59, "texto": "Pretende continuar na empresa nos próximos 2 anos?", "dim": "Bem-Estar", "inv": True},
    {"id": 60, "texto": "Sente que tem equilíbrio entre vida e trabalho?", "dim": "Bem-Estar", "inv": True},
    {"id": 61, "texto": "A empresa oferece canais de denúncia seguros?", "dim": "Bem-Estar", "inv": True},
    {"id": 62, "texto": "Você se sente valorizado como ser humano?", "dim": "Bem-Estar", "inv": True}
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
        servico = dados.get('servico', 'standard').lower().strip()
        setores = dados.get('setores', ["Geral"])
        modo = dados.get('modo', 'individual')
    except:
        servico, setores, modo = "standard", ["Geral"], "individual"

    questoes = QUESTOES_PREMIUM if servico == "premium" else QUESTOES_STANDARD
    return render_template('index.html', questoes=questoes, cliente=cliente_id.title(), servico=servico, setores=setores, opcoes=OPCOES, modo=modo)

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'unisafe').lower()
    servico_final = request.form.get('servico_escondido', 'standard')
    setor_escolhido = request.form.get('setor')
    modo_final = request.form.get('modo_escondido', 'individual')
    
    questoes_ativas = QUESTOES_PREMIUM if servico_final == "premium" else QUESTOES_STANDARD
    total_risco = 0
    pontos_por_dim = {d: 0 for d in MAPA_RISCOS.keys()}
    
    for q in questoes_ativas:
        val_form = request.form.get(f"q{q['id']}")
        if val_form is not None:
            resposta = int(val_form)
            # INVERSÃO INTELIGENTE: (4-resp) se for pergunta "boa"
            pontos = (4 - resposta) if q['inv'] else resposta
            if q['dim'] in pontos_por_dim:
                pontos_por_dim[q['dim']] += pontos
            total_risco += pontos

    max_pontos = len(questoes_ativas) * 4
    porcentagem = (total_risco / max_pontos) * 100
    if porcentagem <= 33: status = "BAIXO"
    elif porcentagem <= 66: status = "MODERADO"
    else: status = "CRÍTICO"

    dim_critica = max(pontos_por_dim, key=pontos_por_dim.get)
    info_risco = MAPA_RISCOS.get(dim_critica, MAPA_RISCOS["Bem-Estar"])

    try:
        dados_envio = {
            "cliente": cliente_final, "setor": setor_escolhido, "pontuacao": total_risco,
            "status": status, "perigo": info_risco["perigo"],
            "consequencia": info_risco["consequencia"], "medida": info_risco["medida"]
        }
        requests.post(URL_GOOGLE, data=json.dumps(dados_envio), timeout=15)
        
        resp = make_response(f"<div style='text-align:center; padding:50px; font-family:sans-serif;'><h1>Sucesso!</h1><p>Diagnóstico registrado.</p></div>")
        if modo_final != "totem":
            resp.set_cookie(f'participou_{cliente_final}', 'sim', max_age=60*60*24*30, path='/')
        return resp
    except:
        return "Erro no envio."

if __name__ == '__main__':
    app.run(debug=True)
