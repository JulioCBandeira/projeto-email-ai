document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".chat-input-area");
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMessage = input.value.trim();
    if (!userMessage) return;

    // Adiciona mensagem do usuário na interface
    addMessage(userMessage, "user-message");

    input.value = ""; // limpa o campo

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();

      if (data.error) {
        addMessage(`Erro: ${data.error}`, "ai-message");
      } else {
        addMessage(data.reply, "ai-message", true);
      }
    } catch (error) {
      addMessage("Erro ao se comunicar com o servidor.", "ai-message");
    }
  });

  function addMessage(text, className, isHtml = false) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", className);

    const textDiv = document.createElement("div");
    textDiv.classList.add("message-text");

    if (isHtml) {
      textDiv.innerHTML = text;
    } else {
      textDiv.textContent = text;
    }

    messageDiv.appendChild(textDiv);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
});
