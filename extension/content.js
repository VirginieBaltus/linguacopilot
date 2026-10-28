console.log("[LinguaCopilot] content script loaded");
// Returns the word located under the mouse click, or null
function getWordAtPoint(x, y) {
  const range = document.caretRangeFromPoint(x, y);
  if (!range || range.startContainer.nodeType !== Node.TEXT_NODE) return null;

  const text = range.startContainer.textContent;
  const isWordChar = (c) => /[\p{L}\p{N}'-]/u.test(c);
  let start = range.startOffset;
  let end = range.startOffset;

  while (start > 0 && isWordChar(text[start - 1])) start--;
  while (end < text.length && isWordChar(text[end])) end++;

  const word = text.slice(start, end);
  return word || null;
}

// Returns the full subtitle text currently displayed
function getCaptionSentence(segment) {
  const captionWindow = segment.closest(".caption-window");
  if (!captionWindow) return segment.textContent.trim();
  return Array.from(captionWindow.querySelectorAll(".ytp-caption-segment"))
    .map((s) => s.textContent.trim())
    .join(" ");
}

document.addEventListener(
  "click",
  (event) => {
    console.log("[LinguaCopilot] click on", event.target);
    const segment = event.target.closest(".ytp-caption-segment");
    if (!segment) return;
    event.stopPropagation();
    event.preventDefault();

    const word = getWordAtPoint(event.clientX, event.clientY);
    if (!word) return;

    const video = document.querySelector("video");
    const payload = {
      word: word,
      sentence: getCaptionSentence(segment),
      video_id: new URLSearchParams(location.search).get("v"),
      timestamp_sec: video ? Math.round(video.currentTime * 10) / 10 : null,
      captured_at: new Date().toISOString(),
    };

    console.log("[LinguaCopilot]", payload);
  },
  true
);