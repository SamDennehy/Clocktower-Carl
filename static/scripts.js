let timerInterval;
let confettiAnimationFrame;
const carlFrameDurations = [200, 150, 90];
const carlFrameOrder = [0, 1, 2, 1, 0];
const carlIdleDuration = 30000;
const timerCrazyDuration = 5000;
const scriptStorageKey = "clocktowerScript";
const audioToggleButton = document.getElementById("toggle-audio-button");
let audioToggle = true;
const screamingToggleButton = document.getElementById("toggle-screaming-button");
let screamingToggle = true;
let timerCrazyTimeout;

if (audioToggleButton) {
    audioToggleButton.addEventListener("click", function() {
        audioToggle = !audioToggle;
        audioToggleButton.textContent = audioToggle ? "Audio On" : "Audio Off";
        }
    )
};

if (screamingToggleButton) {
    screamingToggleButton.addEventListener("click", function() {
        screamingToggle = !screamingToggle;
        screamingToggleButton.textContent = screamingToggle ? "Screaming On" : "Screaming Off";
        }
    )
};

async function updateLogs() {
    const logsElement = document.getElementById("logs-container");
    if (!logsElement) {
        return;
    }

    try {
        const response = await fetch("/logs");
        if (!response.ok) {
            throw new Error(`Log request failed with status ${response.status}`);
        }

        const data = await response.json();

        logsElement.innerHTML = "";

        data.logs.forEach(log => {
            const logElement = document.createElement("div");
            logElement.textContent = log;
            logsElement.appendChild(logElement);
        });
    } catch (error) {
        console.error("Unable to update logs:", error);
    }
}

if (document.getElementById("logs-container")) {
    updateLogs();
    setInterval(updateLogs, 1000);
}

function addSubmitHandler(formId, handler) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener("submit", handler);
    }
}

addSubmitHandler("timer-form", setTimer);

addSubmitHandler("echo-form", async function(event) {
    event.preventDefault();

    const form = event.target;

    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form)
    });

	if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("join-voice-form", async function(event) {
	event.preventDefault();
	const form = event.target;

	const response = await fetch(form.action, {
		method: "POST",
		body: new FormData(form)
	});

	if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("leave-voice-form", async function(event) {
	event.preventDefault();
	const form = event.target;

	const response = await fetch(form.action, {
		method: "POST",
		body: new FormData(form)
	});

	if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("tts-form", async function(event) {
    event.preventDefault();
    const form = event.target;

    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form)
    });

    if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("mp3-form", async function(event) {
    event.preventDefault();
    const form = event.target;

    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form)
    });

    if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("set-auto-react-form", async function(event) {
    event.preventDefault();
    const form = event.target;

    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form)
    });

    if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

addSubmitHandler("disable-auto-react-form", async function(event) {
    event.preventDefault();
    const form = event.target;

    const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form)
    });

    if (!response.ok) {
        const error = await response.text();
        console.log(error);
        return;
    }
});

function setTimer(event) {
    event.preventDefault();
    const durationInput = document.getElementById("timer-duration");
    const durationSeconds = parseInt(durationInput.value, 10);

    if (isNaN(durationSeconds) || durationSeconds <= 0) {
        console.error("Invalid timer duration");
        return;
    }
    
    if (durationSeconds === 2809) {
        displayEasterEgg("Happy Birthday Dean!");
        return;
    }
    else if (durationSeconds === 67) {
        displayEasterEgg("67");
        return;
    }
    else {
        startTimer(Date.now() + durationSeconds * 1000);
    }
}

