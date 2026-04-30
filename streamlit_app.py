import streamlit as st
import matplotlib.pyplot as plt
import os
from script_processamento import pipeline

# CONFIG DA PÁGINA
st.set_page_config(
    page_title="Análise de Planos",
    layout="wide"
)

st.sidebar.info("MapReduce + Streamlit")

pagina = st.sidebar.radio(
    "Navegação",
    ["Análise Individual", "Comparação (futuro)"]
)

st.sidebar.markdown("---")


# =========================
# PÁGINA PRINCIPAL
# =========================
if pagina == "Análise Individual":

    st.title("Análise de Planos de Governo")

    pasta_dados = "dados"

    if not os.path.exists(pasta_dados):
        st.error("Pasta 'dados' não encontrada!")
        st.stop()

    arquivos = [f for f in os.listdir(pasta_dados) if f.lower().endswith(".pdf")]

    if not arquivos:
        st.warning("Nenhum PDF encontrado na pasta /dados")
        st.stop()

    # =========================
    # TOPO COM COLUNAS (LAYOUT HORIZONTAL)
    # =========================
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        arquivo_escolhido = st.selectbox("Escolha o candidato", arquivos)

    with col2:
        top_n = st.selectbox("Top palavras", [5, 10, 15, 20])
        index=1

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        gerar = st.button("Gerar Análise", use_container_width=True)

    # =========================
    # PROCESSAMENTO
    # =========================
    if gerar:

        caminho = os.path.join(pasta_dados, arquivo_escolhido)

        with st.spinner("Processando... "):
            df, texto = pipeline(caminho, top_n)

        st.success("Análise concluída!")

        
        col_grafico, col_tabela = st.columns(2)

        
        with col_grafico:
            st.subheader("Gráfico")

            fig, ax = plt.subplots()
            ax.barh(df["palavra"], df["frequencia"], color="#4E79A7")
            

            ax.set_title(f"{arquivo_escolhido}")
            ax.set_xlabel("Palavras")
            ax.set_ylabel("Frequência")

            plt.xticks(rotation=45)

            st.pyplot(fig)
            
        with col_tabela:
            st.subheader("Dados")
            st.dataframe(df, hide_index=True, use_container_width=True)


        # TEXTO (EXTRA)
        with st.expander("Ver texto extraído"):
            st.write(texto[:10000])

# =========================
# PÁGINA: COMPARAÇÃO
# =========================
elif pagina == "Comparação (futuro)":

    st.title("Comparação entre Candidatos")

    pasta_dados = "dados"

    if not os.path.exists(pasta_dados):
        st.error("Pasta 'dados' não encontrada!")
        st.stop()

    arquivos = [f for f in os.listdir(pasta_dados) if f.lower().endswith(".pdf")]

    if not arquivos:
        st.warning("Nenhum PDF encontrado na pasta /dados")
        st.stop()

    col1, col2 = st.columns([3, 1])

    with col1:
        arquivos_escolhidos = st.multiselect(
            "Escolha até 3 candidatos",
            arquivos,
            max_selections=3
        )

    with col2:
        top_n = st.selectbox("Top palavras", [5, 10, 15, 20], index=1)

    gerar = st.button("Gerar Comparação", use_container_width=True)

    if gerar:

        if len(arquivos_escolhidos) != 3:
            st.warning("Selecione exatamente 3 candidatos")
            st.stop()

        import pandas as pd

        with st.spinner("Processando comparação..."):

            dfs = []

            for arq in arquivos_escolhidos:
                caminho = os.path.join(pasta_dados, arq)
                df, _ = pipeline(caminho, top_n)
                df["candidato"] = arq.replace(".pdf", "")
                dfs.append(df)

            df_final = pd.concat(dfs)

        st.success("Comparação pronta!")

        # =========================
        # 🥉 GRÁFICOS INDIVIDUAIS (EMPILHADOS)
        # =========================
        st.subheader("Análise individual")

        cores = ["#4E79A7", "#F28E2B", "#59A14F"]

        for i, arq in enumerate(arquivos_escolhidos):

            df = dfs[i].sort_values(by="frequencia", ascending=True)

            st.markdown(f"### {arq.replace('.pdf', '')}")

            altura = max(1.5, len(df) * 0.25)

            fig2, ax2 = plt.subplots(figsize=(8, altura))

            ax2.barh(
                df["palavra"],
                df["frequencia"],
                color=cores[i]
            )

            ax2.set_title("Top palavras")
            ax2.set_xlabel("Frequência")
            ax2.set_ylabel("Palavras")

            for j, v in enumerate(df["frequencia"]):
                ax2.text(v + 1, j, str(v), va='center')

            plt.tight_layout()

            st.pyplot(fig2, use_container_width=True)

            st.markdown("---")

        # =========================
        # 🥇 GRÁFICO COMPARATIVO FINAL
        # =========================
        st.subheader("Palavras mais usadas no geral")

        total_palavras = (
            df_final.groupby("palavra")["frequencia"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )

        df_filtrado = df_final[
            df_final["palavra"].isin(total_palavras.index)
        ]

        pivot = df_filtrado.pivot(
            index="palavra",
            columns="candidato",
            values="frequencia"
        ).fillna(0)

        pivot["total"] = pivot.sum(axis=1)
        pivot = pivot.sort_values("total", ascending=True).drop(columns="total")

        altura = max(2, len(pivot) * 0.25)

        fig1, ax1 = plt.subplots(figsize=(8, altura))

        pivot.plot(
            kind="barh",
            stacked=True,
            ax=ax1,
            width=0.6,
            color=cores[:len(pivot.columns)]
        )

        ax1.set_title("Distribuição das palavras entre candidatos")
        ax1.set_xlabel("Frequência total")
        ax1.set_ylabel("Palavras")

        ax1.tick_params(axis='y', labelsize=8)
        ax1.tick_params(axis='x', labelsize=8)

        plt.tight_layout()

        st.pyplot(fig1, use_container_width=True)