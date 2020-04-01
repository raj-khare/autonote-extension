// Once the DOM is ready...
window.addEventListener("DOMContentLoaded", async () => {
  // ...query for the active tab...
  chrome.tabs.query(
    {
      active: true,
      currentWindow: true
    },
    tabs => getNotes(tabs[0].url)
  );
});
const ul = document.getElementById("notes-list");
const loadingContainer = document.getElementById("loading-container");

const getNotes = async url => {
  try {
    const response = await fetch("http://127.0.0.1:5000/notes", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url })
    });
    if (response.status >= 400 && response.status < 600) {
      throw new Error();
    }
    const data = await response.json();
    loadingContainer.remove();
    const notes = data.notes;
    notes.forEach(point => {
      const li = document.createElement("li");
      li.appendChild(document.createTextNode(point));
      ul.appendChild(li);
    });
  } catch {
    document.createElement("li");
    li.appendChild(
      document.createTextNode("Something went wrong. Please try again later")
    );
    ul.appendChild(li);
  }
};
