var images;
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
      case "doWebSearch":
        return await this.handleWikiSearch(parameters);

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
        console.log("weather updates");
        return await this.handleWeatherOperation(parameters);

      case "need_more_info":
        return await parameters.message;
      default:
        return "I'm not sure how to help with that request.";
    }
  }

  async handleWikiSearch(parameters) {
    images = await fetchImages(parameters.user_query);
    return fetchWikiContext(parameters.user_query);
  }

  async handleMusicOperation(functionType, parameters) {
    switch (functionType) {
      case "play_song":
        play_song_by_name(parameters.song_name);
        return "Playing " + parameters.song_name;
      case "pause_song":
        pauseVideo();
        return "Paused Music";
      case "resume_song":
        playVideo();
        return "Resumed";
      case "play_next_song":
        nextVideo();
        return "Playing next song";
      case "play_previous_song":
        prevVideo();
        return "Playing previous song";
      case "play_playlist":
        loadPlaylist(parameters.playlistname);
        return "Playing Now-" + parameters.playlistname;
      default:
        return "Music Function Error No matching function found!";
    }
  }
  async handleNewsOperation(parameters) {
    loadNews(parameters.q);
    return "Showing news on " + parameters.q;
  }

  async handleWeatherOperation(parameters) {
    let dayValue = 1;

    switch ((parameters.day || "").toLowerCase()) {
      case "tomorrow":
        dayValue = 2;
        break;
      case "day after tomorrow":
        dayValue = 3;
        break;
      case "today":
      default:
        dayValue = 1;
        break;
    }

    const weatherData = await getWeatherDetails(dayValue);
    return weatherData;
  }
  async handleReminderOperation(parameters) {
    const res = await fetch("/add_task", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parameters),
    });

    if (!res.ok) throw new Error("Failed to add task");
    loadTasks();
    const text = await res.text();
    return text; // "Reminder to <task_name> added"
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
      const type = routerResponse.name;
      const parameters = routerResponse.arguments;

      console.log(type, parameters);

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

  addMessage(text, sender) {
    console.log(text);
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

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
      console.log(images);
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
      images.length = 0;
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

var player;
const YOUTUBE_API_KEY = "AIzaSyD0faAZQxBQp-faN4STx3LrBvTKTTxBs8o";
function getPlaylistId(name) {
  const playlists = {
    gym: "PLvVNZNdaO6cHX6dpEUuacIx8p-L8lZBW6",
    love: "PLvVNZNdaO6cHs24e6EVIRXN9nOysHVPF5",
    dance: "PLvVNZNdaO6cEa2kPNoopEMXcrfoHqCJSi",
    sad: "PLvVNZNdaO6cFP17t5FtN5dz7J4nlCgoAe",
    spiritual: "PLvVNZNdaO6cHQ5ELpCz1DhRXj4AxXrS-U",
  };

  return playlists[name.toLowerCase()] || null;
}

async function play_song_by_name(songName) {
  console.log(songName);
  try {
    let videoId = await fetchId(songName);
    console.log("videoid", videoId);
    changeVideo(videoId);
  } catch (err) {
    console.error("Error fetching video ID:", err);
  }
}

async function loadPlaylist(playListName = love) {
  try {
    let playlist = await getPlaylist(playListName);
    player.setShuffle(true);
    player.setLoop(true);
    player.loadPlaylist(playlist);
    console.log("Loaded Playlist");
  } catch (err) {
    console.error("Error", err);
  }
}
async function fetchId(query) {
  const url = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&type=video&part=snippet&q=${encodeURIComponent(
    query
  )}`;
  const response = await fetch(url);
  const data = await response.json();

  if (!data.items || data.items.length === 0) {
    throw new Error("No videos found for the query");
  }

  const id = data.items[0].id.videoId;
  console.log("API response:", data);
  return id;
}

async function getPlaylist(name = love) {
  playlistId = getPlaylistId(name);
  const url = `https://www.googleapis.com/youtube/v3/playlistItems?key=${YOUTUBE_API_KEY}&part=contentDetails&playlistId=${playlistId}&maxResults=100`;
  const response = await fetch(url);
  const data = await response.json();
  if (!data.items || data.items.length === 0) {
    throw new Error("Invalid Playlist");
  }
  const videoIds = data.items.map((item) => item.contentDetails.videoId);

  return videoIds;
}

function changeVideo(videoId) {
  console.log(player);
  player.loadVideoById(videoId);
  player.playVideo();
}

function playVideo() {
  player.playVideo();
}
function pauseVideo() {
  player.pauseVideo();
}
function nextVideo() {
  player.nextVideo();
}
function prevVideo() {
  player.previousVideo();
}

const rightContainer = document.getElementById("dynamic-content-up3");

rightContainer.innerHTML = `
    <div id="player" style="display: none;"></div>
    <div class="player-background">
    <img id="yt-thumbnail" class="yt-bg" src="" style=" filter: grayscale(100%) blur(2px);"/>
    <div class="color-overlay"></div>
    
    <div class="overlay">
        <h3 id="yt-title" class="yt-title">Loading...</h3>

        <div class="progress-container">
        <div id="progress-bar" class="progress-bar"></div>
        </div>

        <div class="player-controls">
          <button id="prev-btn" class="player-btn"><i class="fa-solid fa-backward"></i></button>
          <button id="play-btn" class="player-btn"><i class="fa-solid fa-play"></i></button>
          <button id="next-btn" class="player-btn"><i class="fa-solid fa-forward"></i></button>
        </div>
        <div id="time-display"></div>
    </div>

`;

function updateCustomUI(videoId, title) {
  document.getElementById(
    "yt-thumbnail"
  ).src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
  document.getElementById("yt-title").textContent = title;
}

setInterval(() => {
  if (player && player.getCurrentTime && player.getDuration) {
    const progress = (player.getCurrentTime() / player.getDuration()) * 100;
    document.getElementById("progress-bar").style.width = `${progress}%`;
  }
}, 1000);

document.getElementById("play-btn").addEventListener("click", () => {
  const icon = document.querySelector("#play-btn i");
  if (player.getPlayerState() === YT.PlayerState.PLAYING) {
    player.pauseVideo();
    icon.classList.replace("fa-pause", "fa-play");
  } else {
    player.playVideo();
    icon.classList.replace("fa-play", "fa-pause");
  }
});

document
  .getElementById("next-btn")
  .addEventListener("click", () => player.nextVideo());
document
  .getElementById("prev-btn")
  .addEventListener("click", () => player.previousVideo());

function onYouTubeIframeAPIReady() {
  player = new YT.Player("player", {
    height: "250",
    width: "100%",
    videoId: "",
    playerVars: {
      autoplay: 0,
      controls: 0,
      rel: 0,
      fs: 0,
      iv_load_policy: 3,
      playsinline: 1,
    },
    events: {
      onReady: onPlayerReady,
      onStateChange: onPlayerStateChange,
      onError: onPlayerError,
    },
  });
}

function onPlayerError(event) {
  console.warn(
    "Error encountered, skipping to next video. Error code:",
    event.data
  );
  setTimeout(() => {
    if (typeof player.nextVideo === "function") {
      player.nextVideo();
    }
  }, 1000);
}

function onPlayerReady(event) {
  // loadPlaylist("love");
  // setTimeout(() => document.getElementById("play-btn").click(), 1000);
}

function onPlayerStateChange(event) {
  if (event.data === YT.PlayerState.PLAYING) {
    const videoData = player.getVideoData();
    const videoId = player.getVideoUrl().split("v=")[1].split("&")[0];
    updateCustomUI(videoId, videoData.title);

    // Change play button icon to pause
    document
      .querySelector("#play-btn i")
      .classList.replace("fa-play", "fa-pause");
  }

  if (event.data === YT.PlayerState.PAUSED) {
    document
      .querySelector("#play-btn i")
      .classList.replace("fa-pause", "fa-play");
  }
}

setInterval(() => {
  if (player && player.getCurrentTime && player.getDuration) {
    const current = player.getCurrentTime();
    const duration = player.getDuration();
    const progress = (current / duration) * 100;

    document.getElementById("progress-bar").style.width = `${progress}%`;
    document.getElementById("time-display").textContent = `${formatTime(
      current
    )} / ${formatTime(duration)}`;
  }
}, 1000);

function formatTime(sec) {
  const min = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${min}:${s < 10 ? "0" : ""}${s}`;
}

let allNews = [];

async function loadNews(query = "india") {
  try {
    const res = await fetch(`/api/news?query=${encodeURIComponent(query)}`, {
      credentials: "include",
    });
    const data = await res.json();
    allNews = data.articles;
    renderNews();
  } catch (err) {
    console.error("Failed to load news:", err);
  }
}

async function renderNews() {
  try {
    const container = document.getElementById("dynamic-content-down3");
    container.innerHTML = "";

    if (!Array.isArray(allNews) || allNews.length === 0) {
      container.innerHTML = "<p>No news found.</p>";
      return;
    }

    for (const article of allNews) {
      const newsTile = document.createElement("div");
      newsTile.className = "news-tile";

      newsTile.innerHTML = `
        <div class="news-content">
          <div class="news-text">
            <h4 class="news-title">${article.title}</h4>
            <p class="news-desc">${article.description || "No description"}</p>
            <a href="${
              article.url
            }" target="_blank" class="news-link">Read more</a>
          </div>
          ${
            article.urlToImage
              ? `<img src="${article.urlToImage}" class="news-img" alt="news image" />`
              : ""
          }
        </div>
      `;

      container.appendChild(newsTile);
    }
  } catch (err) {
    console.error("Failed to load news:", err);
    document.getElementById("dynamic-content-down3").innerHTML =
      "<p>Error loading news.</p>";
  }
}

setInterval(() => {
  if (allNews.length > 1) {
    const first = allNews.shift();
    allNews.push(first); // rotate
    renderNews();
  }
}, 2 * 60 * 1000); // 2 minutes

loadNews("india");

async function fetchWikiContext(query) {
  const response = await fetch(
    `/get_wiki_context?query=${encodeURIComponent(query)}`
  );
  if (!response.ok) throw new Error("Failed to fetch context");
  return await response.text();
}

async function fetchImages(query) {
  const response = await fetch(
    `/get_images?query=${encodeURIComponent(query)}`
  );
  if (!response.ok) throw new Error("Failed to fetch images");
  return await response.json();
}

async function getWeatherDetails(day = 1) {
  try {
    const res = await fetch(`/api/weather_summary?day=${day}`);
    if (!res.ok) throw new Error("Failed to fetch weather data");

    const data = await res.json();
    return data;
  } catch (err) {
    console.error("Error fetching weather:", err);
    return null;
  }
}

async function loadTasks() {
  try {
    const res = await fetch("/api/tasks", {
      credentials: "include",
    });
    const tasks = await res.json();
    const container = document.getElementById("dynamic-content-down1");
    container.innerHTML = ""; // Clear any previous content

    if (!Array.isArray(tasks) || tasks.length === 0) {
      container.innerHTML = "<p>No tasks found.</p>";
      return;
    }

    for (const task of tasks) {
      const taskEl = document.createElement("div");
      taskEl.className = "task-item";
      taskEl.innerHTML = `
    <h3>${task.title}</h3>
    <p>${task.notes || "No notes"}</p>
    <p><strong>Status:</strong> <span style="color: ${
      task.status === "completed" ? "lightgreen" : "orange"
    };">
    ${task.status === "completed" ? "Done" : "Pending"}
    </span></p>
    ${
      task.due
        ? `<p><strong>Due:</strong> ${new Date(task.due).toLocaleDateString(
            "en-GB",
            {
              day: "numeric",
              month: "long",
              year: "2-digit",
            }
          )}</p>`
        : ""
    }

    ${
      task.status !== "completed"
        ? `<button class="mark-complete" data-id="${task.id}" data-list="${task.taskListId}">Mark as Done</button>`
        : ""
    }
  `;
      container.appendChild(taskEl);
    }

    document.querySelectorAll(".mark-complete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const taskId = btn.getAttribute("data-id");
        const listId = btn.getAttribute("data-list");
        // console.log("Clicked", taskId);

        const res = await fetch("/api/tasks/complete", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ taskId, listId }),
        });

        if (res.ok) {
          await loadTasks();
        } else {
          console.error("Failed to mark task as complete");
        }
      });
    });
  } catch (err) {
    console.error("Failed to load tasks:", err);
    document.getElementById("dynamic-content-down1").innerHTML =
      "<p>No Tasks Yet.</p>";
  }
}

setTimeout(loadTasks, 2000);
