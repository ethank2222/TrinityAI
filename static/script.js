// Remove info box and menu logic
// Navbar tab switching logic
window.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".nav-tab");
  const pages = {
    home: document.getElementById("home-page"),
    peer: document.getElementById("peer-page"),
    socratic: document.getElementById("socratic-page"),
  };
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      Object.values(pages).forEach((page) => (page.style.display = "none"));
      if (tab.dataset.tab === "home") pages.home.style.display = "block";
      if (tab.dataset.tab === "peer") pages.peer.style.display = "block";
      if (tab.dataset.tab === "socratic")
        pages.socratic.style.display = "block";
      // Remove loading overlay when switching tabs
      removeAnimatedLoader();
    });
  });
});

let computing = 0;
let chain = [];
nummessages = 0;

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

// --- Animated Progress Bar Logic ---
function showAnimatedLoader() {
  let loader = document.createElement("div");
  loader.className = "loader";
  loader.style.position = "fixed";
  loader.style.top = "50%";
  loader.style.left = "50%";
  loader.style.transform = "translate(-50%, -50%)";
  loader.style.padding = "25px 50px";
  loader.style.backgroundColor = "rgba(230, 230, 230, 0.9)";
  loader.style.borderRadius = "5px";
  loader.style.textAlign = "center";
  loader.innerHTML = `
        <h2 style="margin: 0px 0px 5px">Loading Response</h2>
        <div class="animated-progress"><div class="animated-progress-bar" id="animated-progress-bar"></div><span class="animated-progress-label" id="animated-progress-label">0%</span></div>
        <p id="progress-text">Receiving initial responses</p>
    `;
  document.body.appendChild(loader);
  // Set initial color (light blue)
  setAnimatedProgressBarColor("blue");
}
function removeAnimatedLoader() {
  let x = document.getElementsByClassName("loader");
  for (let i = 0; i < x.length; i++) x[i].remove();
}

// Set the animated progress bar color by theme
function setAnimatedProgressBarColor(theme) {
  let bar = document.getElementById("animated-progress-bar");
  if (!bar) return;
  if (theme === "blue") {
    bar.style.background = "linear-gradient(90deg, #b3e0ff 0%, #e6f7ff 100%)";
  } else if (theme === "red") {
    bar.style.background = "linear-gradient(90deg, #ffb3b3 0%, #db4d4c 100%)";
  } else if (theme === "orange") {
    bar.style.background = "linear-gradient(90deg, #ffe6c7 0%, #fff6e6 100%)";
  } else if (theme === "green") {
    bar.style.background = "linear-gradient(90deg, #c7ffe6 0%, #e6fff6 100%)";
  } else {
    bar.style.background = "linear-gradient(90deg, #b3e0ff 0%, #e6f7ff 100%)";
  }
}

// Progress bar animation logic
let progressTarget = 0;
let progressCurrent = 0;
let progressInterval = null;
let progressStep = 0;
let progressAnimating = false;

function animateProgressTo(target) {
  debugLog("Animating progress to target:", target);
  progressTarget = target;
  if (!progressInterval) {
    progressInterval = setInterval(() => {
      // Always slowly increase unless at the current milestone
      if (progressCurrent < progressTarget) {
        // If we're close to the target, snap to it
        if (progressTarget - progressCurrent < 1) {
          progressCurrent = progressTarget;
        } else {
          // Always increase, but slow
          progressCurrent += Math.max(
            0.15,
            (progressTarget - progressCurrent) * 0.03
          );
        }
        updateAnimatedProgressBar();
      } else if (progressCurrent > progressTarget) {
        progressCurrent = progressTarget;
        updateAnimatedProgressBar();
      }
      // Hide loader when at 100%
      if (progressCurrent >= 100) {
        progressCurrent = 100;
        updateAnimatedProgressBar();
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
        setTimeout(removeAnimatedLoader, 200); // Hide loader after a short delay
      }
    }, 20);
  }
}
function updateAnimatedProgressBar() {
  debugLog("Updating progress bar:", progressCurrent);
  let bar = document.getElementById("animated-progress-bar");
  let label = document.getElementById("animated-progress-label");
  if (bar && label) {
    bar.style.width = progressCurrent + "%";
    label.innerText = Math.round(progressCurrent) + "%";
  }
}
function setProgressStep(step) {
  // 10 steps, so each is 10%
  progressStep = step;
  let pct = Math.max(step * 10, progressCurrent);
  // Set color by major section
  // 0-2: initial (blue), 3-5: peer editing (red), 6-8: voting/tallying (orange), 9-10: final (green)
  if (step <= 2) {
    setAnimatedProgressBarColor("blue");
  } else if (step <= 5) {
    setAnimatedProgressBarColor("red");
  } else if (step <= 8) {
    setAnimatedProgressBarColor("orange");
  } else {
    setAnimatedProgressBarColor("green");
  }
  // If the bar is behind, jump to the new step
  if (progressCurrent < pct) {
    progressTarget = pct;
    animateProgressTo(progressTarget);
  } else {
    // If the bar is at or ahead, keep animating slowly
    progressTarget = pct;
  }
}

