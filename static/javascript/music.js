// var player;
// let videoId;
// const YOUTUBE_API_KEY = "AIzaSyD0faAZQxBQp-faN4STx3LrBvTKTTxBs8o";
// const GymSongs = "PLvVNZNdaO6cHX6dpEUuacIx8p-L8lZBW6";
// const LoveSongs = "PLvVNZNdaO6cHs24e6EVIRXN9nOysHVPF5";
// const DanceSongs = "PLvVNZNdaO6cEa2kPNoopEMXcrfoHqCJSi";
// const SadSongs = "PLvVNZNdaO6cFP17t5FtN5dz7J4nlCgoAe";
// const SpirtualSongs = "PLvVNZNdaO6cHQ5ELpCz1DhRXj4AxXrS-U";

// async function play_song_by_name(songName) {
//   try {
//     let videoId = await fetchId(songName);
//     console.log("videoid", videoId);
//     changeVideo(videoId);
//   } catch (err) {
//     console.error("Error fetching video ID:", err);
//   }
// }

// async function loadPlaylist() {
//   try {
//     let playlist = await getPlaylist();
//     player.setShuffle(true);
//     player.setLoop(true);
//     player.loadPlaylist(playlist);
//     console.log("Loaded Playlist");
//   } catch (err) {
//     console.error("Error", err);
//   }
// }
// async function fetchId(query) {
//   const url = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&type=video&part=snippet&q=${encodeURIComponent(
//     query
//   )}`;
//   const response = await fetch(url);
//   const data = await response.json();

//   if (!data.items || data.items.length === 0) {
//     throw new Error("No videos found for the query");
//   }

//   const id = data.items[0].id.videoId;
//   console.log("API response:", data);
//   return id;
// }

// async function getPlaylist() {
//   let playlistId = LoveSongs;
//   const url = `https://www.googleapis.com/youtube/v3/playlistItems?key=${YOUTUBE_API_KEY}&part=contentDetails&playlistId=${playlistId}&maxResults=100`;
//   const response = await fetch(url);
//   const data = await response.json();
//   if (!data.items || data.items.length === 0) {
//     throw new Error("Invalid Playlist");
//   }
//   const videoIds = data.items.map((item) => item.contentDetails.videoId);

//   return videoIds;
// }

// function changeVideo(videoId) {
//   player.loadVideoById(videoId);
//   player.playVideo();
// }

// function playVideo() {
//   player.playVideo();
// }
// function pauseVideo() {
//   player.pauseVideo();
// }
// function nextVideo() {
//   player.nextVideo();
// }
// function prevVideo() {
//   player.previousVideo();
// }

// const rightContainer = document.getElementById("dynamic-content-up3");

// rightContainer.innerHTML = `
//     <div id="player" style="display: none;"></div>
//     <div class="player-background">
//     <img id="yt-thumbnail" class="yt-bg" src="" style=" filter: grayscale(100%) blur(2px);"/>
//     <div class="color-overlay"></div>

//     <div class="overlay">
//         <h3 id="yt-title" class="yt-title">Loading...</h3>

//         <div class="progress-container">
//         <div id="progress-bar" class="progress-bar"></div>
//         </div>

//         <div class="player-controls">
//           <button id="prev-btn" class="player-btn"><i class="fa-solid fa-backward"></i></button>
//           <button id="play-btn" class="player-btn"><i class="fa-solid fa-play"></i></button>
//           <button id="next-btn" class="player-btn"><i class="fa-solid fa-forward"></i></button>
//         </div>
//         <div id="time-display"></div>
//     </div>

// `;

// function updateCustomUI(videoId, title) {
//   document.getElementById(
//     "yt-thumbnail"
//   ).src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
//   document.getElementById("yt-title").textContent = title;
// }

// setInterval(() => {
//   if (player && player.getCurrentTime && player.getDuration) {
//     const progress = (player.getCurrentTime() / player.getDuration()) * 100;
//     document.getElementById("progress-bar").style.width = `${progress}%`;
//   }
// }, 1000);

// document.getElementById("play-btn").addEventListener("click", () => {
//   const icon = document.querySelector("#play-btn i");
//   if (player.getPlayerState() === YT.PlayerState.PLAYING) {
//     player.pauseVideo();
//     icon.classList.replace("fa-pause", "fa-play");
//   } else {
//     player.playVideo();
//     icon.classList.replace("fa-play", "fa-pause");
//   }
// });

// document
//   .getElementById("next-btn")
//   .addEventListener("click", () => player.nextVideo());
// document
//   .getElementById("prev-btn")
//   .addEventListener("click", () => player.previousVideo());

// function onYouTubeIframeAPIReady() {
//   player = new YT.Player("player", {
//     height: "250",
//     width: "100%",
//     videoId: "",
//     playerVars: {
//       autoplay: 0,
//       controls: 0,
//       rel: 0,
//       fs: 0,
//       iv_load_policy: 3,
//       playsinline: 1,
//     },
//     events: {
//       onReady: onPlayerReady,
//       onStateChange: onPlayerStateChange,
//       onError: onPlayerError,
//     },
//   });
// }

// function onPlayerError(event) {
//   console.warn(
//     "Error encountered, skipping to next video. Error code:",
//     event.data
//   );
//   setTimeout(() => {
//     if (typeof player.nextVideo === "function") {
//       player.nextVideo();
//     }
//   }, 1000);
// }

// function onPlayerReady(event) {
//   // loadPlaylist();
//   // setTimeout(() => document.getElementById("play-btn").click(), 1000);
// }

// function onPlayerStateChange(event) {
//   if (event.data === YT.PlayerState.PLAYING) {
//     const videoData = player.getVideoData();
//     const videoId = player.getVideoUrl().split("v=")[1].split("&")[0];
//     updateCustomUI(videoId, videoData.title);

//     // Change play button icon to pause
//     document
//       .querySelector("#play-btn i")
//       .classList.replace("fa-play", "fa-pause");
//   }

//   if (event.data === YT.PlayerState.PAUSED) {
//     document
//       .querySelector("#play-btn i")
//       .classList.replace("fa-pause", "fa-play");
//   }
// }

// setInterval(() => {
//   if (player && player.getCurrentTime && player.getDuration) {
//     const current = player.getCurrentTime();
//     const duration = player.getDuration();
//     const progress = (current / duration) * 100;

//     document.getElementById("progress-bar").style.width = `${progress}%`;
//     document.getElementById("time-display").textContent = `${formatTime(
//       current
//     )} / ${formatTime(duration)}`;
//   }
// }, 1000);

// function formatTime(sec) {
//   const min = Math.floor(sec / 60);
//   const s = Math.floor(sec % 60);
//   return `${min}:${s < 10 ? "0" : ""}${s}`;
// }
