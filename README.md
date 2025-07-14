# 🕵️‍♂️ ReconX Web - Plataforma de Análise e Reconhecimento de Superfície de Ataque

ReconX é uma aplicação web que permite realizar varreduras técnicas em domínios e gerar relatórios PDF automatizados com insights fornecidos por uma IA integrada via Google Gemini API.

---

## ⚙️ Requisitos

### 1. Sistema Operacional:
- Desenvolvido e testado no **Kali Linux** (Debian-based)

### 2. Ferramentas Externas (devem estar instaladas e no PATH):

| Ferramenta | Finalidade |
|-----------|------------|
| `nmap`     | Scan de portas e serviços |
| `whatweb`  | Identificação de tecnologias web |
| `amass`    | Enumeração de subdomínios |

> **Dica:** No Kali, essas ferramentas já vêm pré-instaladas. Se estiver usando outra distro, instale com `sudo apt install nmap whatweb amass`.

### 3. API Key do Google Gemini
- É necessário gerar e configurar uma chave de API do **Google Gemini (Generative AI)** para que a IA possa analisar os dados coletados.
- Acesse em : https://aistudio.google.com/

---

## 🚀 Instalação e Execução

```bash
git clone https://github.com/LucasCloud777/reconx_web.git
cd reconx_web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Adicione sua chave da API Gemini no arquivo .env
echo "GEMINI_API_KEY=SUA_CHAVE_AQUI" > .env

# Execute o app
python app.py
```
- - - - - - - - - - - - - - - - - - - - - - - -

🌐 Acesso
Após iniciar a aplicação, acesse via navegador:
http://localhost:5000


📝 Funcionalidades
Seleção e análise de domínios

- Scan com Nmap, WhatWeb e Amass

- Geração de relatório PDF com análise automatizada da IA (Google Gemini)

- Interface leve e funcional em Flask

⚠️ Importante
Esta aplicação não funcionará corretamente em plataformas como Render, Vercel ou Replit, pois elas não oferecem acesso root ou instalação de binários como Nmap, Amass ou WhatWeb.

📦 Licença
Este projeto é de uso livre para fins educacionais e profissionais de segurança ofensiva/defensiva. Desenvolvido por Lucas M. Teixeira.
-  https://www.linkedin.com/in/lucas-m-teixeira-225833282/

