const centralOrb = document.getElementById("centralOrb");
const voiceWave = document.getElementById("voiceWave");

let isListening = false;

centralOrb.addEventListener("click", () => {
  if (!isListening) {
    startListening();
  } else {
    stopListening();
  }
});

function startListening() {
  isListening = true;
  statusText.textContent = "Listening...";
  centralOrb.classList.add("listening");
  voiceWave.classList.add("active");
}

function stopListening() {
  isListening = false;
  statusText.textContent = "Tap to Speak";
  centralOrb.classList.remove("listening");
  voiceWave.classList.remove("active");
}

function createParticle() {
  const particle = document.createElement("div");
  particle.className = "particle";
  particle.style.left = Math.random() * 100 + "%";
  particle.style.animationDelay = Math.random() * 2 + "s";
  particle.style.animationDuration = Math.random() * 10 + 5 + "s";
  document.getElementById("particles").appendChild(particle);

  setTimeout(() => {
    particle.remove();
  }, 15000);
}

// Create particles periodically
setInterval(createParticle, 500);
