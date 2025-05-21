from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

# Defina o URL do seu modelo personalizado do Hugging Face
model_url = "https://hf.co/chat/assistant/682e26ca42a1285bdd7533aa"

# Função para enviar mensagem para o modelo Hugging Face
def get_huggingface_response(message):
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",  # Substitua com seu token do Hugging Face
        "Content-Type": "application/json",
    }
    
    payload = {
        "inputs": message
    }
    
    response = requests.post(model_url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()  # Retorna a resposta do modelo
    else:
        return {"error": f"Erro: {response.status_code}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    try:
        # Enviar a mensagem do usuário ao Hugging Face para obter a resposta
        huggingface_response = get_huggingface_response(user_message)
        
        # Aqui tratamos a resposta e retornamos para o front-end
        if "error" in huggingface_response:
            return jsonify({"error": huggingface_response["error"]})

        # Retorna a resposta do assistente do Hugging Face
        ai_reply = huggingface_response.get("generated_text", "Nenhuma resposta gerada.")
        return jsonify({"reply": ai_reply})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
