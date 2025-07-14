
from flask import Flask, render_template, request, send_file
import subprocess
import requests
from fpdf import FPDF
import datetime
import json
import os
import sys
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


app = Flask(__name__)

# ==== CONFIGURAÇÕES INICIAIS ====

# ==== MÓDULO 1: ENUMERAÇÃO ATIVA COM NMAP ====
def modulo_nmap(target):
    try:
        result = subprocess.run(["nmap", "-sV", "-O", target], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"[ERRO] Nmap retornou um erro: {e.stderr}"
    except FileNotFoundError:
        return "[ERRO] Nmap não encontrado. Certifique-se de que está instalado e no PATH."
    except Exception as e:
        return f"[ERRO] ao executar Nmap: {e}"

# ==== MÓDULO 2: WHATWEB PARA COLETA PASSIVA ====
def modulo_passivo(target):
    try:
        result = subprocess.run(["whatweb", target], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"[ERRO] WhatWeb retornou um erro: {e.stderr}"
    except FileNotFoundError:
        return "[ERRO] WhatWeb não encontrado. Certifique-se de que está instalado e no PATH."
    except Exception as e:
        return f"[ERRO] ao executar WhatWeb: {e}"

# ==== MÓDULO 3: AMASS PARA ENUMERAÇÃO DE SUBDOMÍNIOS ====
def modulo_amass(target):
    try:
        result = subprocess.run(["amass", "enum", "-d", target], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"[ERRO] Amass retornou um erro: {e.stderr}"
    except FileNotFoundError:
        return "[ERRO] Amass não encontrado. Certifique-se de que está instalado e no PATH."
    except Exception as e:
        return f"[ERRO] ao executar Amass: {e}"
# ==== MÓDULO 4: ANÁLISE COM IA (GEMINI) ====
def modulo_gemini(texto_entrada):
    if not GEMINI_API_KEY:
        return "[ERRO] Chave da API Gemini não configurada. Defina a variável de ambiente GEMINI_API_KEY."
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Analise esse relatório de pentest e gere uma análise técnica profissional:\n\n{texto_entrada}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # Levanta um erro para status HTTP 4xx ou 5xx
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"[ERRO] na requisição à API Gemini: {e}"
    except Exception as e:
        return f"[ERRO] na resposta da IA: {e}"

# ==== RELATÓRIO PDF ====
class SophinfinityPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Cores corporativas
        self.azul_cyber = (28, 58, 112)
        self.cinza_escuro = (45, 45, 45)
        self.azul_claro = (72, 138, 199)
        self.vermelho_alerta = (220, 53, 69)
        
    def header(self):
        # Cabeçalho com logo e título
        self.set_fill_color(*self.azul_cyber)
        self.rect(0, 0, 210, 25, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 18)
        self.cell(0, 15, "RELATÓRIO DE RECONHECIMENTO RECONX", 0, 1, "C")
        self.set_font("helvetica", "I", 10)
        self.cell(0, 5, "SOPHINFINITY SEC-SOLUTIONS", 0, 1, "C")
        self.ln(10)
        
    def footer(self):
        # Rodapé com informações da empresa
        self.set_y(-20)
        self.set_fill_color(*self.cinza_escuro)
        self.rect(0, self.h - 20, 210, 20, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 5, f"© 2025 SOPHINFINITY SEC-SOLUTIONS. Todos os direitos reservados.", 0, 1, "C")
        self.cell(0, 5, f"CNPJ: 58.185.435/0001-3 | Página {self.page_no()}/{{nb}} | {datetime.date.today().strftime('%d/%m/%Y')}", 0, 0, "C")
        
    def chapter_title(self, title):
        # Títulos de seção com estilo cybersecurity
        self.set_fill_color(*self.azul_claro)
        self.set_text_color(*self.cinza_escuro)
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, title, 0, 1, "L", True)
        self.ln(4)
        
    def chapter_body(self, body):
        # Corpo do texto
        self.set_text_color(*self.cinza_escuro)
        self.set_font("helvetica", "", 10)
        self.multi_cell(0, 5, body)
        self.ln(5)
        
    def add_info_box(self, title, content, alert_level="info"):
        # Caixas de informação com níveis de alerta
        if alert_level == "critical":
            color = self.vermelho_alerta
        elif alert_level == "warning":
            color = (255, 193, 7)
        else:
            color = self.azul_claro
            
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 10)
        self.cell(0, 6, title, 0, 1, "L", True)
        self.set_text_color(*self.cinza_escuro)
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 5, content, 1)
        self.ln(5)

def gerar_pdf_sophinfinity(analise_ia, target_name, resultados, output_dir="."):
    pdf = SophinfinityPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Informações do alvo
    pdf.chapter_title(f"ALVO DE RECONHECIMENTO: {target_name}")
    pdf.chapter_body(f"Data da Análise: {datetime.date.today().strftime('%d/%m/%Y')}")
    
    # Análise da IA
    pdf.chapter_title("ANÁLISE DE INTELIGÊNCIA ARTIFICIAL (RECONX)")
    pdf.chapter_body(analise_ia)
    
    # Resultados por módulo
    for key, value in resultados.items():
        pdf.chapter_title(f"MÓDULO: {key.upper()}")
        
        # Determinar nível de alerta baseado em palavras-chave
        alert_level = "info"
        if any(word in value.lower() for word in ["crítico", "vulnerabilidade", "exploração"]):
            alert_level = "critical"
        elif any(word in value.lower() for word in ["atenção", "suspeito", "alerta"]):
            alert_level = "warning"
            
        pdf.add_info_box(f"Resultados de {key}", value, alert_level)
    
    # Adicionar página de recomendações
    pdf.add_page()
    pdf.chapter_title("RECOMENDAÇÕES DE SEGURANÇA")
    pdf.chapter_body("Com base na análise realizada, recomendamos as seguintes ações para mitigar riscos identificados:")
    
    # Adicionar marca d'água de confidencial
    pdf.set_font('helvetica', 'B', 60)
    pdf.set_text_color(232, 232, 232)
    pdf.rotate(45, 105, 150)
    pdf.text(105, 100, "RECONX_CONFIDENCIAL")
    pdf.rotate(0)
    
    nome_pdf = os.path.join(output_dir, f"SOPHINFINITY_ReconX_{target_name.replace('.', '_')}.pdf")
    pdf.output(nome_pdf)
    return nome_pdf

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_recon', methods=['POST'])
def run_recon():
    target = request.form['target']
    if not target:
        return "[ERRO] O domínio ou IP alvo não pode ser vazio.", 400

    resultados = {
        "NMAP": modulo_nmap(target),
        "WhatWeb": modulo_passivo(target),
        "AMASS": modulo_amass(target)
    }

    entrada_ia = "\n".join([f"{k}:\n{v}" for k, v in resultados.items()])
    resposta_ia = modulo_gemini(entrada_ia)

    pdf_path = gerar_pdf_sophinfinity(resposta_ia, target, resultados, output_dir="static")

    return render_template('results.html', target=target, nmap_result=resultados["NMAP"], whatweb_result=resultados["WhatWeb"], amass_result=resultados["AMASS"], gemini_analysis=resposta_ia, pdf_path=pdf_path.replace("static/", ""))

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


