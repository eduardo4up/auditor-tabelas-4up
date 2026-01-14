import streamlit as st
import pandas as pd
import base64
import io
from openai import OpenAI

# 1. Configuração da Página e Estilo Visual (CSS Customizado)
st.set_page_config(page_title="Auditor de Tabelas Profissional", layout="wide")

st.markdown("""
    <style>
    /* Estilizando o campo de texto para parecer um editor profissional */
    .stTextArea textarea {
        background-color: #1E1E2E !important;
        color: #D9E0EE !important;
        border: 2px solid #96CDFB !important;
        border-radius: 10px !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização da API (Substitua pela sua chave)
client = OpenAI(api_key="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")

def encode_image(uploaded_file):
    """Converte o arquivo de imagem para Base64 para a API de Visão."""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

st.title("🔍 Auditor Técnico de Tabelas")
st.write("A área de colagem agora ocupa toda a largura, com o upload do print logo abaixo.")

# --- SEÇÃO 1: ÁREA DE COLAGEM (LARGURA TOTAL) ---
st.subheader("1. Cole a Tabela Aqui (Word ou Excel)")
# Removendo colunas para ocupar a horizontal inteira
texto_puro = st.text_area(
    "Área de colagem técnica:", 
    height=250, 
    placeholder="Selecione no Word/Excel, copie (Ctrl+C) e cole aqui (Ctrl+V)...", 
    key="area_tabela"
)

tabela_formatada_ia = ""
if texto_puro:
    try:
        # Lógica para identificar a tabela do Excel/Word via tabulações (\t)
        df = pd.read_csv(io.StringIO(texto_puro), sep='\t')
        st.success("✅ Tabela identificada e processada!")
        st.dataframe(df, use_container_width=True) # Exibe a tabela formatada ocupando toda a tela
        tabela_formatada_ia = df.to_string(index=False)
    except Exception:
        st.warning("⚠️ Formato de tabela não estruturado detectado. A IA analisará como texto simples.")
        tabela_formatada_ia = texto_puro

st.divider() # Linha visual para separar as seções

# --- SEÇÃO 2: ÁREA DO PRINT (LARGURA TOTAL) ---
st.subheader("2. Upload do Print da Tabela")
arquivo_imagem = st.file_uploader("Suba o arquivo de imagem (PNG, JPG ou JPEG):", type=["png", "jpg", "jpeg"])

if arquivo_imagem:
    # A imagem agora aparece abaixo da tabela ocupando a largura disponível
    st.image(arquivo_imagem, caption="Visualização do Print Enviado", use_container_width=True)

st.divider()

# --- SEÇÃO 3: BOTÃO DE AÇÃO E RESULTADOS ---
# O botão também ocupará a largura total para manter a consistência do layout
if st.button("🚀 Iniciar Auditoria Técnica", use_container_width=True):
    if not tabela_formatada_ia or not arquivo_imagem:
        st.error("ERRO: É necessário colar a tabela e fazer o upload do print para continuar.")
    else:
        with st.spinner("Analisando e comparando os dados..."):
            try:
                base64_image = encode_image(arquivo_imagem)
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "Você é um auditor de dados técnicos. Compare a tabela de texto fornecida "
                                "com a imagem enviada. Verifique se todos os valores, modelos e potências correspondem. "
                                "Responda se os dados conferem ou descreva as divergências com precisão."
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Dados da tabela colada:\n{tabela_formatada_ia}"},
                                {
                                    "type": "image_url", 
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                                }
                            ],
                        }
                    ],
                )
                
                st.subheader("📋 Relatório da Auditoria")
                st.info(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Erro ao processar a requisição na API: {e}")