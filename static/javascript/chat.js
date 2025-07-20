class ChatInterface {
  constructor() {
    this.dynamicContentUp2 = document.getElementById("dynamic-content-up2");
    this.chatMessages = document.getElementById("chatMessages");
    this.chatInput = document.getElementById("chatInput");
    this.chatInputField = document.getElementById("chatInputField");
    this.sendBtn = document.getElementById("sendBtn");
    this.closeChat = document.getElementById("closeChat");
    this.typingIndicator = document.getElementById("typingIndicator");
    this.greeting = document.querySelector(".greeting");
    this.chatInputBox = document.querySelector(".chat-input-box");
    this.chatHeader = document.querySelector(".chat-header");
    this.chatInputContainer = document.querySelector(".chat-input-container");

    this.initializeEventListeners();
  }

  async fetchRouterQuery(query) {
    try {
      const response = await fetch(
        `/get_query_type?query=${encodeURIComponent(query)}`
      );
      if (!response.ok) throw new Error("Failed to fetch router response");

      const result = await response.json();
      // You will handle the result's type and function logic separately
      return result;
    } catch (error) {
      console.error("Error fetching router query:", error);
      return {
        type: "error",
        message: "I'm sorry, I couldn't process your request at the moment.",
      };
    }
  }

  async handleFunctionCall(functionType, parameters) {
    switch (functionType) {
      case "search_wikipedia":
        return await this.handleWikiSearch(parameters); // expects: { query }

      case "play_song":
      case "pause_song":
      case "resume_song":
      case "play_next_song":
      case "play_previous_song":
      case "play_playlist":
        return await this.handleMusicOperation(functionType, parameters);

      case "get_news_updates":
        return await this.handleNewsOperation(parameters);

      case "set_todo_and_reminder":
        return await this.handleReminderOperation(parameters);

      case "get_weather_updates":
        return await this.handleWeatherOperation(parameters);

      case "need_more_info":
        return await this.needMoreInfo(parameters);
      case "error":
        return (
          parameters.message || "Sorry, I couldn't understand your request."
        );
      default:
        return "I'm not sure how to help with that request.";
    }
  }

  async handleWikiSearch(parameters) {
    return "Wiki search functionality to be implemented";
  }

  async handleMusicOperation(parameters) {
    return "Music operation functionality to be implemented";
  }

  async handleNewsOperation(parameters) {
    return "News operation functionality to be implemented";
  }

  async handleReminderOperation(parameters) {
    return "Reminder operation functionality to be implemented";
  }

  async handleWeatherOperation(parameters) {
    return "Weather operation functionality to be implemented";
  }

  async needMoreInfo(parameters) {
    return parameters.follow_up;
  }

  initializeEventListeners() {
    // Original chat input (from greeting area)
    this.chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.enterChatMode(this.chatInput.value.trim());
      }
    });

    // Chat interface input
    this.chatInputField.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    this.sendBtn.addEventListener("click", () => {
      this.sendMessage();
    });

    this.closeChat.addEventListener("click", () => {
      this.exitChatMode();
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
      if (
        e.key === "Escape" &&
        this.dynamicContentUp2.classList.contains("chat-mode")
      ) {
        this.exitChatMode();
      }
    });
  }

  async enterChatMode(initialMessage) {
    if (!initialMessage) return;

    // Transform the center content to chat mode
    this.dynamicContentUp2.classList.add("chat-mode");

    // Show chat elements
    this.chatHeader.style.display = "flex";
    this.chatMessages.style.display = "flex";
    this.chatInputContainer.style.display = "block";

    // Clear previous messages
    this.chatMessages.innerHTML = "";

    // Add the initial message
    this.addMessage(initialMessage, "user");

    // Clear the original input
    this.chatInput.value = "";

    // Focus on chat input
    setTimeout(() => {
      this.chatInputField.focus();
    }, 100);

    // Get real response for initial message
    await this.getBotResponse(initialMessage);
  }

  exitChatMode() {
    // Remove chat mode
    this.dynamicContentUp2.classList.remove("chat-mode");

    // Hide chat elements
    this.chatHeader.style.display = "none";
    this.chatMessages.style.display = "none";
    this.chatInputContainer.style.display = "none";

    // Clear input
    this.chatInputField.value = "";
  }

  async sendMessage() {
    const message = this.chatInputField.value.trim();
    if (!message) return;

    // Disable input while processing
    this.chatInputField.disabled = true;
    this.sendBtn.disabled = true;

    this.addMessage(message, "user");
    this.chatInputField.value = "";

    // Get real response
    await this.getBotResponse(message);

    // Re-enable input
    this.chatInputField.disabled = false;
    this.sendBtn.disabled = false;
    this.chatInputField.focus();
  }

  async getBotResponse(query) {
    // Show typing indicator
    this.showTypingIndicator();

    try {
      const routerResponse = await this.fetchRouterQuery(query);

      this.hideTypingIndicator();

      // Destructure the response to get type and parameters
      const { type, parameters } = routerResponse;

      // Call the handler with correct structure
      const responseText = await this.handleFunctionCall(type, parameters);

      // Limit response length for better UX
      let finalResponse = responseText;
      if (typeof responseText === "string" && responseText.length > 1200) {
        finalResponse = responseText.substring(0, 1200) + "...";
      }

      // Add the response
      this.addMessage(
        finalResponse || "I couldn't process your request properly.",
        "bot"
      );
    } catch (error) {
      this.hideTypingIndicator();
      console.error("Error getting bot response:", error);

      this.addMessage(
        "I apologize, but I'm having trouble processing your request right now. Please try again later.",
        "bot"
      );
    }
  }

  addMessage(text, sender, images = null) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    // Handle multi-line content better
    if (text.includes("\n")) {
      // Convert newlines to proper line breaks
      const lines = text.split("\n");
      lines.forEach((line, index) => {
        if (index > 0) {
          contentDiv.appendChild(document.createElement("br"));
        }
        contentDiv.appendChild(document.createTextNode(line));
      });
    } else {
      contentDiv.textContent = text;
    }

    messageDiv.appendChild(contentDiv);

    // Add images if provided
    if (images && images.length > 0) {
      const imagesDiv = document.createElement("div");
      imagesDiv.className = "message-images";

      images.forEach((imageSrc, index) => {
        const imageContainer = document.createElement("div");
        imageContainer.className = "message-image";

        const img = document.createElement("img");
        img.src = imageSrc;
        img.alt = `Response image ${index + 1}`;
        img.loading = "lazy"; // Better performance

        // Handle image load errors
        img.onerror = () => {
          imageContainer.style.display = "none";
        };

        imageContainer.appendChild(img);
        imagesDiv.appendChild(imageContainer);
      });

      messageDiv.appendChild(imagesDiv);
    }

    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }

  showTypingIndicator() {
    this.typingIndicator.style.display = "block";
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    this.typingIndicator.style.display = "none";
  }

  scrollToBottom() {
    setTimeout(() => {
      this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }, 100);
  }
}

// Initialize chat interface when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Wait for your existing renderContent() to complete before initializing chat
  setTimeout(() => {
    new ChatInterface();
  }, 500); // Small delay to ensure greeting is rendered
});
