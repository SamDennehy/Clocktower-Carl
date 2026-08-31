async function updateLogs() {
    const response = await fetch("/logs");
    const data = await response.json();

    const logsElement = document.getElementById("logs");

    logsElement.innerHTML = "";

    data.logs.forEach(log => {
        const logElement = document.createElement("div");
        logElement.textContent = log;
        logsElement.appendChild(logElement);
    });
}

updateLogs();

setInterval(updateLogs, 1000);
