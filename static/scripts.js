let timerInterval;
const carlFrameDurations = [200, 150, 90];
const carlFrameOrder = [0, 1, 2, 1, 0];
const carlIdleDuration = 30000;

async function updateLogs() {
    const response = await fetch("/logs");
    const data = await response.json();

    const logsElement = document.getElementById("logs-container");

    logsElement.innerHTML = "";

    data.logs.forEach(log => {
        const logElement = document.createElement("div");
        logElement.textContent = log;
        logsElement.appendChild(logElement);
    });
}

function addSubmitHandler(formId, handler) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener("submit", handler);
    }
}

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

    startTimer(Date.now() + durationSeconds * 1000);
}

function startTimer(endTime) {
    clearInterval(timerInterval);
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
        }
    }

    updateTimerDisplay();
    timerInterval = setInterval(updateTimerDisplay, 250);
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

    function renderSeating(names) {
        seating.innerHTML = "";
        names.forEach((name, index) => {
            const seat = document.createElement("li");
            const seatName = document.createElement("span");

            seat.className = "player-seat";
            seat.style.setProperty("--seat-angle", `${(index * 360) / names.length}deg`);
            seatName.textContent = name;
            seat.appendChild(seatName);
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
        renderSeating(names);
    });

    const savedPlayerNames = JSON.parse(sessionStorage.getItem("playerNames") || "[]");

    if (savedPlayerNames.length > 0) {
        playerNamesInput.value = savedPlayerNames.join(", ");
        renderSeating(savedPlayerNames);
    }
}
