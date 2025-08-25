import streamlit as st
import pandas as pd
import plotly.express as px


# Configuração da página
st.set_page_config(
    page_title="Dashboard de Jogos | 1980 - 2017",
    page_icon="🎮",
    layout="wide",
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Carregamento dos dados
df = pd.read_csv("https://raw.githubusercontent.com/MatheusFernandesCarillo/jogos-analise/main/Video_Games_Sales_as_at_22_Dec_2016.csv")

# Renomear colunas
df.columns = [
    "Nome", "Plataforma", "Lançamento", "Genero", "Publicadora",
    "Vendas_EUA", "Vendas_Europa", "Vendas_Japão", "Vendas_Outros",
    "Vendas_Global", "Nota_Critica", "Contagem_Criticos",
    "Nota_Usuario", "Contagem_Usuarios", "Desenvolvedora", "Classificação"
]

# Limpeza dos dados
df_limpo = df.drop(columns=['Nota_Critica', 'Contagem_Criticos', 'Nota_Usuario', 'Contagem_Usuarios'])
df_limpo['Lançamento'] = df_limpo['Lançamento'].fillna(0).astype(int)
df_limpo = df_limpo[df_limpo['Lançamento'] != 0]
df_limpo = df_limpo.dropna(subset=['Genero'])

# Filtros na sidebar
st.sidebar.header("🔍 Filtros")

# Filtro de regiões (novo)
regioes = {
    'Global': 'Vendas_Global',
    'América do Norte': 'Vendas_EUA',
    'Europa': 'Vendas_Europa',
    'Japão': 'Vendas_Japão',
    'Resto do Mundo': 'Vendas_Outros'
}
regiao_selecionada = st.sidebar.selectbox(
    "Região para análise:",
    options=list(regioes.keys()),
    index=0
)
coluna_vendas = regioes[regiao_selecionada]

# Filtros existentes (mantidos)
anos_disponiveis = sorted(df_limpo['Lançamento'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis)

plataformas_disponiveis = sorted(df_limpo['Plataforma'].unique())
plataformas_selecionadas = st.sidebar.multiselect("Plataforma", plataformas_disponiveis)

generos_disponiveis = sorted(df_limpo['Genero'].unique())
generos_selecionados = st.sidebar.multiselect("Genero", generos_disponiveis)

# Aplicar filtros
df_filtrado = df_limpo.copy()
if anos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Lançamento'].isin(anos_selecionados)]
if plataformas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Plataforma'].isin(plataformas_selecionadas)]
if generos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Genero'].isin(generos_selecionados)]

dados = df_filtrado if not df_filtrado.empty else df_limpo

# Exibição
st.title("🎲 Dashboard de Análise de Jogos")
st.markdown(f"**Região selecionada:** {regiao_selecionada}")

# Métricas gerais (atualizadas para usar coluna_vendas)
st.subheader("Métricas gerais")

col1, col2, col3, col4 = st.columns(4)

# Métrica 1: Ano com mais lançamentos
jogos_por_ano = dados['Lançamento'].value_counts().reset_index()
jogos_por_ano.columns = ['Ano', 'Quantidade']
ano_top = jogos_por_ano.loc[jogos_por_ano['Quantidade'].idxmax()]
col1.metric("Ano com mais lançamentos", ano_top['Ano'])

# Métrica 2: Total de jogos no ano de pico
col2.metric("Total de jogos nesse ano", ano_top['Quantidade'])

# Métrica 3: Gênero mais vendido (agora usando a região selecionada)
genero_top = dados.groupby('Genero')[coluna_vendas].sum().idxmax()
col3.metric("Gênero mais vendido", genero_top)

# Métrica 4: Plataforma líder (agora usando a região selecionada)
plataforma_top = dados.groupby('Plataforma')[coluna_vendas].sum().idxmax()
col4.metric("Plataforma líder", plataforma_top)

# Divisão visual
st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" />""", 
            unsafe_allow_html=True)

# Gráficos (atualizados para usar coluna_vendas)
st.subheader("Jogos Lançados")
col1, col2 = st.columns(2)

# Gráfico 1: Lançamentos por Plataforma (agora mostra vendas da região selecionada)
with col1:
    st.subheader(f"🕹️ Vendas por Plataforma ({regiao_selecionada})")
    vendas_plataforma = dados.groupby('Plataforma')[coluna_vendas].sum().nlargest(10).reset_index()
    fig1 = px.bar(
        vendas_plataforma,
        x='Plataforma',
        y=coluna_vendas,
        labels={coluna_vendas: 'Vendas (em milhões USD)'}
    )
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Lançamentos por Ano (agora mostra vendas da região selecionada)
with col2:
    st.subheader(f"📅 Vendas por Ano ({regiao_selecionada})")
    vendas_ano = dados.groupby('Lançamento')[coluna_vendas].sum().reset_index()
    fig2 = px.line(
        vendas_ano,
        x='Lançamento',
        y=coluna_vendas,
        labels={coluna_vendas: 'Vendas (em milhões USD)'}
    )
    st.plotly_chart(fig2, use_container_width=True)

# Divisão visual
st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" />""", 
            unsafe_allow_html=True)