// --- Constants for LLMs ---
const LLM_NAMES = ["OpenAI", "Grok", "Anthropic"];
const LLM_CLASSES = ["openai", "grok", "anthropic"];

// Socratic Analysis frontend logic
function renderSocraticResults(data) {
  const resultsDiv = document.getElementById("socratic-results");
  resultsDiv.innerHTML = "";
  if (data.turns && data.turns.length > 0) {
    data.turns.forEach((turn, idx) => {
      const wrapper = document.createElement("div");
      // Assign color class based on LLM
      let llmClass = "";
      if (turn.llm.toLowerCase().includes("openai")) llmClass = "openai";
      else if (turn.llm.toLowerCase().includes("grok")) llmClass = "grok";
      else if (turn.llm.toLowerCase().includes("anthropic"))
        llmClass = "anthropic";
      wrapper.className = `socratic-thought ${llmClass}`;
      wrapper.style.margin = "18px 0";
      wrapper.style.borderRadius = "10px";
      wrapper.style.boxShadow = "0 1px 6px rgba(0,0,0,0.06)";
      wrapper.style.padding = "0";
      wrapper.style.overflow = "hidden";
      // Header/overview
      const header = document.createElement("div");
      header.className = "socratic-overview";
      header.setAttribute("tabindex", "0"); // keyboard accessible
      header.style.cursor = "pointer";
      header.style.padding = "16px 20px";
      header.style.fontWeight = "bold";
      header.style.background = "#eaf2ff";
      header.innerHTML = `<span style="color:#69c8ff;">${turn.llm}</span>: ${turn.overview}`;
      // Full thought (hidden by default)
      const full = document.createElement("div");
      full.className = "socratic-full";
      full.style.display = "none";
      full.style.padding = "16px 20px";
      full.style.background = "#fff";
      full.innerText = turn.full;
      // Toggle
      header.onclick = header.onkeydown = (e) => {
        if (e.type === "click" || e.key === "Enter" || e.key === " ") {
          full.style.display = full.style.display === "none" ? "block" : "none";
        }
      };
      wrapper.appendChild(header);
      wrapper.appendChild(full);
      resultsDiv.appendChild(wrapper);
    });
  }
  // Summary
  if (data.summary) {
    const summaryDiv = document.createElement("div");
    summaryDiv.style.margin = "32px 0 0 0";
    summaryDiv.style.padding = "18px 22px";
    summaryDiv.style.background = "#e6f7e6";
    summaryDiv.style.borderRadius = "10px";
    summaryDiv.style.fontSize = "1.1rem";
    summaryDiv.innerHTML = `<b>Summary:</b> ${data.summary}`;
    resultsDiv.appendChild(summaryDiv);
  }
  if (data.agreement) {
    const agreeDiv = document.createElement("div");
    agreeDiv.style.margin = "18px 0 0 0";
    agreeDiv.style.padding = "14px 20px";
    agreeDiv.style.background = "#fffbe6";
    agreeDiv.style.borderRadius = "10px";
    agreeDiv.innerHTML = `<b>Agreement:</b> ${data.agreement}`;
    resultsDiv.appendChild(agreeDiv);
  }
  if (data.arguments) {
    const argDiv = document.createElement("div");
    argDiv.style.margin = "18px 0 0 0";
    argDiv.style.padding = "14px 20px";
    argDiv.style.background = "#f0f0f0";
    argDiv.style.borderRadius = "10px";
    argDiv.innerHTML = `<b>Arguments:</b> ${data.arguments}`;
    resultsDiv.appendChild(argDiv);
  }
}

