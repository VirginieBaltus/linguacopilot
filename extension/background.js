importScripts("config.js");

const TRANSLATE_URL = API_URL.replace(/\/events$/, "/translate");

function postJson(url, payload, sendResponse) {
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
    },
    body: JSON.stringify(payload),
  })
    .then(async (response) => {
      const data = await response.json().catch(() => ({}));
      sendResponse({ ok: response.ok, data: data });
    })
    .catch((error) => sendResponse({ ok: false, error: error.message }));
}

// Receives requests from content.js and forwards them to the API
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SAVE_WORD") {
    postJson(API_URL, message.payload, sendResponse);
    return true;
  }
  if (message.type === "TRANSLATE_WORD") {
    postJson(TRANSLATE_URL, message.payload, sendResponse);
    return true;
  }
});