# Análise de Franquias
st.subheader("🎯 Franquias Mais Lucrativas")

# Identificar franquias (extraindo do nome do jogo)
franquias_conhecidas = ['Call of Duty', 'FIFA', 'Mario', 'Pokémon', 'Grand Theft Auto', 
                        'The Sims', 'Need for Speed', 'Assassin', 'Final Fantasy', 'Halo']

# Função para identificar franquias
def identificar_franquia(nome):
    nome = nome.lower()
    for franquia in franquias_conhecidas:
        if franquia.lower() in nome:
            return franquia
    return 'Outras'

# Aplicar identificação de franquias
dados['Franquia'] = dados['Nome'].apply(identificar_franquia)

# Agrupar vendas por franquia
vendas_franquias = dados.groupby('Franquia')[coluna_vendas].sum().reset_index()
vendas_franquias = vendas_franquias.sort_values(coluna_vendas, ascending=False)

# Filtrar apenas franquias conhecidas (excluir 'Outras')
vendas_franquias_principais = vendas_franquias[vendas_franquias['Franquia'] != 'Outras']

# CORREÇÃO DO ERRO: Criar lista de cores manualmente
cores_especiais = {
    'Call of Duty': '#FF6B00',
    'FIFA': '#009688', 
    'Mario': '#E91E63',
    'Pokémon': '#FFC107'
}

# Criar lista de cores para cada franquia
cores = []
for franquia in vendas_franquias_principais.head(15)['Franquia']:
    if franquia in cores_especiais:
        cores.append(cores_especiais[franquia])
    else:
        cores.append('#2196F3')  # Cor padrão para as outras

# Gráfico de barras - CORREÇÃO AQUI
fig_franquias = px.bar(
    vendas_franquias_principais.head(15),
    x='Franquia',
    y=coluna_vendas,
    title=f'Top 15 Franquias em Vendas - {regiao_selecionada}',
    labels={coluna_vendas: 'Vendas (em milhões USD)', 'Franquia': 'Franquia'},
    color='Franquia'
)

# Aplicar as cores manualmente (MANEIRA CORRETA)
fig_franquias.update_traces(
    marker_color=cores,
    hovertemplate="<b>%{x}</b><br>Vendas: %{y:.2f}M<extra></extra>"
)

st.plotly_chart(fig_franquias, use_container_width=True)

# Métricas específicas das franquias mencionadas - VERSÃO CORRIGIDA
st.write("### 📊 Desempenho das Franquias Mencionadas")

# Criar ranking CORRETO baseado no gráfico (top 15)
ranking_correto = vendas_franquias_principais.head(15).reset_index(drop=True)
ranking_correto['Rank'] = ranking_correto.index + 1

col1, col2, col3, col4 = st.columns(4)

franquias_alvo = ['Call of Duty', 'FIFA', 'Mario', 'Pokémon']
for i, franquia in enumerate(franquias_alvo):
    # Buscar o ranking CORRETO da franquia
    rank_info = ranking_correto[ranking_correto['Franquia'] == franquia]
    
    if not rank_info.empty:
        total_vendas = rank_info[coluna_vendas].values[0]
        ranking_pos = rank_info['Rank'].values[0]
    else:
        total_vendas = 0
        ranking_pos = "N/A"
    
    with eval(f'col{i+1}'):
        st.metric(f"{franquia}", f"${total_vendas:,.0f}M", f"Rank: #{ranking_pos}")