function summarizeError(errText) {
  if (!errText) return "Service unavailable.";
  const firstLine = errText.split("\n")[0];
  if (/429|rate limit/i.test(firstLine)) return "Rate limit exceeded.";
  if (/quota/i.test(firstLine)) return "Quota exceeded.";
  if (/INTERNAL SERVER ERROR/i.test(firstLine)) return "Internal server error.";
  if (/timeout/i.test(firstLine)) return "Request timed out.";
  if (/network/i.test(firstLine)) return "Network error.";
  return "Service unavailable.";
}
// --- Error handling for LLM failures in Peer Review ---
async function send() {
  if (computing == 0 && document.getElementById("text").value != "") {
    if (document.getElementById("welcome") != undefined) {
      document.getElementById("welcome").remove();
    }
    computing = 1;
    var question = document.getElementById("text").value;
    chain.push(question);
    nummessages++;
    printMessage("user", question, 4);
    document.getElementById("text").value = "";
    let openai_response,
      grok_response,
      claude_response,
      response1,
      response2,
      response3,
      vote1,
      vote2,
      vote3;
    var done = 0;
    showAnimatedLoader();
    progressCurrent = 0;
    setProgressStep(0);
    let errorMessages = [];
    // Get first responses in parallel
    let firstResponses = await Promise.all([
      new Promise((resolve) => {
        $.ajax({
          url: "/openaiFirstResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: question }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            errorMessages.push(
              "OpenAI failed: " + summarizeError(err.responseText)
            );
            resolve("[OpenAI Error: " + summarizeError(err.responseText) + "]");
          },
        });
      }),
      new Promise((resolve) => {
        $.ajax({
          url: "/grokFirstResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: question }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            errorMessages.push(
              "Grok failed: " + summarizeError(err.responseText)
            );
            resolve("[Grok Error: " + summarizeError(err.responseText) + "]");
          },
        });
      }),
      new Promise((resolve) => {
        $.ajax({
          url: "/claudeFirstResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: question }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            errorMessages.push(
              "Anthropic failed: " + summarizeError(err.responseText)
            );
            resolve(
              "[Anthropic Error: " + summarizeError(err.responseText) + "]"
            );
          },
        });
      }),
    ]);
    openai_response = firstResponses[0];
    grok_response = firstResponses[1];
    claude_response = firstResponses[2];
    if (errorMessages.length > 0) {
      let loader = document.getElementsByClassName("loader")[0];
      if (loader) {
        let errorDiv = document.createElement("div");
        errorDiv.style.color = "red";
        errorDiv.style.marginTop = "16px";
        errorDiv.innerHTML = errorMessages
          .map((e) => `<div>${e}</div>`)
          .join("");
        loader.appendChild(errorDiv);
      }
    }
    done = 3;
    setProgressStep(done);
    document.getElementById("progress-text").innerHTML =
      "Peer editing the responses";
    // Modify responses in parallel
    let modPrompt =
      "Here was the question that was given: " +
      question +
      " Given the following three responses, use the best and most accurate information from each to write a new consolidated response to the question: 1. " +
      openai_response +
      " 2. " +
      grok_response +
      " 3. " +
      claude_response +
      ". Do not give any qualifiers like 'here's a consolidated response based on the given information.";
    let modResponses = await Promise.all([
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/openaiModifyingResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: modPrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/grokModifyingResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: modPrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/claudeModifyingResponse",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: modPrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
    ]);
    response1 = modResponses[0];
    response2 = modResponses[1];
    response3 = modResponses[2];
    done = 6;
    setProgressStep(done);
    document.getElementById("progress-text").innerHTML = "Collecting votes";
    // Voting in parallel
    let votePrompt =
      "Here was the question that was given: " +
      question +
      " Given the following three responses, return only the number of the best response. 1. " +
      response1 +
      " 2. " +
      response2 +
      " 3. " +
      response3 +
      " Remember, only return the number '1', '2', or '3' as a standalone number.";
    let votes = await Promise.all([
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/openaiVoting",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: votePrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/grokVoting",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: votePrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
      new Promise((resolve, reject) => {
        $.ajax({
          url: "/claudeVoting",
          contentType: "application/json",
          type: "POST",
          data: JSON.stringify({ question: votePrompt }),
          success: function (data) {
            resolve(data.message);
          },
          error: function (err) {
            reject(err);
          },
        });
      }),
    ]);
    vote1 = votes[0];
    vote2 = votes[1];
    vote3 = votes[2];
    done = 9;
    setProgressStep(done);
    document.getElementById("progress-text").innerHTML = "Tallying Votes";
    // Tally votes
    var votesfor1 = 0;
    var votesfor2 = 0;
    var votesfor3 = 0;
    if (vote1 == 1) {
      votesfor1 += 1;
    } else if (vote1 == 2) {
      votesfor2 += 1;
    } else if (vote1 == 3) {
      votesfor3 += 1;
    }
    if (vote2 == 1) {
      votesfor1 += 1;
    } else if (vote2 == 2) {
      votesfor2 += 1;
    } else if (vote2 == 3) {
      votesfor3 += 1;
    }
    if (vote3 == 1) {
      votesfor1 += 1;
    } else if (vote3 == 2) {
      votesfor2 += 1;
    } else if (vote3 == 3) {
      votesfor3 += 1;
    }
    var best_response = response3;
    let toolIndex = 3;
    if (votesfor1 > votesfor2 && votesfor1 > votesfor3) {
      best_response = response1;
      toolIndex = 1;
    }
    if (votesfor2 > votesfor1 && votesfor2 > votesfor3) {
      best_response = response2;
      toolIndex = 2;
    }
    tempGlobal = best_response;
    console.log(tempGlobal);
    done = 10;
    setProgressStep(done);
    // Wait for progress bar to reach 100% before showing the message
    await waitForProgressBarToComplete();
    setTimeout(removeAnimatedLoader, 400);
    nummessages++;
    chain.push(best_response);
    printMessage("computer", best_response, toolIndex);
    computing = 0;
  }
}

