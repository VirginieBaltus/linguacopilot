console.log("[LinguaCopilot] content script loaded");

const HOVER_DELAY_MS = 400;
const translationCache = new Map();
let hoveredKey = null;
let hoverTimer = null;

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

// Returns an element drawn over the video player, creating it if needed
function getOverlay(className) {
  let element = document.querySelector(`.${className}`);
  const player = getPlayer();
  if (!element) {
    element = document.createElement("div");
    element.className = className;
  }
  if (element.parentElement !== player) player.appendChild(element);
  return element;
}

// Displays a short confirmation on top of the video player
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
  setTimeout(() => toast.remove(), 2500);
}

function hideHover() {
  for (const className of ["lc-word-highlight", "lc-tooltip"]) {
    const element = document.querySelector(`.${className}`);
    if (element) element.style.display = "none";
  }
  clearTimeout(hoverTimer);
  hoveredKey = null;
}

// Displays the translation bubble above the hovered word
function showTooltip(text, wordRect, playerRect) {
  const tooltip = getOverlay("lc-tooltip");
  tooltip.textContent = text;
  tooltip.style.display = "block";
  tooltip.style.left = `${wordRect.left - playerRect.left + wordRect.width / 2}px`;
  tooltip.style.top = `${wordRect.top - playerRect.top - 10}px`;
}

function requestTranslation(key, word, sentence, wordRect, playerRect) {
  if (translationCache.has(key)) {
    showTooltip(translationCache.get(key), wordRect, playerRect);
    return;
  }

  showTooltip("…", wordRect, playerRect);
  chrome.runtime.sendMessage({ type: "TRANSLATE_WORD", payload: { word: word, sentence: sentence } }, (response) => {
    const failed = chrome.runtime.lastError || !response || !response.ok;
    const translation = !failed && response.data && response.data.translation;
    if (translation) translationCache.set(key, translation);
    // The mouse may have moved to another word in the meantime
    if (hoveredKey === key) showTooltip(translation || "Traduction indisponible", wordRect, playerRect);
  });
}

// Highlights the word under the mouse and translates it after a short pause
document.addEventListener("mousemove", (event) => {
  const segment = event.target.closest(".ytp-caption-segment");
  const result = segment ? getWordAtPoint(event.clientX, event.clientY) : null;
  if (!result) {
    hideHover();
    return;
  }

  const wordRect = result.range.getBoundingClientRect();
  const playerRect = getPlayer().getBoundingClientRect();
  const highlight = getOverlay("lc-word-highlight");
  highlight.style.display = "block";
  highlight.style.left = `${wordRect.left - playerRect.left - 2}px`;
  highlight.style.top = `${wordRect.top - playerRect.top}px`;
  highlight.style.width = `${wordRect.width + 4}px`;
  highlight.style.height = `${wordRect.height}px`;

  const sentence = getCaptionSentence(segment);
  const key = `${result.word}|${sentence}`;
  if (key === hoveredKey) return;

  hoveredKey = key;
  clearTimeout(hoverTimer);
  const tooltip = document.querySelector(".lc-tooltip");
  if (tooltip) tooltip.style.display = "none";
  hoverTimer = setTimeout(
    () => requestTranslation(key, result.word, sentence, wordRect, playerRect),
    HOVER_DELAY_MS
  );
});

// Saves the clicked word for the flashcards
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
    const sentence = getCaptionSentence(segment);

    const video = document.querySelector("video");
    const payload = {
      word: word,
      sentence: sentence,
      video_id: new URLSearchParams(location.search).get("v"),
      timestamp_sec: video ? Math.round(video.currentTime * 10) / 10 : null,
      captured_at: new Date().toISOString(),
    };

    chrome.runtime.sendMessage({ type: "SAVE_WORD", payload: payload }, (response) => {
      if (chrome.runtime.lastError || !response || !response.ok) {
        console.error("[LinguaCopilot] save failed", chrome.runtime.lastError || response);
        showToast(`« ${word} » non enregistré`, "Erreur d'envoi, voir la console", true);
        return;
      }
      const translation = response.data && response.data.translation;
      if (translation) translationCache.set(`${word}|${sentence}`, translation);
      showToast(`« ${word} » enregistré`, null);
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
  hideHover();
  const video = document.querySelector("video");
  if (video && pausedByHover) {
    video.play();
  }
  pausedByHover = false;
});