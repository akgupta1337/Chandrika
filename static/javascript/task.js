// async function loadTasks() {
//   try {
//     const res = await fetch("/api/tasks", {
//       credentials: "include",
//     });
//     const tasks = await res.json();
//     const container = document.getElementById("dynamic-content-down1");
//     container.innerHTML = ""; // Clear any previous content

//     if (!Array.isArray(tasks) || tasks.length === 0) {
//       container.innerHTML = "<p>No tasks found.</p>";
//       return;
//     }

//     for (const task of tasks) {
//       const taskEl = document.createElement("div");
//       taskEl.className = "task-item";
//       taskEl.innerHTML = `
//     <h3>${task.title}</h3>
//     <p>${task.notes || "No notes"}</p>
//     <p><strong>Status:</strong> <span style="color: ${
//       task.status === "completed" ? "lightgreen" : "orange"
//     };">
//     ${task.status === "completed" ? "Done" : "Pending"}
//     </span></p>
//     ${
//       task.due
//         ? `<p><strong>Due:</strong> ${new Date(task.due).toLocaleDateString(
//             "en-GB",
//             {
//               day: "numeric",
//               month: "long",
//               year: "2-digit",
//             }
//           )}</p>`
//         : ""
//     }

//     ${
//       task.status !== "completed"
//         ? `<button class="mark-complete" data-id="${task.id}" data-list="${task.taskListId}">Mark as Done</button>`
//         : ""
//     }
//   `;
//       container.appendChild(taskEl);
//     }

//     document.querySelectorAll(".mark-complete").forEach((btn) => {
//       btn.addEventListener("click", async () => {
//         const taskId = btn.getAttribute("data-id");
//         const listId = btn.getAttribute("data-list");
//         // console.log("Clicked", taskId);

//         const res = await fetch("/api/tasks/complete", {
//           method: "POST",
//           credentials: "include",
//           headers: {
//             "Content-Type": "application/json",
//           },
//           body: JSON.stringify({ taskId, listId }),
//         });

//         if (res.ok) {
//           await loadTasks();
//         } else {
//           console.error("Failed to mark task as complete");
//         }
//       });
//     });
//   } catch (err) {
//     console.error("Failed to load tasks:", err);
//     document.getElementById("dynamic-content-down1").innerHTML =
//       "<p>No Tasks Yet.</p>";
//   }
// }

// setTimeout(loadTasks, 2000);