function waitForProgressBarToComplete() {
  return new Promise((resolve) => {
    function check() {
      if (progressCurrent >= 100) {
        resolve();
      } else {
        setTimeout(check, 10);
      }
    }
    check();
  });
}

function printMessage(type, text, tool) {
  var elemwrap = document.createElement("div");
  elemwrap.style.width = "100%";
  elemwrap.style.display = "flex";
  elemwrap.style.marginTop = "20px";
  var elem = document.createElement("div");
  // Assign modern classes for styling
  if (type === "user") {
    elem.className = "message user";
  } else {
    let toolClass = "";
    if (tool === 1) toolClass = "openai";
    else if (tool === 2) toolClass = "grok";
    else if (tool === 3) toolClass = "anthropic";
    elem.className = `message trinityResponse ${toolClass}`;
  }
  elem.style.wordBreak = "auto-phrase";
  elem.style.whiteSpace = "normal";
  elem.style.margin = "0px 20px";
  elem.style.width = "fit-content";
  elem.style.maxWidth = "70%";
  elem.style.textAlign = "left";
  if (type == "user") {
    elem.style.alignSelf = "right";
    elemwrap.style.justifyContent = "right";
    elem.innerText = text;
  } else {
    toolNames = ["ChatGPT (Open AI)", "Grok (xAI)", "Claude (Anthropic AI)"];
    toolLinks = [
      "https://openai.com/chatgpt/",
      "https://grok.x.ai/",
      "https://claude.ai/",
    ];
    elem.innerHTML =
      `
          <span class="trinity-meta"><a target="_blank" href="` +
      toolLinks[tool - 1] +
      `" style="font-size: 12px; color: inherit; text-decoration: underline; font-style: italic;">Largest Contributor: ` +
      toolNames[tool - 1] +
      `</a></span>
      ` +
      text +
      `
      <div>
          <label for="cars">Submit Feedback:</label>
          <select name="options">
              <option value="10">10</option>
              <option value="9">9</option>
              <option value="8">8</option>
              <option value="7">7</option>
              <option value="6">6</option>
              <option value="5">5</option>
              <option value="4">4</option>
              <option value="3">3</option>
              <option value="2">2</option>
              <option value="1">1</option>
          </select>
          <button style="cursor:pointer;" onclick=submitFeedback(this)>Submit</button>
      </div>
      `;
    elem.style.alignSelf = "left";
  }
  document.getElementById("messages").appendChild(elemwrap);
  elemwrap.appendChild(elem);
  var objDiv = document.getElementById("messages");
  objDiv.scrollTop = objDiv.scrollHeight;
}
async function submitFeedback(button) {
  var question =
    button.parentNode.parentNode.parentNode.previousElementSibling.children[0]
      .innerText;
  var score = button.parentNode.children[1].value;
  var tool = "openai";
  if (button.parentNode.parentNode.children[0].innerText.includes("Grok")) {
    tool = "grok";
  }
  if (button.parentNode.parentNode.children[0].innerText.includes("claude")) {
    tool = "claude";
  }
  var resp = await new Promise((resolve, reject) => {
    $.ajax({
      url: "/postDatapoint",
      contentType: "application/json",
      type: "POST",
      data: JSON.stringify({
        question: question,
        tool: tool,
        score: score,
      }),
      success: function (data) {
        resolve(data.message);
      },
      error: function (err) {
        reject(err);
      },
    });
  });
  button.parentNode.innerHTML = resp;
}

