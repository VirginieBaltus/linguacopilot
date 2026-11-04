const API_URL = "https://xvbjlaakxc.execute-api.eu-north-1.amazonaws.com/events";

// Receives words from content.js and sends them to the API
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "SAVE_WORD") return;

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload),
  })
    .then(async (response) => {
      const data = await response.json().catch(() => ({}));
      sendResponse({ ok: response.ok, data: data });
    })
    .catch((error) => sendResponse({ ok: false, error: error.message }));

  // Keeps the message channel open until sendResponse is called
  return true;
});