# Análise detalhada por jogo dentro das franquias
st.write("### 🎮 Detalhamento por Jogo")

franquia_selecionada = st.selectbox(
    "Selecione uma franquia para detalhar:",
    options=franquias_alvo
)

if franquia_selecionada:
    jogos_franquia = dados[dados['Franquia'] == franquia_selecionada]
    top_jogos = jogos_franquia.sort_values(coluna_vendas, ascending=False).head(10)
    
    fig_detalhe = px.bar(
        top_jogos,
        x='Nome',
        y=coluna_vendas,
        title=f'Top 10 Jogos da Franquia {franquia_selecionada} - {regiao_selecionada}',
        labels={coluna_vendas: 'Vendas (em milhões USD)', 'Nome': 'Jogo'},
        hover_data=['Plataforma', 'Lançamento'],
        color_discrete_sequence=[cores_especiais.get(franquia_selecionada, '#2196F3')]
    )
    st.plotly_chart(fig_detalhe, use_container_width=True)
    
    # Estatísticas da franquia
    total_jogos = len(jogos_franquia)
    ano_primeiro = jogos_franquia['Lançamento'].min()
    ano_ultimo = jogos_franquia['Lançamento'].max()
    
    st.write(f"**Estatísticas da franquia {franquia_selecionada}:**")
    st.write(f"- Total de jogos: {total_jogos}")
    st.write(f"- Período: {ano_primeiro} - {ano_ultimo}")
    st.write(f"- Vendas médias por jogo: ${(jogos_franquia[coluna_vendas].sum()/total_jogos):.2f}M")

# Divisão visual
st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" />""", 
        unsafe_allow_html=True)

# Análise de Preferências Regionais por Gênero (Interativa)
st.subheader("🌍 Comparador de Preferências Regionais")

# DEFINIR regioes_comparacao AQUI (linha que estava faltando)
regioes_comparacao = {
    'América do Norte': 'Vendas_EUA',
    'Europa': 'Vendas_Europa', 
    'Japão': 'Vendas_Japão',
    'Resto do Mundo': 'Vendas_Outros',
    'Global': 'Vendas_Global'
}

# Filtros interativos
col1, col2 = st.columns(2)

with col1:
    genero_selecionado = st.selectbox(
        "Selecione o gênero:",
        options=sorted(dados['Genero'].unique())
    )

with col2:
    regiao_comparacao = st.selectbox(
        "Selecione a região para análise:",
        options=list(regioes_comparacao.keys())
    )

# O resto do código continua exatamente como estava...
# [TODO: Colar aqui todo o restante do código da análise regional]
# Dados para a análise
coluna_regiao = regioes_comparacao[regiao_comparacao]

# 1. Participação do gênero na região selecionada
vendas_regiao = dados.groupby('Genero')[coluna_regiao].sum()
participacao_genero = (vendas_regiao[genero_selecionado] / vendas_regiao.sum()) * 100

# 2. Comparação com outras regiões
participacoes = {}
for regiao_nome, regiao_col in regioes_comparacao.items():
    vendas_temp = dados.groupby('Genero')[regiao_col].sum()
    participacoes[regiao_nome] = (vendas_temp[genero_selecionado] / vendas_temp.sum()) * 100

# 3. Ranking do gênero em cada região
rankings = {}
for regiao_nome, regiao_col in regioes_comparacao.items():
    vendas_temp = dados.groupby('Genero')[regiao_col].sum().sort_values(ascending=False)
    rankings[regiao_nome] = list(vendas_temp.index).index(genero_selecionado) + 1

# Métricas principais
st.write(f"### 📊 {genero_selecionado} em {regiao_comparacao}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Participação", 
        f"{participacao_genero:.1f}%",
        f"Rank: #{rankings[regiao_comparacao]}"
    )

