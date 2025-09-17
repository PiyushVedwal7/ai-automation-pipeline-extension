// Check if assistant already exists
if (!document.getElementById("aiFloating")) {

  const container = document.createElement("div");
  container.id = "aiFloating";
  container.innerHTML = `
    <div id="aiHeader">
      🤖 AI Assistant
      <button id="aiCollapse">−</button>
      <button id="aiClose">×</button>
    </div>
    <div id="aiBody">
      <div id="aiChat"></div>
      <input type="text" id="aiInput" placeholder="Type or speak command..." />
      <button id="aiSend">Send</button>
      <button id="aiMic">🎤</button>
    </div>
  `;
  document.body.appendChild(container);

  // ----- Draggable -----
  const header = document.getElementById("aiHeader");
  let offsetX, offsetY, isDragging = false;

  header.onmousedown = (e) => {
    if (e.target.id === "aiCollapse" || e.target.id === "aiClose") return;
    isDragging = true;
    offsetX = e.clientX - container.getBoundingClientRect().left;
    offsetY = e.clientY - container.getBoundingClientRect().top;
  };

  document.onmousemove = (e) => {
    if (!isDragging) return;
    container.style.left = e.clientX - offsetX + "px";
    container.style.top = e.clientY - offsetY + "px";
  };

  document.onmouseup = () => isDragging = false;

  // ----- Collapse/Expand -----
  const body = document.getElementById("aiBody");
  const collapseBtn = document.getElementById("aiCollapse");
  collapseBtn.onclick = () => {
    if (body.style.display === "none") {
      body.style.display = "block";
      collapseBtn.textContent = "−";
    } else {
      body.style.display = "none";
      collapseBtn.textContent = "+";
    }
  };

  // ----- Close -----
  const closeBtn = document.getElementById("aiClose");
  closeBtn.onclick = () => container.style.display = "none";

  // ----- Send command -----
  const input = document.getElementById("aiInput");
  const sendBtn = document.getElementById("aiSend");
  const chat = document.getElementById("aiChat");

  sendBtn.onclick = async () => {
    const command = input.value;
    if (!command) return;
    addMessage("You: " + command, "user");
    input.value = "";
    try {
      const res = await fetch("http://127.0.0.1:5000/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
      });
      const data = await res.json();
      if (data.result) {
        addMessage("AI Pipeline Result:", "ai");
        data.result.forEach(c => addMessage("- " + c, "ai"));
      } else if (data.reply) {
        addMessage("AI: " + data.reply, "ai");
      } else if (data.error) {
        addMessage("⚠️ " + JSON.stringify(data.error), "ai");
      }
    } catch (err) {
      addMessage("⚠️ Error: " + err.message, "ai");
    }
  };

  function addMessage(text, cls){
    const p = document.createElement("p");
    p.textContent = text;
    p.className = cls;
    chat.appendChild(p);
    chat.scrollTop = chat.scrollHeight;
  }

}
