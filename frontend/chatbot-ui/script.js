const messages = [];
const inputElement = document.querySelector(".message-input");

inputElement.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

function renderChatArea(shouldRenderLoading) {
  let final_html = "";
  messages.forEach((msg) => {
    let html = "";
    if (msg.type === "user") {
      html = `
        <div class="message user-message">
          <div class="message-avatar user-avatar">J</div>
          <div class="message-content user-content">
            ${msg.content}
          </div>
        </div>
    `;
    } else {
      let imageHTML = "";
      msg.images.forEach((img) => {
        imageHTML += `<img src="${img}" class="msg-img" alt="Attached Image">`;
      });
      html = `
        <div class="message">
          <div class="message-avatar claude-avatar">C</div>
          <div class="message-content">
            ${msg.content}
            <br/>
            ${
              imageHTML === ""
                ? ""
                : '<h2 class="image-header">Relevant Images</h2>'
            }
            ${imageHTML}
          </div>
        </div>
    `;
    }
    final_html += html;
  });

  const chatContainer = document.querySelector(".messages-container");
  chatContainer.innerHTML = final_html;
  if (shouldRenderLoading) renderLoadingAnimation(chatContainer);
  else {
    let container = document.querySelector(".chat-area");
    container.scrollTop = container.scrollHeight;
  }
}

// renderChatArea();
const sendButton = document.querySelector(".send-button");
sendButton.addEventListener("click", () => {
  sendMessage();
});

function renderLoadingAnimation(container) {
  const loadingAnimation = `
        <div class="message loading-message">
        <div class="message-avatar claude-avatar">C</div>
        <div class="message-content">
        <div class="loading-bubble">
          <div class="loading-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
        </div>
      </div>
  `;
  container.innerHTML += loadingAnimation;
  let chatContainer = document.querySelector(".chat-area");
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
  const inputMsg = inputElement.value;
  if (inputMsg === "") return;
  messages.push({
    type: "user",
    content: inputMsg,
  });
  inputElement.value = "";
  renderChatArea(true);
  getChatbotResponse(inputMsg);
}

async function getChatbotResponse(query) {
  const data = {
    input: {
      user_query: {
        content: query,
        additional_kwargs: {},
        response_metadata: {},
        type: "human",
        name: "string",
        id: "string",
        example: false,
        additionalProp1: {},
      },
    },
    config: {},
    kwargs: {},
  };
  let responseData;
  let imageData;
  try {
    const response = await fetch("http://localhost:8000/agent/invoke", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    const imageResponse = await fetch(
      `http://localhost:8000/query_image?query=${query}`,
      {
        method: "GET",
        headers: { "Content-Type": "text/plain" },
      }
    );
    responseData = await response.json();
    imageData = await imageResponse.json();
    document.querySelector(".loading-message").remove();
  } catch (error) {
    console.log(error);
  }
  messages.push({
    type: "ai",
    content: responseData.output.answer.content,
    images: imageData.images,
  });
  renderChatArea(false);
}

renderChatArea(false);
