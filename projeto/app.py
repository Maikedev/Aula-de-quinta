from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import init_db, save_data, get_all_data
import plotly.express as px
import pandas as pd

app = Flask(__name__)

# Inicializar banco de dados
init_db()

# Função de resposta para o chatbot
def responder_pergunta(pergunta):
    pergunta = pergunta.lower()
    if "sintomas" in pergunta:
        return "Os sintomas mais comuns registrados incluem febre, tosse, dor de cabeça e fadiga. Você pode verificar o gráfico no dashboard."
    elif "região" in pergunta:
        return "A maior parte dos registros vem das regiões Sudeste e Nordeste, conforme mostrado no gráfico de regiões."
    elif "idade" in pergunta:
        return "Os dados indicam que a maioria dos registros é de pessoas entre 20 e 40 anos de idade."
    elif "ajuda" in pergunta or "sobre" in pergunta:
        return "Este chatbot pode responder perguntas sobre os gráficos de sintomas, regiões, idades e outros dados coletados no formulário."
    else:
        return "Desculpe, não entendi a pergunta. Tente perguntar sobre sintomas, regiões ou idades."

# Rota para o chatbot
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    pergunta = data.get("pergunta", "")
    resposta = responder_pergunta(pergunta)
    return jsonify({"resposta": resposta})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    idade = int(request.form['idade'])
    genero = request.form['genero']
    regiao = request.form['regiao']
    sintomas = request.form['sintomas']

    save_data(nome, idade, genero, regiao, sintomas)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    global df  # Tornar o DataFrame acessível globalmente
    data = get_all_data()
    df = pd.DataFrame(data, columns=['id', 'nome', 'idade', 'genero', 'regiao', 'sintomas', 'data_envio'])

    # Gráficos
    custom_colors = px.colors.qualitative.Set2

    genero_fig = px.pie(df, names='genero', title="Distribuição por Gênero", hole=0.4, color_discrete_sequence=custom_colors)
    idade_fig = px.histogram(df, x='idade', nbins=10, title="Distribuição de Idades", color_discrete_sequence=custom_colors)
    regiao_fig = px.bar(
        df['regiao'].value_counts().reset_index(),
        x='regiao', y='count',
        title="Distribuição por Região",
        labels={"index": "Região", "regiao": "Quantidade"},
        color_discrete_sequence=custom_colors
    )

    sintomas_series = df['sintomas'].str.split(',').explode().str.strip().dropna()
    sintomas_count = sintomas_series.value_counts().reset_index()
    sintomas_count.columns = ['Sintoma', 'Frequência']

    sintomas_fig = px.bar(
        sintomas_count.head(10),
        x='Frequência',
        y='Sintoma',
        orientation='h',
        title="Sintomas Mais Comuns",
        color_discrete_sequence=custom_colors
    )

    return render_template(
        'dashboard.html',
        genero_plot=genero_fig.to_html(full_html=False),
        idade_plot=idade_fig.to_html(full_html=False),
        regiao_plot=regiao_fig.to_html(full_html=False),
        sintomas_plot=sintomas_fig.to_html(full_html=False)
    )


def responder_pergunta(pergunta):
    """
    Gera uma resposta baseada na análise dos dados do DataFrame `df`.
    """
    global df  # Certifique-se de que o DataFrame é acessível
    pergunta = pergunta.lower()

    # Verifica se o DataFrame está carregado
    if df.empty:
        return "Os dados ainda não foram carregados. Por favor, insira algumas informações no formulário."

    try:
        if "sintomas" in pergunta:
            if "região" in pergunta or "regiao" in pergunta:
                sintomas_series = df[['regiao', 'sintomas']].copy()
                sintomas_series['sintomas'] = sintomas_series['sintomas'].str.split(',').explode().str.strip()

                # Agrupar por região e contar sintomas
                regioes_sintomas = sintomas_series.groupby('regiao')['sintomas'].count().reset_index()
                regioes_sintomas = regioes_sintomas.sort_values(by='sintomas', ascending=False)

                resposta = "As regiões com mais registros de sintomas são:\n"
                resposta += "\n".join(f"{linha['regiao']}: {linha['sintomas']} registros"
                                       for _, linha in regioes_sintomas.iterrows())
                return resposta
            else:
                top_sintomas = df['sintomas'].str.split(',').explode().str.strip().value_counts().head(3)
                resposta = "Os sintomas mais comuns registrados são: "
                resposta += ', '.join(f"{sintoma} ({freq} ocorrências)" for sintoma, freq in top_sintomas.items())
                return resposta

        elif "região" in pergunta or "regiao" in pergunta:
            regiao_mais_comum = df['regiao'].value_counts().idxmax()
            freq_regiao = df['regiao'].value_counts().max()
            return f"A região com mais registros é {regiao_mais_comum}, com {freq_regiao} ocorrências."

        elif "idade" in pergunta:
            if "região" in pergunta or "regiao" in pergunta:
                # Calcular a média de idade por região
                media_idade_por_regiao = df.groupby('regiao')['idade'].mean()
                resposta = "A média de idade por região é:\n"
                resposta += "\n".join(f"{regiao}: {idade:.1f} anos" for regiao, idade in media_idade_por_regiao.items())
                return resposta
            else:
                idade_media = df['idade'].mean()
                return f"A idade média dos participantes é {idade_media:.1f} anos."

        elif "gênero" in pergunta or "genero" in pergunta:
            genero_count = df['genero'].value_counts()
            resposta = "A distribuição por gênero é a seguinte: "
            resposta += ', '.join(f"{genero}: {freq}" for genero, freq in genero_count.items())
            return resposta

        elif "ajuda" in pergunta or "sobre" in pergunta:
            return "Este chatbot pode responder perguntas sobre os gráficos de sintomas, regiões, idades, gêneros e outros dados coletados no formulário."

        else:
            return "Desculpe, não entendi a pergunta. Tente perguntar sobre sintomas, regiões, idades ou gêneros."
    except Exception as e:
        return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"



if __name__ == '__main__':
    app.run(debug=True)
