let computing = 0;

document.getElementById("menu").onclick = function () {
  showInfo();
};

function showInfo() {
  alert(
    "TrinityAI - Merging the most powerful AI tools on the market into a single chat solution.\n\nUse the capabilities of ChatGPT, Google Gemini, and Anthropic AI (Claude) in a single tool."
  );
}

document.getElementById("button").onclick = function () {
  send();
};
document.addEventListener("keydown", function (event) {
  if (
    event.key === "Enter" &&
    document.activeElement === document.getElementById("text")
  ) {
    event.preventDefault();
    send();
  }
});

async function send() {
  if (computing == 0 && document.getElementById("text").value != "") {
    if (document.getElementById("welcome") != undefined) {
      document.getElementById("welcome").remove();
    }
    computing = 1;
    var question = document.getElementById("text").value;
    printMessage("user", question);
    document.getElementById("text").value = "";

    try {
      // Get responses from all three AI services
      const [openai_response, gemini_response, claude_response] =
        await Promise.all([
          getAIResponse("openai", question),
          getAIResponse("gemini", question),
          getAIResponse("claude", question),
        ]);

      // Display all responses
      printMessage("ai", `OpenAI: ${openai_response}`, "openai");
      printMessage("ai", `Gemini: ${gemini_response}`, "gemini");
      printMessage("ai", `Claude: ${claude_response}`, "claude");
    } catch (error) {
      printMessage("ai", `Error: ${error.message}`, "error");
    }

    computing = 0;
  }
}

async function getAIResponse(service, question) {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: `/${service}`,
      contentType: "application/json",
      type: "POST",
      data: JSON.stringify({ question: question }),
      success: function (data) {
        resolve(data.message);
      },
      error: function (err) {
        reject(
          new Error(`${service} failed: ${err.responseText || err.statusText}`)
        );
      },
    });
  });
}

function printMessage(type, text, aiType = null) {
  var elemwrap = document.createElement("div");
  elemwrap.style.width = "100%";
  elemwrap.style.display = "flex";
  elemwrap.style.marginTop = "20px";

  var elem = document.createElement("div");
  elem.className = "message";
  elem.style.wordBreak = "break-word";
  elem.style.whiteSpace = "normal";
  elem.style.margin = "0px 20px";
  elem.style.borderRadius = "15px";
  elem.style.padding = "10px 18px";
  elem.style.width = "fit-content";
  elem.style.maxWidth = "70%";
  elem.style.textAlign = "left";

  if (type == "user") {
    elem.style.alignSelf = "right";
    elemwrap.style.justifyContent = "right";
    elem.style.backgroundColor = "#dcdcdc";
    elem.innerText = text;
  } else {
    elem.style.alignSelf = "left";
    elemwrap.style.justifyContent = "left";

    if (aiType === "openai") {
      elem.style.backgroundColor = "#69c8ff";
    } else if (aiType === "gemini") {
      elem.style.backgroundColor = "#db4d4c";
      elem.style.color = "white";
    } else if (aiType === "claude") {
      elem.style.backgroundColor = "#eea638";
      elem.style.color = "white";
    } else {
      elem.style.backgroundColor = "#dcdcdc";
    }

    elem.innerHTML = `<strong>${
      aiType ? aiType.toUpperCase() + ": " : ""
    }</strong>${text}`;
  }

  document.getElementById("messages").appendChild(elemwrap);
  elemwrap.appendChild(elem);
  var objDiv = document.getElementById("messages");
  objDiv.scrollTop = objDiv.scrollHeight;
}