function startTimer(endTime) {
    clearInterval(timerInterval);
    clearTimeout(timerCrazyTimeout);

    const timerCarl = document.querySelector(".timer-carl");
    if (timerCarl) {
        timerCarl.classList.remove("timer-expired");
    }

    const timerDisplay = document.getElementById("timer-display");

    if (!timerDisplay) {
        return;
    }

    sessionStorage.setItem("timerEndTime", String(endTime));

    function updateTimerDisplay() {
        const remainingSeconds = Math.max(0, Math.ceil((endTime - Date.now()) / 1000));
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;
        timerDisplay.textContent = `${minutes}m ${seconds}s`;

        if (remainingSeconds <= 0) {
            clearInterval(timerInterval);
            sessionStorage.removeItem("timerEndTime");

            if (timerCarl) {
                var chimeAudio = document.getElementById("chime-audio");
                var changeCarlFaceAndScream = () => {
                    timerCarl.classList.add("timer-expired");
                    timerCrazyTimeout = setTimeout(() => {
                        timerCarl.classList.remove("timer-expired");
                    }, timerCrazyDuration);

                    var screamingAudio = document.getElementById("screaming-audio");
                    if (screamingAudio && audioToggle && screamingToggle) {
                        screamingAudio.currentTime = 0;
                        screamingAudio.play();
                    }
                };

                if (chimeAudio && audioToggle) {
                    chimeAudio.currentTime = 0;
                    chimeAudio.addEventListener("ended", changeCarlFaceAndScream, { once: true });
                    chimeAudio.play();
                } else {
                    changeCarlFaceAndScream();
                }
            }
        }
    }

    updateTimerDisplay();
    timerInterval = setInterval(updateTimerDisplay, 250);
}

function displayEasterEgg(message) {
    const easterEgg = document.getElementById("watching-message");
    if (easterEgg) {
        easterEgg.textContent = message;
    }

    launchConfetti();
}

function launchConfetti() {
    const existingCanvas = document.getElementById("confetti-canvas");
    if (existingCanvas) {
        existingCanvas.remove();
    }

    if (confettiAnimationFrame) {
        cancelAnimationFrame(confettiAnimationFrame);
    }

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    const colors = ["#f7d774", "#ffffff", "#ff6b6b", "#69d2e7", "#9be564"];
    const particles = [];
    const pixelRatio = window.devicePixelRatio || 1;
    const endTime = performance.now() + 3500;

    canvas.id = "confetti-canvas";
    document.body.appendChild(canvas);

    function resizeCanvas() {
        canvas.width = window.innerWidth * pixelRatio;
        canvas.height = window.innerHeight * pixelRatio;
        canvas.style.width = `${window.innerWidth}px`;
        canvas.style.height = `${window.innerHeight}px`;
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    }

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas, { once: true });

    for (let index = 0; index < 140; index += 1) {
        particles.push({
            x: Math.random() * window.innerWidth,
            y: -20 - Math.random() * window.innerHeight * 0.35,
            width: 5 + Math.random() * 7,
            height: 8 + Math.random() * 9,
            speed: 2 + Math.random() * 4,
            drift: -1.5 + Math.random() * 3,
            rotation: Math.random() * Math.PI,
            rotationSpeed: -0.15 + Math.random() * 0.3,
            color: colors[index % colors.length]
        });
    }

    function animateConfetti(currentTime) {
        context.clearRect(0, 0, window.innerWidth, window.innerHeight);

        particles.forEach(particle => {
            particle.y += particle.speed;
            particle.x += particle.drift;
            particle.rotation += particle.rotationSpeed;

            context.save();
            context.translate(particle.x, particle.y);
            context.rotate(particle.rotation);
            context.fillStyle = particle.color;
            context.fillRect(-particle.width / 2, -particle.height / 2, particle.width, particle.height);
            context.restore();
        });

        if (currentTime < endTime) {
            confettiAnimationFrame = requestAnimationFrame(animateConfetti);
        } else {
            canvas.remove();
            confettiAnimationFrame = undefined;
        }
    }

    confettiAnimationFrame = requestAnimationFrame(animateConfetti);
}

const savedTimerEndTime = Number(sessionStorage.getItem("timerEndTime"));

if (savedTimerEndTime > Date.now()) {
    startTimer(savedTimerEndTime);
}

