const chatbox = document.getElementById("chatbox");
const inputField = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");

sendBtn.addEventListener("click", sendMessage);
inputField.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const userInput = inputField.value.trim();
  if (!userInput) return;

  // Show user's message
  chatbox.innerHTML += `<p class='user'><b>You:</b> ${userInput}</p>`;
  inputField.value = "";

  // Show typing indicator
  typingIndicator.style.display = "block";

  try {
    const res = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userInput })
    });

    const data = await res.json();

    // Hide typing indicator and show bot's message
    typingIndicator.style.display = "none";
    chatbox.innerHTML += `<p class='bot'><b>Bot:</b> ${data.reply}</p>`;
  } catch (error) {
    typingIndicator.style.display = "none";
    chatbox.innerHTML += `<p class='bot'><b>Bot:</b> Error contacting server.</p>`;
  }

  chatbox.scrollTop = chatbox.scrollHeight;
}

// Emoji Picker Setup
const picker = new EmojiButton();
const emojiBtn = document.getElementById('emojiBtn');

emojiBtn.addEventListener('click', () => {
  picker.togglePicker(emojiBtn);
});

picker.on('emoji', emoji => {
  inputField.value += emoji;
  inputField.focus();
});
