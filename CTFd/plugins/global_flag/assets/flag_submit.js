function globalFlagSend() {
  const value = document.getElementById("global-flag-input").value;
  fetch(CTFd.config.urlRoot + "/plugins/global_flag/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ submission: value })
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.data && data.data.status === "correct") {
        alert("Solved " + data.data.challenge + "!");
        if (window.updateChallengeBoard) {
          window.updateChallengeBoard();
        } else {
          location.reload();
        }
      } else if (data.data && data.data.status === "already_solved") {
        alert("Already solved " + data.data.challenge + ".");
      } else if (data.data && data.data.status === "authentication_required") {
        window.location = CTFd.config.urlRoot + "/login?next=" + window.location.pathname;
      } else {
        alert("Incorrect flag");
      }
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const board = document.getElementById("challenges-board");
  if (!board) return;
  const container = board.parentElement;
  const form = document.createElement("div");
  form.className = "input-group mb-3";
  form.innerHTML = `<input id="global-flag-input" type="text" class="form-control" placeholder="Global Flag"/><div class="input-group-append"><button id="global-flag-submit" class="btn btn-outline-secondary" type="button">Submit</button></div>`;
  container.insertBefore(form, board);
  document.getElementById("global-flag-submit").addEventListener("click", globalFlagSend);
  document.getElementById("global-flag-input").addEventListener("keypress", e => {
    if (e.keyCode === 13) globalFlagSend();
  });
});