with col2:
    # Região onde o gênero é mais popular
    regiao_mais_popular = max(participacoes, key=participacoes.get)
    diferenca = participacoes[regiao_mais_popular] - participacao_genero
    if regiao_mais_popular != regiao_comparacao:
        st.metric("Mais popular em", regiao_mais_popular, f"+{diferenca:.1f}%")
    else:
        st.metric("Mais popular em", "Esta região", "🏆")

with col3:
    # Região onde o gênero é menos popular
    regiao_menos_popular = min(participacoes, key=participacoes.get)
    diferenca = participacao_genero - participacoes[regiao_menos_popular]
    if regiao_menos_popular != regiao_comparacao:
        st.metric("Menos popular em", regiao_menos_popular, f"-{diferenca:.1f}%")
    else:
        st.metric("Menos popular em", "Esta região", "⬇️")

# Gráfico de comparação entre regiões
df_comparacao = pd.DataFrame({
    'Região': list(participacoes.keys()),
    'Participação': list(participacoes.values()),
    'Ranking': [rankings[r] for r in participacoes.keys()]
})

fig_comparacao = px.bar(
    df_comparacao,
    x='Região',
    y='Participação',
    title=f'Participação de {genero_selecionado} por Região (%)',
    labels={'Participação': 'Participação (%)', 'Região': ''},
    color='Participação',
    color_continuous_scale='Blues',
    hover_data=['Ranking']
)

# Destacar a região selecionada
cores = ['#FF6B00' if regiao == regiao_comparacao else '#1f77b4' for regiao in df_comparacao['Região']]
fig_comparacao.update_traces(marker_color=cores)

st.plotly_chart(fig_comparacao, use_container_width=True)

# Top jogos do gênero na região selecionada
st.write(f"### 🎮 Top 5 Jogos de {genero_selecionado} em {regiao_comparacao}")

top_jogos = dados[dados['Genero'] == genero_selecionado].sort_values(
    coluna_regiao, ascending=False
).head(5)[['Nome', 'Plataforma', 'Lançamento', coluna_regiao]]

# Formatar tabela
top_jogos[coluna_regiao] = top_jogos[coluna_regiao].apply(lambda x: f"${x:.2f}M")
top_jogos.columns = ['Jogo', 'Plataforma', 'Ano', 'Vendas']

st.dataframe(top_jogos, hide_index=True)

# Gráficos lado a lado - EVOLUÇÃO e COMPARAÇÃO
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    # Evolução temporal do gênero
    st.write(f"#### 📈 Evolução em {regiao_comparacao}")
    evolucao = dados[dados['Genero'] == genero_selecionado].groupby('Lançamento')[coluna_regiao].sum().reset_index()
    
    if not evolucao.empty:
        fig_evolucao = px.line(
            evolucao,
            x='Lançamento',
            y=coluna_regiao,
            title=f'Evolução de {genero_selecionado}',
            labels={coluna_regiao: 'Vendas (USD)', 'Lançamento': 'Ano'}
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.info(f"Sem dados de evolução para {genero_selecionado}")

with col_graf2:
    # Comparação com outros gêneros
    st.write(f"#### 🔄 Comparação com Outros Gêneros")
    vendas_por_genero = dados.groupby('Genero')[coluna_regiao].sum().sort_values(ascending=False).reset_index()
    vendas_por_genero['Participação'] = (vendas_por_genero[coluna_regiao] / vendas_por_genero[coluna_regiao].sum()) * 100
    
    fig_generos = px.bar(
        vendas_por_genero.head(8),  # Top 8 para caber melhor
        x='Genero',
        y='Participação',
        title='Participação dos Gêneros (%)',
        labels={'Participação': 'Participação (%)', 'Genero': 'Gênero'}
    )
    
    # Destacar o gênero selecionado
    cores_generos = ['#FF6B00' if gen == genero_selecionado else '#1f77b4' for gen in vendas_por_genero.head(8)['Genero']]
    fig_generos.update_traces(marker_color=cores_generos)
    fig_generos.update_layout(xaxis_tickangle=45)  # Girar labels para melhor visualização
    
    st.plotly_chart(fig_generos, use_container_width=True)

