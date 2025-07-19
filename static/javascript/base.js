async function fetchQuote() {
  try {
    const response = await fetch(
      "https://api.quotable.io/quotes/random?maxLength=50"
    );
    const data = await response.json();
    const quote = data[0].content;
    document.getElementById("tagline").textContent = `"${quote}"`;
  } catch (error) {
    console.error("Error fetching quote:", error);
  }
}

// fetchQuote();

window.addEventListener("message", (event) => {
  if (event.data === "authenticated") {
    window.location.reload();
  }
});

window.addEventListener("load", () => {
  clock();
  function clock() {
    const today = new Date();

    // get time components
    const hours = today.getHours();
    const minutes = today.getMinutes();
    const seconds = today.getSeconds();

    //add '0' to hour, minute & second when they are less 10
    const hour = hours < 10 ? "0" + hours : hours;
    const minute = minutes < 10 ? "0" + minutes : minutes;
    const second = seconds < 10 ? "0" + seconds : seconds;

    //make clock a 12-hour time clock
    const hourTime = hour > 12 ? hour - 12 : hour;

    if (hour === 0) {
      hour = 12;
    }
    //assigning 'am' or 'pm' to indicate time of the day
    const ampm = hour < 12 ? "AM" : "PM";

    // get date components
    const month = today.getMonth();
    const year = today.getFullYear();
    const day = today.getDate();

    //declaring a list of all months in  a year
    const monthList = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    //get current date and time
    const date = monthList[month] + " " + day + ", " + year;
    const time = hourTime + ":" + minute + " " + ampm;

    //combine current date and time
    const dateTime = time;

    //print current date and time to the DOM
    document.getElementById("date-time").innerHTML = dateTime;
    setTimeout(clock, 1000);
  }
});

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return { text: "Good Morning", icon: "fas fa-sun" };
  if (hour < 18) return { text: "Good Afternoon", icon: "fas fa-cloud-sun" };
  return { text: "Good Evening", icon: "fas fa-moon" };
}

function renderContent() {
  const { text, icon } = getGreeting();
  const container = document.getElementById("dynamic-content-up2");

  container.innerHTML = `
    <h1 class="title">C.H.A.N.D.R.I.K.A</h1>
    <p class="tagline" id="tagline">Your Personal Assistant</p>
    <h2 class="greeting"><i class="${icon}"></i> ${text}</h2>
    <div class="clock"><h1 id="date-time"></h1></div>
  `;
}

// Call after DOM loads
document.addEventListener("DOMContentLoaded", renderContent);
