document.addEventListener("DOMContentLoaded", () => {
  const openBtn = document.getElementById("openFloating");
  if (!openBtn) return;

  openBtn.addEventListener("click", async () => {
    try {
      // Get the active tab
      let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) return;

      // Inject the floating.js script
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ["floating.js"]
      });

      // Inject the floating.css styles
      await chrome.scripting.insertCSS({
        target: { tabId: tab.id },
        files: ["floating.css"]
      });

    } catch (err) {
      console.error("Error injecting assistant:", err);
    }
  });
});
