let timerInterval;
let confettiAnimationFrame;
const carlFrameDurations = [200, 150, 90];
const carlFrameOrder = [0, 1, 2, 1, 0];
const carlIdleDuration = 30000;
const timerCrazyDuration = 5000;
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

    if (displayEasterEgg(durationSeconds)) {
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

function displayEasterEgg(key) {
    const easterEgg = document.getElementById("watching-message");
    const stylesheet = document.getElementById("stylesheet");
    const hatdiv = document.getElementById("timer-hats");
    switch (key) {
        case 2809:
            easterEgg.textContent = "🏳️‍🌈Happy Birthday Dean!🏳️‍🌈";
            stylesheet.href = "/static/styles.css";
            hatdiv.innerHTML = `
                <img class="timer-hat" src="/static/hats/partyhat.png" alt="">
            `;
            launchConfetti();
            const ymcaAudio = document.getElementById("ymca-audio");
            if (ymcaAudio && audioToggle) {
                ymcaAudio.currentTime = 0;
                ymcaAudio.play();
            }
            return true;
        case 67:
            easterEgg.textContent = "67";
            hatdiv.innerHTML = "";
            return true;
        case 3110:
            easterEgg.textContent = "Happy Halloween!";
            stylesheet.href = "/static/halloween.css";
            hatdiv.innerHTML = `
                <img class="timer-hat" src="/static/hats/witchhat.png" alt="">
            `;
            return true;
        case 2512:
            easterEgg.textContent = "Merry Christmas!";
            stylesheet.href = "/static/christmas.css";
            hatdiv.innerHTML = `
                <img class="timer-hat" src="/static/hats/santahat.png" alt="">
            `;
            return true;
        default:
            easterEgg.textContent = "CARL IS WATCHING";
            hatdiv.innerHTML = "";
            return false;
    }
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
    const characterCountStorageKey = "characterCounts";

    function getSeatStatuses() {
        try {
            const savedStatuses = JSON.parse(localStorage.getItem(seatStatusStorageKey) || "[]");
            return Array.isArray(savedStatuses) ? savedStatuses : [];
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
        let travelerCount = 0;
        names.forEach((rawName, index) => {
            const isTraveler = rawName.includes("[Tr]");
            const name = rawName.replace("[Tr]", "").trim();
            const seat = document.createElement("li");
            const seatButton = document.createElement("button");
            const ghostVoteButton = document.createElement("button");
            const status = seatStatuses[index];
            const hasGhostVote = status === "ghostVote" || status?.ghostVote === true;
            const isDead = status === true || status?.dead === true;

            if (isTraveler) {
                travelerCount += 1;
            }

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
                statuses[index] = { dead: !isDead, ghostVote: hasGhostVote };
                saveSeatStatuses(statuses);
                renderSeating(names);
            });

            ghostVoteButton.type = "button";
            ghostVoteButton.className = "ghost-vote-button";
            ghostVoteButton.textContent = "👻";
            ghostVoteButton.classList.toggle("active", hasGhostVote);
            ghostVoteButton.classList.toggle("dead", !hasGhostVote);
            ghostVoteButton.setAttribute("aria-pressed", String(hasGhostVote));
            ghostVoteButton.setAttribute("aria-label", `${name}: Ghost vote. Toggle status`);
            ghostVoteButton.addEventListener("click", function() {
                const statuses = getSeatStatuses();
                statuses[index] = { dead: isDead, ghostVote: !hasGhostVote };
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

        calculateAndUpdateCharacterCount(
            getPlayerCount(names),
            getTravelerCount(names)
        );
    });

    const savedPlayerNames = JSON.parse(sessionStorage.getItem("playerNames") || "[]");

    if (savedPlayerNames.length > 0) {
        playerNamesInput.value = savedPlayerNames.join(", ");
        renderSeating(savedPlayerNames);
    }

    const savedCharacterCounts = sessionStorage.getItem(characterCountStorageKey);
    if (savedCharacterCounts) {
        try {
            updateCharacterCount(JSON.parse(savedCharacterCounts), getPlayerCount(savedPlayerNames), getTravelerCount(savedPlayerNames));
        } catch {
            sessionStorage.removeItem(characterCountStorageKey);
        }
    } else if (savedPlayerNames.length > 0) {
        calculateAndUpdateCharacterCount(
            getPlayerCount(savedPlayerNames),
            getTravelerCount(savedPlayerNames)
        );
    }
}

function getPlayerCount(names) {
    return names.filter(name => !name.includes("[Tr]")).length;
}

function getTravelerCount(names) {
    return names.filter(name => name.includes("[Tr]")).length;
}

function calculateCharacterCount(playerCount, travelerCount) {
    let gameType = "invalid";
    if (playerCount > 6) {
        gameType = "standard";
    }
    else if (playerCount > 4) {
        gameType = "teensyville";
    }

    let townsfolk = 0
    let outsiders = 0
    let minions = 0
    let demons = 0
    let travelers = 0
    let needTravelers = false

    if (gameType === "standard") {
        if (playerCount > 15) {
            playerCount = 15;
            needTravelers = true;
        }
        demons = 1;
        minions = Math.floor((playerCount - 1) / 3) - 1;
        outsiders = (playerCount - 1) % 3;
        townsfolk = playerCount - outsiders - minions - demons;
        travelers = travelerCount || 0;
    }

    if (gameType === "teensyville") {
        demons = 1;
        minions = 1;
        townsfolk = 3;
        outsiders = playerCount == 5 ? 0 : 1;
        travelers = travelerCount || 0;
    }
    return {
        townsfolk: townsfolk,
        outsiders: outsiders,
        minions: minions,
        demons: demons,
        travelers: travelers,
        needTravelers: needTravelers
    }
}

function updateCharacterCount(characterCountDict, playerCount, travelerCount) {
    const characterCountContainer = document.querySelector(".character-count-container");
    if (!characterCountContainer) {
        return;
    }

    characterCountContainer.innerHTML = `
        <p class="player-count">Players: ${playerCount + travelerCount}</p>
        <p class="townsfolk-count">T: ${characterCountDict.townsfolk}</p>
        <p class="outsider-count">O: ${characterCountDict.outsiders}</p>
        <p class="minion-count">M: ${characterCountDict.minions}</p>
        <p class="demon-count">D: ${characterCountDict.demons}</p>
        <p class="traveler-count">Tr: ${characterCountDict.travelers}</p>
        <p class="need-travelers-message">${characterCountDict.needTravelers ? "Travelers required in order to proceed!" : ""}</p>
    `;
}

function calculateAndUpdateCharacterCount(playerCount, travelerCount) {
    const characterCountDict = calculateCharacterCount(playerCount, travelerCount);
    sessionStorage.setItem("characterCounts", JSON.stringify(characterCountDict));
    updateCharacterCount(characterCountDict, playerCount, travelerCount);
}