function startCarlCycle() {
    const carlImages = Array.from(document.querySelectorAll(".timer-carl-image"));

    if (carlImages.length === 0) {
        return;
    }

    let sequenceIndex = 0;

    function showNextFrame() {
        const frameIndex = carlFrameOrder[sequenceIndex];

        carlImages.forEach((image, index) => {
            image.style.opacity = index === frameIndex ? "1" : "0";
        });

        const frameDuration = carlFrameDurations[frameIndex] ?? carlFrameDurations.at(-1);
        sequenceIndex += 1;

        if (sequenceIndex >= carlFrameOrder.length) {
            sequenceIndex = 0;
            setTimeout(showNextFrame, frameDuration + carlIdleDuration);
            return;
        }

        setTimeout(showNextFrame, frameDuration);
    }

    showNextFrame();
}

startCarlCycle();

const seatingForm = document.getElementById("seating-form");

if (seatingForm) {
    const playerNamesInput = document.getElementById("player-names");
    const seating = document.getElementById("player-seating");
    const seatStatusStorageKey = "playerSeatStatuses";

    function getSeatStatuses() {
        try {
            const savedStatuses = JSON.parse(localStorage.getItem(seatStatusStorageKey) || "[]");
            if (!Array.isArray(savedStatuses)) {
                return [];
            }

            return savedStatuses.map(status => {
                if (status === true) {
                    return { dead: true, ghostVote: false };
                }
                if (status === "ghostVote") {
                    return { dead: false, ghostVote: true };
                }
                return {
                    dead: Boolean(status && status.dead),
                    ghostVote: Boolean(status && status.ghostVote)
                };
            });
        } catch {
            return [];
        }
    }

    function saveSeatStatuses(statuses) {
        localStorage.setItem(seatStatusStorageKey, JSON.stringify(statuses));
    }

    function renderSeating(names) {
        const seatStatuses = getSeatStatuses();
        seating.innerHTML = "";
        names.forEach((name, index) => {
            let isTraveler = false;
            if (name.includes("[T]")) {
                isTraveler = true;
                name = name.replace("[T]", "").trim();
            }


            const seat = document.createElement("li");
            const seatButton = document.createElement("button");
            const ghostVoteButton = document.createElement("button");
            const status = seatStatuses[index] || { dead: false, ghostVote: false };
            const hasGhostVote = status.ghostVote;
            const isDead = status.dead;

            seat.className = isTraveler
                ? "player-seat player-seat-traveler"
                : "player-seat";
            seat.style.setProperty("--seat-angle", `${(index * 360) / names.length}deg`);
            
            seatButton.type = "button";
            seatButton.className = "player-seat-button";
            seatButton.textContent = name;
            seatButton.classList.toggle("dead", isDead);
            seatButton.setAttribute("aria-pressed", String(isDead));
            seatButton.setAttribute("aria-label", `${name}: ${isDead ? "dead" : "alive"}. Toggle status`);
            seatButton.addEventListener("click", function() {
                const statuses = getSeatStatuses();
                statuses[index] = statuses[index] || { dead: false, ghostVote: false };
                statuses[index].dead = !statuses[index].dead;
                saveSeatStatuses(statuses);
                renderSeating(names);
            });

            ghostVoteButton.type = "button";
            ghostVoteButton.className = "ghost-vote-button";
            ghostVoteButton.textContent = "👻";
            ghostVoteButton.classList.toggle("active", hasGhostVote);
            ghostVoteButton.setAttribute("aria-pressed", String(hasGhostVote));
            ghostVoteButton.setAttribute("aria-label", `${name}: Ghost vote. Toggle status`);
            ghostVoteButton.addEventListener("click", function() {
                const statuses = getSeatStatuses();
                statuses[index] = statuses[index] || { dead: false, ghostVote: false };
                statuses[index].ghostVote = !statuses[index].ghostVote;
                saveSeatStatuses(statuses);
                renderSeating(names);
            });

            seat.appendChild(seatButton);
            seat.appendChild(ghostVoteButton);
            seating.appendChild(seat);
        });
    }

    seatingForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const names = playerNamesInput.value
            .split(",")
            .map(name => name.trim())
            .filter(Boolean);

        sessionStorage.setItem("playerNames", JSON.stringify(names));
        const seatStatuses = getSeatStatuses().slice(0, names.length);
        while (seatStatuses.length < names.length) {
            seatStatuses.push({ dead: false, ghostVote: true });
        }
        saveSeatStatuses(seatStatuses);
        renderSeating(names);
    });

    const savedPlayerNames = JSON.parse(sessionStorage.getItem("playerNames") || "[]");

    if (savedPlayerNames.length > 0) {
        playerNamesInput.value = savedPlayerNames.join(", ");
        renderSeating(savedPlayerNames);
    }
}

