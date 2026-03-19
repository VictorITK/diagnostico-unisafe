from flask import Flask, render_template, request, redirect, url_for
import os
import requests
import json

app = Flask(__name__)

# SEU LINK DO GOOGLE
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

QUESTOES = [
    {"id": 1, "texto": "Você sente que precisa correr ou trabalhar muito rápido para dar conta de tudo?", "dim": "Demanda"},
    {"id": 2, "texto": "No final do dia, você se sente muito cansado ou 'esgotado' mentalmente pelo serviço?", "dim": "Demanda"},
    {"id": 3, "texto": "A chefia te entrega tarefas com prazos que são impossíveis de cumprir?", "dim": "Demanda"},
    {"id": 4, "texto": "Você precisa deixar coisas importantes sem fazer porque tem trabalho demais acumulado?", "dim": "Demanda"},
    {"id": 5, "texto": "O seu trabalho exige que você fique 'ligado' ou concentrado por tempo demais sem parar?", "dim": "Demanda"},
    {"id": 6, "texto": "Você pode dar sua opinião sobre como o trabalho do seu setor é organizado?", "dim": "Controle"},
    {"id": 7, "texto": "Você consegue escolher a ordem das tarefas que vai fazer durante o seu turno?", "dim": "Controle"},
    {"id": 8, "texto": "O seu trabalho te ensina coisas novas ou te ajuda a crescer como profissional?", "dim": "Controle"},
    {"id": 9, "texto": "Se você precisar de 5 minutos para ir ao banheiro ou tomar água, você consegue sair?", "dim": "Controle"},
    {"id": 10, "texto": "A empresa te escuta antes de mudar alguma regra que afeta o seu dia a dia?", "dim": "Controle"},
    {"id": 11, "texto": "Se o bicho pegar no serviço, você sente que seus colegas te ajudam?", "dim": "Suporte"},
    {"id": 12, "texto": "O seu encarregado ou supervisor te ajuda a resolver problemas de trabalho?", "dim": "Suporte"},
    {"id": 13, "texto": "Alguém te avisa se o seu trabalho está sendo bem feito ou se precisa melhorar?", "dim": "Suporte"},
    {"id": 14, "texto": "As ferramentas, EPIs e materiais que você precisa estão sempre na mão?", "dim": "Suporte"},
    {"id": 15, "texto": "Você sente que a empresa valoriza o esforço que você faz no dia a dia?", "dim": "Suporte"},
    {"id": 16, "texto": "O pessoal do seu setor trabalha unido e se ajuda de verdade?", "dim": "Relacionamento"},
    {"id": 17, "texto": "Você sofre alguma pressão chata, fofoca ou falta de respeito de outros colegas?", "dim": "Relacionamento"},
    {"id": 18, "texto": "Quando rola uma briga ou desentendimento, a chefia resolve de um jeito justo?", "dim": "Relacionamento"},
    {"id": 19, "texto": "Existe respeito e educação entre todo mundo, desde o ajudante até o chefe?", "dim": "Relacionamento"},
    {"id": 20, "texto": "Você se sente bem-vindo e respeitado pelos seus companheiros de equipe?", "dim": "Relacionamento"},
    {"id": 21, "texto": "Você sabe exatamente o que a empresa espera do seu trabalho?", "dim": "Papel"},
    {"id": 22, "texto": "As suas obrigações são bem explicadas ou você fica em dúvida do que é sua função?", "dim": "Papel"},
    {"id": 23, "texto": "Acontece de um chefe mandar uma coisa e outro chefe mandar outra diferente?", "dim": "Papel"},
    {"id": 24, "texto": "Você entende por que o seu trabalho é importante para o resultado da empresa?", "dim": "Papel"},
    {"id": 25, "texto": "Você tem permissão para resolver os probleminhas que aparecem na sua frente?", "dim": "Papel"},
    {"id": 26, "texto": "A empresa te avisa com antecedência se for mudar seu horário ou sua equipe?", "dim": "Mudança"},
    {"id": 27, "texto": "A chefia te pergunta o que você acha antes de mudar o seu jeito de trabalhar?", "dim": "Mudança"},
    {"id": 28, "texto": "Quando chega uma máquina ou tecnologia nova, explicam bem como usar antes de começar?", "dim": "Mudança"},
    {"id": 29, "texto": "Você sente que seu emprego está garantido e que não será mandado embora logo?", "dim": "Mudança"},
    {"id": 30, "texto": "Quando muda alguma regra ou ferramenta, a chefia te treina e te ajuda a se adaptar?", "dim": "Mudança"}
]

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "À vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    cliente_id = request.args.get('cliente', 'UNISAFE').strip().lower()
    try:
        r = requests.get(f"{URL_GOOGLE}?cliente={cliente_id}", timeout=10)
        setores = r.json().get('setores', ["Geral", "Administrativo", "Operacional"])
    except:
        setores = ["Geral", "Administrativo", "Operacional"]
    nome_exibicao = cliente_id.replace("_", " ").title()
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=nome_exibicao)

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    setor_escolhido = request.form.get('setor')
    respostas = {f"q{q['id']}": request.form.get(f"q{q['id']}") for q in QUESTOES}
    total = sum(int(v) for v in respostas.values() if v)
    status = "ALERTA" if total >= 60 else "OK"

    try:
        dados_envio = {"cliente": cliente_final, "setor": setor_escolhido, "pontuacao": total, "status": status}
        requests.post(URL_GOOGLE, data=json.dumps(dados_envio), timeout=10)
    except:
        pass

    # EM VEZ DE GERAR PDF, REDIRECIONA PARA PÁGINA DE SUCESSO
    return "<h1>Pesquisa enviada com sucesso!</h1><p>Obrigado por participar. Suas respostas foram registradas com segurança.</p>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
