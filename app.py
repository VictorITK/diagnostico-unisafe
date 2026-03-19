from Flask import Flask, render_template, request, make_response
import requests
import json
import os

app = Flask(__name__)

# URL do seu Google Apps Script (Certifique-se de que é a URL mais recente)
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzR6SGpx47m2tuOGRkHrG3qt2aMFrBcR1JXtTk04WV2Sf82xtt2F9JyVSM3yS5FAPMN/exec"

# Inteligência baseada no Guia de Riscos Psicossociais da NR-01
MAPA_RISCOS = {
    "Demanda": {"perigo": "Excesso de demandas no trabalho (sobrecarga)", "consequencia": "Transtorno mental; DORT; Fadiga", "medida": "Priorização de tarefas; pausas regulares; redimensionamento de equipe."},
    "Controle": {"perigo": "Baixo controle no trabalho / Falta de autonomia", "consequencia": "Transtorno mental; DORT", "medida": "Aumentar participação na organização; permitir resolução de problemas no posto."},
    "Suporte": {"perigo": "Falta de suporte/apoio no trabalho", "consequencia": "Transtorno mental", "medida": "Canais de diálogo com chefia; suporte gerencial ativo; comunicação interna."},
    "Relacionamento": {"perigo": "Maus relacionamentos / Assédio", "consequencia": "Transtorno mental", "medida": "Código de ética; mediação de conflitos; canais de denúncia seguros."},
    "Papel": {"perigo": "Baixa clareza de papel/função", "consequencia": "Transtorno mental", "medida": "Definição clara de atribuições; revisões de metas; treinamento de fluxo."},
    "Mudanca": {"perigo": "Má gestão de mudanças organizacionais", "consequencia": "Transtorno mental; DORT", "medida": "Comunicação antecipada; treinamentos prévios; escuta ativa antes da implementação."}
}

# 30 Questões categorizadas
QUESTOES = [
    {"id": 1, "texto": "Você precisa trabalhar muito rápido?", "dim": "Demanda"},
    {"id": 2, "texto": "Seu trabalho exige muito esforço emocional?", "dim": "Demanda"},
    {"id": 3, "texto": "Você tem tempo suficiente para concluir suas tarefas?", "dim": "Demanda"},
    {"id": 4, "texto": "O volume de trabalho é excessivo?", "dim": "Demanda"},
    {"id": 5, "texto": "Você precisa trabalhar horas extras com frequência?", "dim": "Demanda"},
    {"id": 6, "texto": "Você pode influenciar a quantidade de trabalho que recebe?", "dim": "Controle"},
    {"id": 7, "texto": "Você tem voz sobre como o trabalho é organizado?", "dim": "Controle"},
    {"id": 8, "texto": "Você pode escolher o seu ritmo de trabalho?", "dim": "Controle"},
    {"id": 10, "texto": "Você tem autonomia para tomar decisões importantes?", "dim": "Controle"},
    {"id": 11, "texto": "Seus colegas ouvem seus problemas de trabalho?", "dim": "Suporte"},
    {"id": 12, "texto": "Você recebe apoio dos colegas quando precisa?", "dim": "Suporte"},
    {"id": 13, "texto": "Seu superior direto apoia o seu desenvolvimento?", "dim": "Suporte"},
    {"id": 14, "topo": "O supervisor ajuda a planejar bem as tarefas?", "dim": "Suporte"},
    {"id": 15, "texto": "A empresa oferece recursos necessários para o trabalho?", "dim": "Suporte"},
    {"id": 16, "texto": "Existe colaboração na sua equipe?", "dim": "Relacionamento"},
    {"id": 17, "texto": "Você se sente respeitado no ambiente de trabalho?", "dim": "Relacionamento"},
    {"id": 18, "texto": "Existem conflitos constantes entre os colegas?", "dim": "Relacionamento"},
    {"id": 19, "texto": "Você já presenciou falta de ética no trabalho?", "dim": "Relacionamento"},
    {"id": 20, "texto": "A comunicação interna é clara e educada?", "dim": "Relacionamento"},
    {"id": 21, "texto": "Você sabe exatamente suas responsabilidades?", "dim": "Papel"},
    {"id": 22, "texto": "Seus objetivos de trabalho são claros?", "dim": "Papel"},
    {"id": 23, "texto": "Você recebe ordens conflitantes?", "dim": "Papel"},
    {"id": 24, "texto": "Você entende como seu trabalho ajuda a empresa?", "dim": "Papel"},
    {"id": 25, "texto": "As expectativas sobre seu cargo são bem definidas?", "dim": "Papel"},
    {"id": 26, "texto": "A empresa avisa mudanças com antecedência?", "dim": "Mudanca"},
    {"id": 27, "texto": "Você é consultado antes de mudanças no seu posto?", "dim": "Mudanca"},
    {"id": 28, "topo": "Há treinamento quando algo novo é implementado?", "dim": "Mudanca"},
    {"id": 29, "texto": "As mudanças recentes foram bem planejadas?", "dim": "Mudanca"},
    {"id": 30, "texto": "Você se sente seguro quanto ao futuro na empresa?", "dim": "Mudanca"}
]