async function handleScriptFormSubmit(event) {
    event.preventDefault();

    const scriptInput = document.getElementById("scriptInput");
    const scriptContent = scriptInput.value.trim();

    if (!scriptContent) {
        return;
    }

    try {
        const response = await fetch("/build_script", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                script: scriptContent
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        localStorage.setItem(scriptStorageKey, JSON.stringify(data.script));
        return data.script;
    } catch (error) {
        console.error("Error submitting script:", error);
        return;
    }
}

function renderScript(script) {
    const scriptContainer = document.getElementById("script-container");
    if (!scriptContainer) {
        return;
    }

    const characters = Array.isArray(script.characters) ? script.characters : [];
    const categoryOrder = ["Townsfolk", "Outsiders", "Minions", "Demons"];
    const groupedCharacters = characters.reduce((groups, character) => {
        const name = typeof character === "string"
            ? character
            : character.name || character.id || "Unknown character";
        const category = typeof character === "string"
            ? "Other"
            : character.category || "Other";
        const description = typeof character === "string"
            ? "Description unavailable."
            : character.description || "Description unavailable.";

        if (!categoryOrder.includes(category)) {
            return groups;
        }

        if (!groups[category]) {
            groups[category] = [];
        }
        groups[category].push({ name, description });
        return groups;
    }, {});
    const categoryColumns = [
        ["Townsfolk"],
        ["Outsiders", "Minions", "Demons"]
    ];
    const categoryMarkup = categoryColumns
        .map(column => `
            <div class="character-column">
                ${column
                    .filter(category => groupedCharacters[category])
                    .map(category => `
                        <section class="character-category category-${category.toLowerCase()}">
                            <h3>${category}</h3>
                            <div class="character-grid">
                                ${groupedCharacters[category]
                                    .map(({ name, description }) => `
                                        <article class="character-entry">
                                            <h4>${name}</h4>
                                            <p>${description}</p>
                                        </article>
                                    `)
                                    .join("")}
                            </div>
                        </section>
                    `)
                    .join("")}
            </div>
        `)
        .join("");

    scriptContainer.innerHTML = `
        <h2>${script.name}</h2>
        <div class="character-categories">${categoryMarkup}</div>
    `;
}

async function fetchAndRenderScript() {
    try {
        const script = await handleScriptFormSubmit(new Event("submit", { cancelable: true }));
        if (script) {
            renderScript(script);
        }
    }
    catch (error) {
        console.error("Error fetching and rendering script:", error);
    }
}

const scriptForm = document.getElementById("scriptForm");
if (scriptForm) {
    scriptForm.addEventListener("submit", function(event) {
        event.preventDefault();
        fetchAndRenderScript();
    });

    const savedScript = localStorage.getItem(scriptStorageKey);
    if (savedScript) {
        try {
            renderScript(JSON.parse(savedScript));
        } catch (error) {
            localStorage.removeItem(scriptStorageKey);
            console.error("Unable to restore saved script:", error);
        }
    }
}