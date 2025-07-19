let allNews = [];

async function loadTodayNews() {
  try {
    const res = await fetch("/api/news", {
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

loadTodayNews();