// Socratic Analysis error display in loader
function showSocraticLoader(msg) {
  document.getElementById(
    "socratic-results"
  ).innerHTML = `<div class="socratic-loader" style="padding:20px;">${
    msg ||
    'Analyzing... <span class="loader-dot">.</span><span class="loader-dot">.</span><span class="loader-dot">.</span> (this may take up to 3 minutes)'
  }</div>`;
}
// Socratic Analysis incremental display logic
let socraticPolling = null;
let socraticSessionId = null;
let socraticLastTurnCount = 0;

// DEBUG: Log key events and data for Socratic Analysis and progress bar
function debugLog(...args) {
  if (window.DEBUG_SOCRATIC) {
    console.log("[Socratic Debug]", ...args);
  }
}

// --- Socratic Analysis debug hooks ---
function renderSocraticTurnsIncremental(data) {
  debugLog(
    "Rendering Socratic turns, current count:",
    socraticLastTurnCount,
    "new data:",
    data
  );
  const resultsDiv = document.getElementById("socratic-results");
  // Only append new turns
  if (!data.turns || data.turns.length === 0) return;
  for (let i = socraticLastTurnCount; i < data.turns.length; i++) {
    const turn = data.turns[i];
    debugLog("Rendering Socratic turn:", turn);
    const wrapper = document.createElement("div");
    let llmClass = "";
    if (turn.llm.toLowerCase().includes("openai")) llmClass = "openai";
    else if (turn.llm.toLowerCase().includes("grok")) llmClass = "grok";
    else if (turn.llm.toLowerCase().includes("anthropic"))
      llmClass = "anthropic";
    wrapper.className = `socratic-thought ${llmClass}`;
    wrapper.style.margin = "18px 0";
    wrapper.style.borderRadius = "10px";
    wrapper.style.boxShadow = "0 1px 6px rgba(0,0,0,0.06)";
    wrapper.style.padding = "0";
    wrapper.style.overflow = "hidden";
    const header = document.createElement("div");
    header.className = "socratic-overview";
    header.setAttribute("tabindex", "0");
    header.style.cursor = "pointer";
    header.style.padding = "16px 20px";
    header.style.fontWeight = "bold";
    header.style.background = "#eaf2ff";
    header.innerHTML = `<span style="color:#69c8ff;">${turn.llm}</span>: ${turn.overview}`;
    const full = document.createElement("div");
    full.className = "socratic-full";
    full.style.display = "none";
    full.style.padding = "16px 20px";
    full.style.background = "#fff";
    full.innerText = turn.full;
    header.onclick = header.onkeydown = (e) => {
      if (e.type === "click" || e.key === "Enter" || e.key === " ") {
        full.style.display = full.style.display === "none" ? "block" : "none";
      }
    };
    wrapper.appendChild(header);
    wrapper.appendChild(full);
    resultsDiv.appendChild(wrapper);
  }
  socraticLastTurnCount = data.turns.length;
  // If finished, show summary/arguments/agreement
  if (data.summary || data.agreement || data.arguments) {
    debugLog(
      "Rendering Socratic summary/agreement/arguments:",
      data.summary,
      data.agreement,
      data.arguments
    );
    if (data.summary) {
      const summaryDiv = document.createElement("div");
      summaryDiv.style.margin = "32px 0 0 0";
      summaryDiv.style.padding = "18px 22px";
      summaryDiv.style.background = "#e6f7e6";
      summaryDiv.style.borderRadius = "10px";
      summaryDiv.style.fontSize = "1.1rem";
      summaryDiv.innerHTML = `<b>Summary:</b> ${data.summary}`;
      resultsDiv.appendChild(summaryDiv);
    }
    if (data.agreement) {
      const agreeDiv = document.createElement("div");
      agreeDiv.style.margin = "18px 0 0 0";
      agreeDiv.style.padding = "14px 20px";
      agreeDiv.style.background = "#fffbe6";
      agreeDiv.style.borderRadius = "10px";
      agreeDiv.innerHTML = `<b>Agreement:</b> ${data.agreement}`;
      resultsDiv.appendChild(agreeDiv);
    }
    if (data.arguments) {
      const argDiv = document.createElement("div");
      argDiv.style.margin = "18px 0 0 0";
      argDiv.style.padding = "14px 20px";
      argDiv.style.background = "#f0f0f0";
      argDiv.style.borderRadius = "10px";
      argDiv.innerHTML = `<b>Arguments:</b> ${data.arguments}`;
      resultsDiv.appendChild(argDiv);
    }
  }
}

