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

document.getElementById("echo-form").addEventListener("submit", async function(event) {
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

document.getElementById("join-voice-form").addEventListener("submit", async function(event) {
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

document.getElementById("leave-voice-form").addEventListener("submit", async function(event) {
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

updateLogs();

setInterval(updateLogs, 1000);


