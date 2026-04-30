import pdfplumber
import re
from collections import Counter
import pandas as pd

stopwords = {
    "o","a","os","as","um","uma","uns","umas",
    "de","da","do","das","dos","e","em","para",
    "com","por","no","na","nos","nas","que", "não",
    "se", "é", "ao", "às", "como", "mas","foi", "ser", 
    "ter", "está",
}

def extrair_texto_pdf(caminho_pdf):
    texto_completo = ""

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"

    return texto_completo

def preprocessar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    
    palavras = texto.split()
    
    palavras = [
        p for p in palavras 
        if p not in stopwords and len(p) > 2
    ]
    
    return palavras

def pipeline(caminho_pdf, top_n=10):
    texto = extrair_texto_pdf(caminho_pdf)
    palavras = preprocessar_texto(texto)
    
    contador = Counter(palavras)
    
    df = pd.DataFrame(contador.items(), columns=["palavra", "frequencia"])
    df = df.sort_values(by="frequencia", ascending=False).head(top_n)
    
    return df, texto