# Ajuste da questão 9 que estava faltando
QUESTOES.insert(8, {"id": 9, "texto": "O trabalho permite que você aprenda coisas novas?", "dim": "Controle"})

OPCOES = [("0", "Nunca"), ("1", "Raramente"), ("2", "Às vezes"), ("3", "Frequentemente"), ("4", "Sempre")]

@app.route('/')
def index():
    # Pega o cliente da URL (ex: ?cliente=usaplas)
    cliente_id = request.args.get('cliente', 'UNISAFE').strip().lower()
    
    # Busca setores e modo no Google Sheets
    try:
        r = requests.get(f"{URL_GOOGLE}?cliente={cliente_id}", timeout=10)
        dados = r.json()
        setores = dados.get('setores', ["Geral"])
        modo_cliente = dados.get('modo', 'individual').lower()
    except:
        setores, modo_cliente = ["Geral"], "individual"

    # VERIFICAÇÃO DO BLOQUEIO: Se o modo for individual e já tiver o cookie, bloqueia
    if modo_cliente == "individual" and request.cookies.get(f'participou_{cliente_id}'):
        return render_template('bloqueado.html', cliente=cliente_id.title())

    # Passa o 'modo' para o HTML decidir se mostra o botão 'Próximo'
    return render_template('index.html', questoes=QUESTOES, opcoes=OPCOES, setores=setores, cliente=cliente_id.title(), modo=modo_cliente)

@app.route('/enviar', methods=['POST'])
def enviar():
    cliente_final = request.form.get('cliente_escondido', 'UNISAFE')
    modo_final = request.form.get('modo_escondido', 'individual')
    setor_escolhido = request.form.get('setor')
    
    # Cálculo da pontuação por dimensão e total
    pontos_por_dim = {d: 0 for d in MAPA_RISCOS.keys()}
    total = 0
    for q in QUESTOES:
        val = int(request.form.get(f"q{q['id']}", 0))
        pontos_por_dim[q['dim']] += val
        total += val

    # Critério UNISAFE de Classificação de Risco (0-120)
    if total <= 40: status_texto = "BAIXO"
    elif total <= 80: status_texto = "MODERADO (ALERTA)"
    else: status_texto = "CRÍTICO (URGENTE)"

    # Identifica a dimensão mais crítica para o PGR
    dim_critica = max(pontos_por_dim, key=pontos_por_dim.get)
    info_risco = MAPA_RISCOS[dim_critica]

    # Envia dados para a Planilha do Google
    try:
        dados_envio = {
            "cliente": cliente_final,
            "setor": setor_escolhido,
            "pontuacao": total,
            "status": status_texto,
            "perigo": info_risco["perigo"],
            "consequencia": info_risco["consequencia"],
            "medida": info_risco["medida"]
        }
        requests.post(URL_GOOGLE, data=json.dumps(dados_envio), timeout=10)
        
        # Página de sucesso personalizada conforme o modo
        btn_proximo = f"<br><br><a href='/?cliente={cliente_final}' style='padding:15px; background:#004a87; color:white; text-decoration:none; border-radius:5px; font-weight:bold;'>PRÓXIMO COLABORADOR</a>" if modo_final == "totem" else ""
        
        resp = make_response(f"""
            <div style='text-align:center; padding:50px; font-family:sans-serif; background-color:#f0f2f5; height:100vh;'>
                <div style='background:white; padding:40px; border-radius:15px; box-shadow:0 4px 6px rgba(0,0,0,0.1); display:inline-block;'>
                    <h1 style='color:#004a87;'>Sucesso!</h1>
                    <p>Sua participação foi registrada anonimamente. A <strong>UNISAFE</strong> agradece sua colaboração para um ambiente mais seguro.</p>
                    {btn_proximo}
                </div>
            </div>
        """)
        
        # ATIVAÇÃO DO BLOQUEIO: Se o modo for individual, grava o cookie por 30 dias
        if modo_final == "individual":
            resp.set_cookie(f'participou_{cliente_final}', 'sim', max_age=60*60*24*30)
        
        return resp
    except:
        return "<div style='text-align:center; padding:50px;'><h1>Erro ao enviar</h1><p>Houve um problema. Por favor, tente novamente.</p></div>"

if __name__ == '__main__':
    app.run(debug=True)