function pollSocraticResults() {
  if (!socraticSessionId) return;
  debugLog("Polling Socratic results for session:", socraticSessionId);
  fetch(
    `/socraticAnalysisStream?session_id=${encodeURIComponent(
      socraticSessionId
    )}`
  )
    .then((resp) => resp.json())
    .then((data) => {
      debugLog("Polled Socratic data:", data);
      renderSocraticTurnsIncremental(data);
      if (data.finished || (data.summary && data.agreement && data.arguments)) {
        debugLog("Socratic polling finished");
        clearInterval(socraticPolling);
        socraticPolling = null;
      }
    })
    .catch((e) => {
      debugLog("Error in Socratic polling:", e);
      clearInterval(socraticPolling);
      socraticPolling = null;
    });
}

function socraticSubmit() {
  const input = document.getElementById("socratic-input");
  const question = input.value;
  if (!question) return;
  debugLog("Submitting Socratic question:", question);
  // Clear the input immediately
  input.value = "";
  // Clear results area first, then show loader
  document.getElementById("socratic-results").innerHTML = "";
  showSocraticLoader(
    "Thinking about: <b>" +
      question.replace(/</g, "&lt;").replace(/>/g, "&gt;") +
      "</b>"
  );
  socraticLastTurnCount = 0;
  // Start a new Socratic session
  fetch("/socraticAnalysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })
    .then((resp) => resp.json())
    .then((data) => {
      debugLog("Received initial Socratic session data:", data);
      // Assume backend returns a session_id for polling
      socraticSessionId = data.session_id || "default";
      renderSocraticTurnsIncremental(data);
      if (!data.finished && !socraticPolling) {
        debugLog("Starting Socratic polling interval");
        socraticPolling = setInterval(pollSocraticResults, 1000); // Faster polling
      }
    })
    .catch((e) => {
      debugLog("Error in Socratic submit:", e);
      let msg =
        e && e.message ? summarizeError(e.message) : "Service unavailable.";
      showSocraticLoader('<span style="color:red;">' + msg + "</span>");
    });
}
document.getElementById("socratic-send").onclick = socraticSubmit;
document
  .getElementById("socratic-input")
  .addEventListener("keydown", function (e) {
    // Submit on Enter (without Shift/Ctrl/Cmd), allow Shift+Enter for newline
    if (
      e.key === "Enter" &&
      !e.shiftKey &&
      !e.ctrlKey &&
      !e.metaKey &&
      this.value.trim() !== ""
    ) {
      e.preventDefault();
      socraticSubmit();
    } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      socraticSubmit();
    }
  });

