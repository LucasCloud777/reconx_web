from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import datetime
import os

app = Flask(__name__)

# ==== MÓDULOS SIMULADOS PARA DEMO ====
def modulo_nmap_demo(target):
    return f"""Starting Nmap 7.80 ( https://nmap.org ) at {datetime.datetime.now()}
Nmap scan report for {target}
Host is up (0.020s latency).
Not shown: 998 closed ports
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.41
443/tcp  open  https   Apache httpd 2.4.41

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.23 seconds"""

def modulo_whatweb_demo(target):
    return f"""http://{target} [200 OK] Apache[2.4.41], Country[UNITED STATES][US], HTML5, HTTPServer[Apache/2.4.41], IP[142.250.191.14], Title[Google], UncommonHeaders[alt-svc], X-Frame-Options[SAMEORIGIN], X-XSS-Protection[0]"""

def modulo_amass_demo(target):
    return f"""www.{target}
mail.{target}
ftp.{target}
blog.{target}
shop.{target}"""

def modulo_gemini_demo(texto_entrada):
    return f"""ANÁLISE TÉCNICA DE SEGURANÇA - RELATÓRIO PROFISSIONAL

RESUMO EXECUTIVO:
O alvo analisado apresenta uma configuração padrão de servidor web com Apache 2.4.41 executando nas portas 80 e 443. A análise revela pontos importantes para consideração de segurança.

DESCOBERTAS PRINCIPAIS:

1. SERVIÇOS IDENTIFICADOS:
   - Servidor HTTP/HTTPS Apache 2.4.41
   - Portas 80 e 443 abertas e responsivas
   - Tempo de resposta baixo (20ms) indicando boa conectividade

2. SUBDOMÍNIOS DESCOBERTOS:
   - Múltiplos subdomínios identificados (www, mail, ftp, blog, shop)
   - Expansão da superfície de ataque potencial

3. TECNOLOGIAS WEB:
   - HTML5 implementado
   - Headers de segurança parcialmente configurados
   - X-Frame-Options presente (SAMEORIGIN)
   - X-XSS-Protection desabilitado (valor 0)

RECOMENDAÇÕES DE SEGURANÇA:

1. ALTA PRIORIDADE:
   - Habilitar X-XSS-Protection
   - Implementar Content Security Policy (CSP)
   - Verificar configurações de HTTPS

2. MÉDIA PRIORIDADE:
   - Auditoria de subdomínios ativos
   - Implementar HSTS headers
   - Verificar versão do Apache para vulnerabilidades conhecidas

3. MONITORAMENTO:
   - Implementar logging de segurança
   - Monitoramento contínuo de novos subdomínios

CONCLUSÃO:
O alvo apresenta uma configuração básica de segurança com algumas lacunas que devem ser endereçadas para melhorar a postura de segurança geral."""

# ==== RELATÓRIO PDF ====
class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Relatório de Reconhecimento - ReconX", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}} | Gerado por SOPHINFINITY | {datetime.date.today()} | ReconX", new_x="RIGHT", new_y="TOP", align="R")

    def chapter_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("helvetica", "", 10)
        self.multi_cell(0, 5, body)
        self.ln()

def gerar_pdf(analise_ia, target_name, resultados, output_dir="."):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.chapter_title(f"Alvo: {target_name}")
    pdf.chapter_body(f"Data da Análise: {datetime.date.today()}")

    pdf.chapter_title("Análise da IA (Gemini)")
    pdf.chapter_body(analise_ia)

    for key, value in resultados.items():
        pdf.chapter_title(f"Resultados do Módulo: {key}")
        pdf.chapter_body(value)

    nome_pdf = os.path.join(output_dir, f"relatorio_reconx_{target_name.replace('.', '_')}.pdf")
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
        "NMAP": modulo_nmap_demo(target),
        "WhatWeb": modulo_whatweb_demo(target),
        "AMASS": modulo_amass_demo(target)
    }

    entrada_ia = "\n".join([f"{k}:\n{v}" for k, v in resultados.items()])
    resposta_ia = modulo_gemini_demo(entrada_ia)

    pdf_path = gerar_pdf(resposta_ia, target, resultados, output_dir="static")

    return render_template('results.html', target=target, nmap_result=resultados["NMAP"], whatweb_result=resultados["WhatWeb"], amass_result=resultados["AMASS"], gemini_analysis=resposta_ia, pdf_path=pdf_path.replace("static/", ""))

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

