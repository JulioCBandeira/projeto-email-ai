from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from huggingface_hub import InferenceClient
import os
import PyPDF2
import unicodedata
import re

# Carregar variáveis de ambiente
load_dotenv()

# Configuração inicial do app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Cliente Hugging Face com provedor Nebius
client = InferenceClient(
    provider="nebius",
    api_key=os.getenv("HF_API_KEY")
)

MODEL_NAME = "google/gemma-2-2b-it"

def limpar_texto(texto):
    # Remover caracteres especiais e normalizar a acentuação
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = re.sub(r'\s+', ' ', texto)  # Remove múltiplos espaços
    return texto.strip()

def get_huggingface_response(message):
    # Limpeza do texto
    message = limpar_texto(message)

    prompt = f"""
    Classifique o seguinte e-mail como PRODUTIVO ou IMPRODUTIVO. Se for PRODUTIVO, gere uma resposta breve e formal. Se for IMPRODUTIVO, informe que não é necessária uma resposta.

    Exemplos:
    E-mail: "Gostaria de saber os horários disponíveis para marcar uma reunião."
    Categoria: PRODUTIVO
    Resposta: Agradecemos seu contato. Estamos disponíveis na próxima semana nos dias 24 e 25 às 10h.

    E-mail: "Feliz natal"
    Categoria: IMPRODUTIVO
    Resposta: Nenhuma necessária

    Agora, analise este e-mail:
    "{message}"

    Responda no seguinte formato:
    Categoria: <PRODUTIVO ou IMPRODUTIVO>
    Resposta: <resposta gerada ou "Nenhuma necessária">
    """

    try:
        # Chama o modelo da HuggingFace
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = completion.choices[0].message.content

        categoria = "Não identificada"
        resposta = ""

        # Extrair Categoria e Resposta do texto retornado
        for line in response_text.splitlines():
            if "Categoria:" in line:
                categoria = line.replace("Categoria:", "").strip()
            elif "Resposta:" in line:
                resposta = line.replace("Resposta:", "").strip()

        resultado_formatado = (
            f"<strong>Categoria:</strong> {categoria}<br>"
            f"<strong>Resposta:</strong> {resposta}"
        )
        return {"generated_text": resultado_formatado}

    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    result = get_huggingface_response(user_message)

    if "error" in result:
        return jsonify({"error": result["error"]})

    return jsonify({"reply": result["generated_text"]})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Arquivo vazio."})

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
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

    # Limpeza do texto extraído
    text_content = limpar_texto(text_content)

    result = get_huggingface_response(text_content)

    if "error" in result:
        return jsonify({"error": result["error"]})

    return jsonify({"reply": f"<strong>Arquivo enviado:</strong> {filename}<br>" + result["generated_text"]})

if __name__ == "__main__":
    app.run(debug=True)
