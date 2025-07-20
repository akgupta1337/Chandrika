const now = new Date();

// Format: "13 July 25"
const formattedDate = now.toLocaleDateString("en-GB", {
  day: "numeric",
  month: "long",
  year: "2-digit",
});

// Format: "Saturday"
const dayName = now.toLocaleDateString("en-GB", {
  weekday: "long",
});

async function loadWeatherLeft() {
  try {
    const res = await fetch("/api/weather");
    const data = await res.json();
    const place = data.city + ", " + data.region;
    const container = document.getElementById("dynamic-content-up1");

    let iconClass = "fa-solid fa-sun"; // default icon

    if (data.precipitation > 0.6) {
      iconClass = "fa-solid fa-cloud-showers-heavy"; // heavy rain
    } else if (data.precipitation > 0.2) {
      iconClass = "fa-solid fa-cloud-meatball"; // cloudy or light rain
    } else if (data.temperature < 12) {
      iconClass = "fa-solid fa-snowflake"; // optional: use snowflake if very cold
    } else {
      iconClass = "fa-solid fa-sun"; // sunny
    }

    container.innerHTML = `
  <div class="weather-widget">
    <div class="weather-left">
      <div class="temp-row">
        <p class="temp">${data.temperature}°</p>
        <i class="${iconClass} weather-icon-inline"></i>
      </div>
      <p class="city-name">${place}</p>
      <p class="date-text">${formattedDate}</p>
      <p class="day-text">${dayName}</p>
    </div>
    <div class="system-right" id="system-info"></div>
  </div>

  
`;
  } catch (err) {
    console.error("Weather fetch failed:", err);
  }
}
async function loadSystemInfo() {
  try {
    const res = await fetch("/api/system-info");
    const data = await res.json();

    const systemContainer = document.getElementById("system-info");
    systemContainer.innerHTML = `
  <p><i class="fas fa-desktop"></i> <strong>OS:</strong> ${data.os} ${data.os_version}</p>
  <p><i class="fas fa-microchip"></i> <strong>CPU:</strong> ${data.cpu_usage}%</p>
  <p><i class="fas fa-memory"></i> <strong>Memory:</strong> ${data.memory}%</p>
  <p><i class="fas fa-cogs"></i> <strong>Cores:</strong> ${data.cpu_cores}</p>
`;
  } catch (err) {
    console.error("Failed to load system info:", err);
  }
}

// loadSystemInfo();
loadWeatherLeft();
