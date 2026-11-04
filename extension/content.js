console.log("[LinguaCopilot] content script loaded");

// Returns the word under the given point and its text range, or null
function getWordAtPoint(x, y) {
  const caret = document.caretRangeFromPoint(x, y);
  if (!caret || caret.startContainer.nodeType !== Node.TEXT_NODE) return null;

  const textNode = caret.startContainer;
  const text = textNode.textContent;
  const isWordChar = (c) => /[\p{L}\p{N}'-]/u.test(c);
  let start = caret.startOffset;
  let end = caret.startOffset;

  while (start > 0 && isWordChar(text[start - 1])) start--;
  while (end < text.length && isWordChar(text[end])) end++;

  const word = text.slice(start, end);
  if (!word) return null;

  const range = document.createRange();
  range.setStart(textNode, start);
  range.setEnd(textNode, end);
  return { word: word, range: range };
}

// Returns the full subtitle text currently displayed
function getCaptionSentence(segment) {
  const captionWindow = segment.closest(".caption-window");
  if (!captionWindow) return segment.textContent.trim();
  return Array.from(captionWindow.querySelectorAll(".ytp-caption-segment"))
    .map((s) => s.textContent.trim())
    .join(" ");
}

function getPlayer() {
  return document.querySelector("#movie_player") || document.body;
}

// Displays a short message on top of the video player
function showToast(title, detail, isError = false) {
  const previous = document.querySelector(".lc-toast");
  if (previous) previous.remove();

  const toast = document.createElement("div");
  toast.className = isError ? "lc-toast lc-toast--error" : "lc-toast";

  const titleElement = document.createElement("div");
  titleElement.className = "lc-toast__title";
  titleElement.textContent = title;
  toast.appendChild(titleElement);

  if (detail) {
    const detailElement = document.createElement("div");
    detailElement.className = "lc-toast__detail";
    detailElement.textContent = detail;
    toast.appendChild(detailElement);
  }

  getPlayer().appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// Highlights the word under the mouse with a box drawn over the subtitle
function getHighlightBox() {
  let box = document.querySelector(".lc-word-highlight");
  const player = getPlayer();
  if (!box) {
    box = document.createElement("div");
    box.className = "lc-word-highlight";
  }
  if (box.parentElement !== player) player.appendChild(box);
  return box;
}

function hideHighlight() {
  const box = document.querySelector(".lc-word-highlight");
  if (box) box.style.display = "none";
}

document.addEventListener("mousemove", (event) => {
  const segment = event.target.closest(".ytp-caption-segment");
  if (!segment) {
    hideHighlight();
    return;
  }

  const result = getWordAtPoint(event.clientX, event.clientY);
  if (!result) {
    hideHighlight();
    return;
  }

  const wordRect = result.range.getBoundingClientRect();
  const playerRect = getPlayer().getBoundingClientRect();
  const box = getHighlightBox();
  box.style.display = "block";
  box.style.left = `${wordRect.left - playerRect.left - 2}px`;
  box.style.top = `${wordRect.top - playerRect.top}px`;
  box.style.width = `${wordRect.width + 4}px`;
  box.style.height = `${wordRect.height}px`;
});

// Sends the clicked word to the API
document.addEventListener(
  "click",
  (event) => {
    const segment = event.target.closest(".ytp-caption-segment");
    if (!segment) return;
    event.stopPropagation();
    event.preventDefault();

    const result = getWordAtPoint(event.clientX, event.clientY);
    if (!result) return;
    const word = result.word;

    const video = document.querySelector("video");
    const payload = {
      word: word,
      sentence: getCaptionSentence(segment),
      video_id: new URLSearchParams(location.search).get("v"),
      timestamp_sec: video ? Math.round(video.currentTime * 10) / 10 : null,
      captured_at: new Date().toISOString(),
    };

    console.log("[LinguaCopilot]", payload);

    chrome.runtime.sendMessage({ type: "SAVE_WORD", payload: payload }, (response) => {
      if (chrome.runtime.lastError || !response || !response.ok) {
        console.error("[LinguaCopilot] save failed", chrome.runtime.lastError || response);
        showToast(`« ${word} » non enregistré`, "Erreur d'envoi, voir la console", true);
        return;
      }

      // The translation will be returned by the Lambda once DeepL is added
      const translation = response.data && response.data.translation;
      showToast(`« ${word} » enregistré`, translation || null);
    });
  },
  true
);

// Pauses the video while the mouse is over the subtitles, then resumes it
let pausedByHover = false;

document.addEventListener("mouseover", (event) => {
  if (!event.target.closest(".caption-window")) return;
  const video = document.querySelector("video");
  if (video && !video.paused) {
    video.pause();
    pausedByHover = true;
  }
});

document.addEventListener("mouseout", (event) => {
  const captionWindow = event.target.closest(".caption-window");
  if (!captionWindow) return;
  // Ignore moves between words inside the same subtitle block
  if (event.relatedTarget && captionWindow.contains(event.relatedTarget)) return;
  hideHighlight();
  const video = document.querySelector("video");
  if (video && pausedByHover) {
    video.play();
  }
  pausedByHover = false;
});