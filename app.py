from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from huggingface_hub import InferenceClient
import os
import PyPDF2
import unicodedata
import re
from flask_session import Session

# Carrego as variáveis de ambiente (ex: HF_API_KEY)
load_dotenv()

# Inicializo o app Flask e configuro a pasta de uploads
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuro a sessão para manter o histórico de conversa entre requisições
app.secret_key = "chave_secreta_segura"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Instancio o cliente da Hugging Face com o modelo da Nebius
client = InferenceClient(
    model="google/gemma-2-2b-it",
    provider="nebius",
    api_key=os.getenv("HF_API_KEY")
)

# Função para limpar e normalizar o texto
def limpar_texto(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

# Função que monta o prompt e envia para o modelo, e extrai a resposta
def get_huggingface_response(contexto):
    prompt = f"""
Classifique a conversa abaixo como PRODUTIVA ou IMPRODUTIVA. Se for PRODUTIVA, gere uma resposta breve e formal com continuidade. Se for IMPRODUTIVA, responda de forma respeitosa e corporativa, dizendo que não é necessária resposta, mas que está à disposição.

Exemplo:
Usuário: Olá, gostaria de agendar uma reunião
IA: Estamos disponíveis para agendar uma reunião. Qual a melhor data e horário para você?
Usuário: Segunda-feira às 17h
Categoria: PRODUTIVO
Resposta: Reunião agendada para segunda-feira às 17h. Enviarei o convite em breve.

Usuário: Feliz aniversário
Categoria: IMPRODUTIVO
Resposta: Obrigado! Estou à disposição para assuntos relacionados ao trabalho.

Agora, analise esta conversa:
{contexto}

Responda no seguinte formato:
Categoria: <PRODUTIVO ou IMPRODUTIVO>
Resposta: <resposta gerada>
"""

    try:
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content.strip()

        categoria = "Não identificada"
        resposta = ""

        # Faço o parsing da resposta para extrair Categoria e Resposta
        for line in response_text.splitlines():
            if "Categoria:" in line:
                categoria = line.replace("Categoria:", "").strip()
            elif "Resposta:" in line:
                resposta = line.replace("Resposta:", "").strip()

        resultado_formatado = (
            f"<strong>Categoria:</strong> {categoria}<br>"
            f"<strong>Resposta:</strong> {resposta}"
        )
        return {"generated_text": resultado_formatado, "resposta_pura": resposta}

    except Exception as e:
        return {"error": str(e)}

# Página principal
@app.route("/")
def index():
    return render_template("index.html")

# Rota que recebe as mensagens do chat e responde com base no histórico
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    # Inicializo o histórico se ainda não existir
    if "history" not in session:
        session["history"] = []

    # Se a última resposta já foi uma conclusão, limpo o histórico
    if session["history"]:
        ultima_resposta = session["history"][-1].lower()
        palavras_chave_finais = [
            "reunião agendada",
            "enviarei o convite",
            "convite enviado",
            "não é necessária resposta",
            "estou à disposição"
        ]
        if any(palavra in ultima_resposta for palavra in palavras_chave_finais):
            session["history"] = []

    # Adiciono a nova mensagem ao histórico
    session["history"].append(f"Usuário: {user_message}")
    contexto = "\n".join(session["history"])

    # Envio o contexto para o modelo e recebo a resposta
    result = get_huggingface_response(contexto)

    if "error" in result:
        return jsonify({"error": result["error"]})

    # Atualizo o histórico com a resposta da IA
    resposta_texto = result["resposta_pura"]
    session["history"].append(f"IA: {resposta_texto}")

    return jsonify({"reply": result["generated_text"]})

# Rota que permite envio de arquivos (PDF ou TXT) para análise
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio."})

    # Salvo o arquivo na pasta de uploads
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Leio o conteúdo do arquivo de acordo com o tipo
        if filename.lower().endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text_content = "".join(page.extract_text() or "" for page in reader.pages)
        elif filename.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text_content = f.read()
        else:
            return jsonify({"error": "Formato não suportado. Use .pdf ou .txt."})
    except Exception as e:
        return jsonify({"error": f"Erro ao ler o arquivo: {str(e)}"})

    # Limpo o texto antes de enviar ao modelo
    text_content = limpar_texto(text_content)
    result = get_huggingface_response(text_content)

    if "error" in result:
        return jsonify({"error": result["error"]})

    return jsonify({"reply": f"<strong>Arquivo enviado:</strong> {filename}<br>" + result["generated_text"]})

# Executo o app no modo debug
if __name__ == "__main__":
    app.run(debug=True)
