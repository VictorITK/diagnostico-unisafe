from flask import Flask, render_template, request
import os
import requests
import json

app = Flask(__name__)

URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

MAPA_RISCOS = {
    "Demanda": {
        "perigo": "Excesso de demandas no trabalho (sobrecarga)",
        "consequencia": "Transtorno mental; DORT; Doenças cardiovasculares",
        "medida": "Priorização de tarefas; pausas regulares; redimensionamento de equipe; flexibilização de horários."
    },
    "Controle": {
        "perigo": "Baixo controle no trabalho / Falta de autonomia",
        "consequencia": "Transtorno mental; DORT",
        "medida": "Aumentar participação do trabalhador na organização; permitir resolução de problemas no posto."
    },
    "Suporte": {
        "perigo": "Falta de suporte/apoio no trabalho",
        "consequencia": "Transtorno mental",
        "medida": "Canais de diálogo com a chefia; suporte gerencial ativo; fortalecimento da comunicação interna."
    },
    "Relacionamento": {
        "perigo": "Maus relacionamentos / Assédio",
        "consequencia": "Transtorno mental",
        "medida": "Código de ética; mediação de conflitos; canais de denúncia seguros e anônimos."
    },
    "Papel": {
        "perigo": "Baixa clareza de papel/função",
        "consequencia": "Transtorno mental",
        "medida": "Definição clara de atribuições; revisões semanais de metas; treinamento sobre fluxo de trabalho."
    },
    "Mudanca": {
        "perigo": "Má gestão de mudanças organizacionais",
        "consequencia": "Transtorno mental; DORT",
        "medida": "Comunicação antecipada; treinamentos prévios; escuta ativa antes da implementação."
    }
}

QUESTOES = [
    {"id": 1, "texto": "Você sente que precisa correr ou trabalhar muito rápido?", "dim": "Demanda"},
    {"id": 2, "texto": "No final do dia, você se sente 'esgotado' mentalmente?", "dim": "Demanda"},
    {"id": 3, "texto": "A chefia entrega tarefas com prazos impossíveis?", "dim": "Demanda"},
    {"id": 4, "texto": "Você pode opinar sobre como o trabalho é organizado?", "dim": "Controle"},
    {"id": 5, "texto": "Você consegue escolher a ordem das tarefas?", "dim": "Controle"},
    {"id": 6, "texto": "Seus colegas te ajudam quando o bicho pega?", "dim": "Suporte"},
    {"id": 7, "texto": "O supervisor te ajuda a resolver problemas?", "dim": "Suporte"},
    {"id": 8, "texto": "Existe respeito e educação entre todos?", "dim": "Relacionamento"},
    {"id": 9, "texto": "Você sofre pressão chata ou fofoca de colegas?", "dim": "Relacionamento"},
    {"id": 10, "texto": "Você sabe exatamente o que a empresa espera de você?", "dim": "Papel"},
    {"id": 11, "texto": "A empresa avisa antes de mudar seu horário ou equipe?", "dim": "Mudanca"}
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "À vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'UNISAFE').strip().lower()
    try:
        r = requests.get(f"{URL_GOOGLE}?cliente={cliente_id}", timeout=10)
        setores = r.json().get('setores', ["Geral"])
    except:
        setores = ["Geral"]
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=cliente_id.title())

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    setor_escolhido = request.form.get('setor')
    
    pontos_por_dim = {d: 0 for d in MAPA_RISCOS.keys()}
    total = 0
    for q in QUESTOES:
        val = int(request.form.get(f"q{q['id']}", 0))
        pontos_por_dim[q['dim']] += val
        total += val

    dim_critica = max(pontos_por_dim, key=pontos_por_dim.get)
    info_risco = MAPA_RISCOS[dim_critica]

    try:
        dados_envio = {
            "cliente": cliente_final,
            "setor": setor_escolhido,
            "pontuacao": total,
            "status": "ALERTA" if total >= 15 else "OK", 
            "perigo": info_risco["perigo"],
            "consequencia": info_risco["consequencia"],
            "medida": info_risco["medida"]
        }
        requests.post(URL_GOOGLE, data=json.dumps(dados_envio), timeout=10)
    except: pass

    return "<h1>Sucesso!</h1><p>Suas respostas foram registradas anonimamente. Obrigado por colaborar com a UNISAFE.</p>"
