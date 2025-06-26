// Get references to the elements in the HTML (the chatbox and the input field)
const chatbox = document.getElementById("chatbox"); // The div where messages will be displayed
const inputField = document.getElementById("messageInput"); // The input field where the user types the message

// Adding an event listener to the "Send" button that triggers the sendMessage function when clicked
document.getElementById("sendBtn").addEventListener("click", sendMessage);

// Add event listener to the input field to send a message when the "Enter" key is pressed
inputField.addEventListener("keypress", function (e) {
  if (e.key === "Enter") { // Check if the "Enter" key was pressed
    sendMessage(); // Call the sendMessage function when Enter is pressed
  }
});

// Function that sends the message to the backend and handles responses
async function sendMessage() {
  const userInput = inputField.value.trim(); // Get the user input and remove extra spaces at the start and end
  if (!userInput) return; // If the user input is empty, don't do anything
  

  // Show the user's message in the chatbox
  chatbox.innerHTML += `<p class='user'><b>You:</b> ${userInput}</p>`;
  inputField.value = ""; // Clear the input field after the message is sent

  try {
    // Send the user's message to the backend using the Fetch API
    const res = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST', // The method is POST because we are sending data
      headers: { 'Content-Type': 'application/json' }, // Specify that the content type is JSON
      body: JSON.stringify({ message: userInput }) // Send the user message as JSON
    });

    // Parse the response from the backend
    const data = await res.json(); // This returns the response from the backend as a JavaScript object

    // Show the bot's reply in the chatbox
    chatbox.innerHTML += `<p class='bot'><b>Bot:</b> ${data.reply}</p>`;
  } catch (error) {
    // If there is an error (e.g., the backend is not reachable), show an error message
    chatbox.innerHTML += `<p class='bot'><b>Bot:</b> Error contacting server.</p>`;
  }

  // Automatically scroll to the latest message in the chatbox (so the user can see the new message)
  chatbox.scrollTop = chatbox.scrollHeight;
}
