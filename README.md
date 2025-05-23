# projeto-email-ai
📬 Assistente de E-mails Inteligente
Este projeto é um assistente virtual inteligente para triagem e resposta automática de e-mails corporativos. Ele classifica as mensagens como PRODUTIVAS ou IMPRODUTIVAS e gera respostas formais com base no conteúdo.

✅ Deploy online:
https://assistente-de-e-mails-inteligente.onrender.com/

----------------------------------------------

⚙️ Tecnologias Utilizadas
Python 3.11

- Flask
- Hugging Face (Gemma 2B via Nebius)
- Flask-Session
- HTML/CSS
- Render (Deploy)
- UptimeRobot (Monitoramento)

----------------------------------------------

🧠 Funcionalidades

- Classificação de e-mails em “PRODUTIVO” ou “IMPRODUTIVO”
- Geração de respostas formais e contextuais
- Upload de arquivos (.pdf ou .txt) para análise de conteúdo
- Histórico de conversa com contexto de sessão
- Deploy gratuito e monitorado via Render

----------------------------------------------

🧪 Demonstração
Exemplos de uso:

Usuário: Olá, gostaria de agendar uma reunião  
→ Categoria: PRODUTIVO  
→ Resposta: Estamos disponíveis para agendar uma reunião. Qual a melhor data e horário para você?

Usuário: Feliz aniversário  
→ Categoria: IMPRODUTIVO  
→ Resposta: Obrigado! Estou à disposição para assuntos relacionados ao trabalho.

----------------------------------------------

🖥️ Instruções de Execução Local
1. Clone o repositório

git clone https://github.com/JulioCBandeira/projeto-email-ai.git
cd projeto-email-ai

2. Crie o ambiente virtual e ative-o

python -m venv .venv
source .venv/bin/activate      # Linux/Mac
.venv\Scripts\activate         # Windows

3. Instale as dependências

pip install -r requirements.txt

----------------------------------------------

📦 Exemplo de requirements.txt:

Flask
python-dotenv
huggingface_hub
flask_session
PyPDF2

4. Configure o arquivo .env
Crie um arquivo chamado .env na raiz com a variável da sua chave API da Hugging Face com provedor Nebius:

HF_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

5. Execute a aplicação

python app.py
Acesse em http://localhost:5000/

----------------------------------------------

☁️ Deploy no Render

- Repositório sincronizado com Render
- Build automático com gunicorn
- Monitorado 24/7 pelo UptimeRobot

----------------------------------------------

🧠 Roadmap Futuro

-Exportação de histórico em PDF
- Integração com e-mails reais (via IMAP/SMTP)
- Interface mais moderna (Bootstrap 5)

----------------------------------------------

🤝 Contribuições

Sinta-se à vontade para abrir issues, forks ou pull requests.