// Hamburger menu logic for responsive navbar
window.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".nav-tab");
  const pages = {
    home: document.getElementById("home-page"),
    peer: document.getElementById("peer-page"),
    socratic: document.getElementById("socratic-page"),
  };
  const hamburger = document.getElementById("navbar-hamburger");
  const dropdown = document.getElementById("navbar-dropdown");
  const mainTabs = document.querySelectorAll("#navbar-tabs .nav-tab");
  const dropdownTabs = document.querySelectorAll("#navbar-dropdown .nav-tab");

  // Tab switching logic (main and dropdown)
  function activateTab(tabName) {
    // Main tabs
    mainTabs.forEach((t) => t.classList.remove("active"));
    // Dropdown tabs
    dropdownTabs.forEach((t) => t.classList.remove("active"));
    // Activate correct tab in both
    document
      .querySelectorAll('.nav-tab[data-tab="' + tabName + '"]')
      .forEach((t) => t.classList.add("active"));
    // Show correct page
    Object.values(pages).forEach((page) => (page.style.display = "none"));
    if (tabName === "home") pages.home.style.display = "block";
    if (tabName === "peer") pages.peer.style.display = "block";
    if (tabName === "socratic") pages.socratic.style.display = "block";
    // Hide dropdown if open
    dropdown.style.display = "none";
  }
  mainTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      activateTab(tab.dataset.tab);
    });
  });
  dropdownTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      activateTab(tab.dataset.tab);
    });
  });
  // Hamburger toggle
  hamburger.addEventListener("click", function (e) {
    e.stopPropagation();
    dropdown.style.display =
      dropdown.style.display === "flex" ? "none" : "flex";
  });
  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (
      dropdown.style.display === "flex" &&
      !dropdown.contains(e.target) &&
      e.target !== hamburger
    ) {
      dropdown.style.display = "none";
    }
  });
  // Keyboard accessibility
  hamburger.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      dropdown.style.display =
        dropdown.style.display === "flex" ? "none" : "flex";
    }
  });
  // Ensure homepage is active on load
  activateTab("home");
});

// --- Keyboard accessibility for dropdown tabs ---
window.addEventListener("DOMContentLoaded", function () {
  const dropdownTabs = document.querySelectorAll("#navbar-dropdown .nav-tab");
  dropdownTabs.forEach((tab) => {
    tab.setAttribute("tabindex", "0");
    tab.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        tab.click();
      }
    });
  });
});

// --- Responsive chat/input area ---
window.addEventListener("resize", function () {
  const wrapper = document.querySelector(".wrapper");
  if (window.innerWidth < 700) {
    wrapper.style.width = "98vw";
  } else {
    wrapper.style.width = "80%";
  }
});

// Make the animated progress bar lighter by injecting a lighter background color
// This will override the default style if present
(function () {
  const style = document.createElement("style");
  style.innerHTML = `
    .animated-progress-bar {
      background: linear-gradient(90deg, #b3e0ff 0%, #e6f7ff 100%) !important;
    }
  `;
  document.head.appendChild(style);
})();
