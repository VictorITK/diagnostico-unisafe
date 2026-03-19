from flask import Flask, render_template, request, make_response, url_for
import requests
import json
import os

app = Flask(__name__)

URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

# DICIONÁRIO PREMIUM (20 DOMÍNIOS - BASEADO NO COPSOQ II)
DOMINIOS_PREMIUM = {
    "Demandas Quantitativas": {"perigo": "Sobrecarga de volume", "medida": "Redimensionar equipe"},
    "Demandas Cognitivas": {"perigo": "Alta exigência mental", "medida": "Pausas cognitivas"},
    "Demandas Emocionais": {"perigo": "Desgaste emocional", "medida": "Suporte psicológico"},
    "Influência no Trabalho": {"perigo": "Baixa autonomia", "medida": "Participação nas decisões"},
    "Possibilidades de Desenvolvimento": {"perigo": "Estagnação", "medida": "Plano de carreira"},
    "Sentido do Trabalho": {"perigo": "Falta de propósito", "medida": "Feedback de impacto"},
    "Comprometimento com o Local": {"perigo": "Baixo engajamento", "medida": "Programas de incentivo"},
    "Clareza de Papel": {"perigo": "Ambiguidade de funções", "medida": "Definição de cargos"},
    "Conflitos de Papel": {"perigo": "Ordens contraditórias", "medida": "Alinhamento gerencial"},
    "Qualidade de Liderança": {"perigo": "Gestão ineficiente", "medida": "Treinamento de líderes"},
    "Apoio Social - Chefia": {"perigo": "Isolamento da gestão", "medida": "Canais de escuta"},
    "Apoio Social - Colegas": {"perigo": "Falta de cooperação", "medida": "Dinâmicas de grupo"},
    "Feedback sobre o Trabalho": {"perigo": "Falta de retorno", "medida": "Avaliações periódicas"},
    "Reconhecimento": {"perigo": "Invisibilidade", "medida": "Reconhecimento público"},
    "Previsibilidade": {"perigo": "Incerteza constante", "medida": "Transparência de metas"},
    "Justiça Organizacional": {"perigo": "Tratamento desigual", "medida": "Políticas de equidade"},
    "Insegurança no Trabalho": {"perigo": "Medo de demissão", "medida": "Estabilidade e comunicação"},
    "Conflito Trabalho-Família": {"perigo": "Desequilíbrio pessoal", "medida": "Flexibilidade de horário"},
    "Saúde e Bem-Estar": {"perigo": "Adoecimento", "medida": "Programa de saúde mental"},
    "Presenteísmo": {"perigo": "Trabalho doente", "medida": "Cultura de cuidado"}
}

# QUESTÕES PREMIUM (Resumidas para teste, mas cobrindo os domínios)
QUESTOES_PREMIUM = [
    {"id": 1, "texto": "Você tem tempo suficiente para as tarefas?", "dim": "Demandas Quantitativas", "inv": True},
    {"id": 2, "texto": "Seu trabalho exige que você tome decisões difíceis?", "dim": "Demandas Cognitivas", "inv": False},
    {"id": 3, "texto": "Seu trabalho é emocionalmente desgastante?", "dim": "Demandas Emocionais", "inv": False},
    {"id": 4, "texto": "Você pode influenciar as decisões do seu setor?", "dim": "Influência no Trabalho", "inv": True},
    {"id": 5, "texto": "Você aprende coisas novas no seu trabalho?", "dim": "Possibilidades de Desenvolvimento", "inv": True},
    {"id": 6, "texto": "Você sente que seu trabalho é importante?", "dim": "Sentido do Trabalho", "inv": True},
    {"id": 7, "texto": "Você se sente orgulhoso de trabalhar aqui?", "dim": "Comprometimento com o Local", "inv": True},
    {"id": 8, "texto": "Você sabe exatamente quais são suas tarefas?", "dim": "Clareza de Papel", "inv": True},
    {"id": 9, "texto": "Você recebe pedidos contraditórios de chefes diferentes?", "dim": "Conflitos de Papel", "inv": False},
    {"id": 10, "texto": "Seu chefe planeja bem o trabalho da equipe?", "dim": "Qualidade de Liderança", "inv": True},
    {"id": 11, "texto": "Seu chefe ouve suas sugestões?", "dim": "Apoio Social - Chefia", "inv": True},
    {"id": 12, "texto": "Seus colegas te ajudam quando você precisa?", "dim": "Apoio Social - Colegas", "inv": True},
    {"id": 13, "texto": "A empresa te informa como está o seu desempenho?", "dim": "Feedback sobre o Trabalho", "inv": True},
    {"id": 14, "texto": "Seu trabalho é reconhecido e valorizado?", "dim": "Reconhecimento", "inv": True},
    {"id": 15, "texto": "Você recebe as informações que precisa antecipadamente?", "dim": "Previsibilidade", "inv": True},
    {"id": 16, "texto": "Os problemas são resolvidos de forma justa aqui?", "dim": "Justiça Organizacional", "inv": True},
    {"id": 17, "texto": "Você tem medo de perder o emprego em breve?", "dim": "Insegurança no Trabalho", "inv": False},
    {"id": 18, "texto": "Suas exigências do trabalho atrapalham sua vida familiar?", "dim": "Conflito Trabalho-Família", "inv": False},
    {"id": 19, "texto": "Você se sente esgotado ao final do dia?", "dim": "Saúde e Bem-Estar", "inv": False},
    {"id": 20, "texto": "Você trabalha mesmo quando se sente doente?", "dim": "Presenteísmo", "inv": False}
]

# (Mantenha aqui as QUESTOES_STANDARD e MAPA_RISCOS_STANDARD que já tínhamos)
QUESTOES_STANDARD = [
    {"id": 1, "texto": "Você precisa trabalhar muito rápido?", "dim": "Demanda", "inv": False},
    # ... (restante das 30 questões que já usamos)
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "Às vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'unisafe').strip().lower()
    tipo_servico = request.args.get('servico', 'standard').lower() # NOVO: standard ou premium
    
    if request.cookies.get(f'participou_{cliente_id}'):
        return render_template('bloqueado.html', cliente=cliente_id.title())
        
    try:
        r = requests.get(f"{URL_GOOGLE}?cliente={cliente_id}", timeout=15)
        dados = r.json()
        setores = dados.get('setores', ["Geral"])
        modo_cliente = dados.get('modo', 'individual').lower().strip()
    except:
        setores, modo_cliente = ["Geral"], "individual"

    questoes = QUESTOES_PREMIUM if tipo_servico == 'premium' else QUESTOES_STANDARD
    
    return render_template('index.html', questoes=questoes, opcoes=OPCOES, setores=setores, cliente=cliente_id.title(), modo=modo_cliente, servico=tipo_servico)

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'unisafe').lower()
    tipo_servico = request.form.get('servico_escondido', 'standard')
    # ... (Lógica de cálculo adaptada para o tipo_servico)
    # Envia para a planilha do cliente configurada no ID_Planilha
    return "Sucesso!"
