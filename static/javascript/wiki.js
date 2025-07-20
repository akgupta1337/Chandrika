async function fetchWikiContext(query) {
  const response = await fetch(
    `/get_wiki_context?query=${encodeURIComponent(query)}`
  );
  if (!response.ok) throw new Error("Failed to fetch context");
  return await response.json();
}

async function fetchImages(query) {
  const response = await fetch(
    `/get_images?query=${encodeURIComponent(query)}`
  );
  if (!response.ok) throw new Error("Failed to fetch images");
  return await response.json();
}

function updateImageCarousel(images) {
  const imageContainer = document.getElementById("dynamic-content-up2");
  imageContainer.innerHTML = "";

  const img = document.createElement("img");
  img.className = "context-image";
  imageContainer.appendChild(img);

  let index = 0;
  function showNextImage() {
    img.src = images[index];
    index = (index + 1) % images.length;
  }

  showNextImage();
  if (images.length > 1) {
    setInterval(showNextImage, 5000); // Change every 5 seconds
  }
}

function updateWikiContent(query, paragraphs) {
  const contentContainer = document.getElementById("dynamic-content-down2");
  contentContainer.innerHTML = ""; // Clear

  const title = document.createElement("h2");
  title.textContent = `Question: ${query}`;
  title.className = "user-query";
  contentContainer.appendChild(title);

  const summaryDiv = document.createElement("div");
  summaryDiv.className = "wiki-summary";

  if (Array.isArray(paragraphs)) {
    for (const para of paragraphs) {
      const p = document.createElement("p");
      p.textContent = para;
      summaryDiv.appendChild(p);
    }
  } else {
    const p = document.createElement("p");
    p.textContent = paragraphs;
    summaryDiv.appendChild(p);
  }

  contentContainer.appendChild(summaryDiv);
}

async function handleQuery(query) {
  try {
    const [images, context] = await Promise.all([
      fetchImages(query),
      fetchWikiContext(query),
    ]);

    if (images.length > 0) updateImageCarousel(images);
    updateWikiContent(query, context);
  } catch (err) {
    console.error("[ERROR]", err);
  }
}

// handleQuery("who is elon musk");
