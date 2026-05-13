"use strict";
const buildingView = document.querySelector("#building-view");
const movementSummary = document.querySelector("#movement-summary");
const statusMessage = document.querySelector("#status-message");
const tickValue = document.querySelector("#tick-value");
const queuedValue = document.querySelector("#queued-value");
const form = document.querySelector("#passenger-form");
const originSelect = document.querySelector("#origin-floor");
const destinationSelect = document.querySelector("#destination-floor");
const pauseToggle = document.querySelector("#pause-toggle");
const restartToggle = document.querySelector("#restart-toggle");
function floorPositionExpression(floor, floors) {
    const lowestFloor = Math.min(...floors.map((floorState) => floorState.floor));
    const floorOffset = floor - lowestFloor;
    return `calc(${floorOffset} * var(--floor-height) + (var(--floor-height) - var(--cab-size)) / 2)`;
}
function populateFloorOptions() {
    if (!originSelect || !destinationSelect) {
        return;
    }
    [originSelect, destinationSelect].forEach((select) => {
        select.innerHTML = "";
        for (let floor = 1; floor <= 5; floor += 1) {
            const option = document.createElement("option");
            option.value = String(floor);
            option.textContent = `Floor ${floor}`;
            select.append(option);
        }
    });
    destinationSelect.value = "5";
}
function renderWaitingPassengers(waitingPassengers) {
    return waitingPassengers
        .map(() => '<span class="passenger-dot waiting" aria-hidden="true"></span>')
        .join("");
}
function renderCabPassengers(passengers) {
    return passengers
        .map(() => '<span class="passenger-dot" aria-hidden="true"></span>')
        .join("");
}
function describeWaitingPassengers(waitingPassengers) {
    if (waitingPassengers.length === 0) {
        return "No passengers waiting";
    }
    const upCount = waitingPassengers.filter((passenger) => passenger.direction === "up").length;
    const downCount = waitingPassengers.length - upCount;
    const directions = [
        upCount > 0 ? `${upCount} up` : "",
        downCount > 0 ? `${downCount} down` : "",
    ].filter(Boolean);
    return `${waitingPassengers.length} waiting (${directions.join(", ")})`;
}
function renderFloorMetadata(floorState, elevators) {
    const elevatorsOnFloor = elevators.filter((elevator) => elevator.current_floor === floorState.floor);
    const elevatorStatus = elevatorsOnFloor.length === 0
        ? "No elevator at this floor"
        : elevatorsOnFloor
            .map((elevator) => {
            const stops = elevator.scheduled_stops.length > 0 ? elevator.scheduled_stops.join(", ") : "none";
            return `${elevator.id}: ${elevator.direction}, doors ${elevator.door_state}, riders ${elevator.passengers.length}/${elevator.capacity}, stops ${stops}`;
        })
            .join("; ");
    return `
        <div class="floor-meta">
            <strong>Floor ${floorState.floor}</strong>
            <span>${describeWaitingPassengers(floorState.waiting_passengers)}</span>
            <span>${elevatorStatus}</span>
        </div>
    `;
}
function renderBuilding(snapshot) {
    if (!buildingView) {
        return;
    }
    const floorCount = snapshot.floors.length;
    const elevatorIds = snapshot.elevators.map((elevator) => elevator.id).join(",");
    const floorIds = snapshot.floors.map((floorState) => String(floorState.floor)).join(",");
    const frameKey = `${floorIds}|${elevatorIds}`;
    if (buildingView.dataset.frameKey !== frameKey) {
        buildingView.dataset.frameKey = frameKey;
        buildingView.innerHTML = `
            <div class="building-labels"></div>
            <div class="shaft-grid"><div class="shaft-cells"></div></div>
            <div class="floor-metadata"></div>
        `;
    }
    buildingView.style.minHeight = `calc(${floorCount} * var(--floor-height))`;
    const buildingLabels = buildingView.querySelector(".building-labels");
    const shaftGrid = buildingView.querySelector(".shaft-grid");
    const shaftCellsContainer = buildingView.querySelector(".shaft-cells");
    const floorMetadataContainer = buildingView.querySelector(".floor-metadata");
    if (!buildingLabels || !shaftGrid || !shaftCellsContainer || !floorMetadataContainer) {
        return;
    }
    const rowTemplate = `repeat(${floorCount}, var(--floor-height))`;
    buildingLabels.style.gridTemplateRows = rowTemplate;
    shaftGrid.style.gridTemplateRows = rowTemplate;
    shaftGrid.style.gridTemplateColumns = `repeat(${snapshot.elevators.length}, var(--shaft-width))`;
    shaftGrid.style.width = `calc(${snapshot.elevators.length} * var(--shaft-width))`;
    shaftCellsContainer.style.gridTemplateRows = rowTemplate;
    shaftCellsContainer.style.gridTemplateColumns = `repeat(${snapshot.elevators.length}, var(--shaft-width))`;
    const floorLabels = snapshot.floors
        .map((floorState) => {
        return `
                <div class="floor-label">
                    <div>Floor ${floorState.floor}</div>
                    <div class="waiting-area">${renderWaitingPassengers(floorState.waiting_passengers)}</div>
                </div>
            `;
    })
        .join("");
    const shaftCells = snapshot.floors
        .flatMap(() => snapshot.elevators.map(() => '<div class="shaft-cell"></div>'))
        .join("");
    const floorMetadata = snapshot.floors
        .map((floorState) => renderFloorMetadata(floorState, snapshot.elevators))
        .join("");
    buildingLabels.innerHTML = floorLabels;
    shaftCellsContainer.innerHTML = shaftCells;
    floorMetadataContainer.innerHTML = floorMetadata;
    snapshot.elevators.forEach((elevator, index) => {
        let shaftTrack = shaftGrid.querySelector(`[data-elevator-id="${elevator.id}"]`);
        let cab = shaftTrack?.querySelector(".elevator-cab");
        if (!shaftTrack || !cab) {
            shaftTrack = document.createElement("div");
            shaftTrack.className = "shaft-track";
            shaftTrack.dataset.elevatorId = elevator.id;
            cab = document.createElement("div");
            shaftTrack.append(cab);
            shaftGrid.append(shaftTrack);
        }
        shaftTrack.style.gridColumn = String(index + 1);
        shaftTrack.style.gridRow = `1 / ${floorCount + 1}`;
        const cabColorClass = `cab-${elevator.id}`;
        cab.className = `elevator-cab ${cabColorClass} ${elevator.door_state === "open" ? "open" : ""}`.trim();
        cab.style.bottom = floorPositionExpression(elevator.current_floor, snapshot.floors);
        cab.innerHTML = `
      <div class="cab-header">
        <strong>${elevator.id}</strong>
        <span>${elevator.direction}</span>
      </div>
      <div class="passenger-dots">${renderCabPassengers(elevator.passengers)}</div>
    `;
    });
}
function renderMovementSummary(snapshot) {
    if (!movementSummary) {
        return;
    }
    const totalMoved = snapshot.elevators.reduce((total, elevator) => total + elevator.passengers_moved, 0);
    const averageWaitTime = snapshot.average_passenger_wait_time_seconds.toFixed(1);
    const cabTotals = snapshot.elevators
        .map((elevator) => `
            <div class="movement-stat">
                <span>${elevator.id}</span>
                <strong>${elevator.passengers_moved}</strong>
            </div>
        `)
        .join("");
    movementSummary.innerHTML = `
        <div class="movement-row cab-movement-row">${cabTotals}</div>
        <div class="movement-row total-movement-row">
            <span>Total passengers moved</span>
            <strong>${totalMoved}</strong>
        </div>
        <div class="movement-row average-wait-row">
            <span>Average passenger wait time</span>
            <strong>${averageWaitTime} sec</strong>
        </div>
    `;
}
function renderSnapshot(snapshot) {
    if (tickValue) {
        tickValue.textContent = String(snapshot.tick);
    }
    if (queuedValue) {
        queuedValue.textContent = String(snapshot.queued_requests);
    }
    if (statusMessage) {
        statusMessage.textContent = snapshot.status_message;
    }
    if (pauseToggle) {
        pauseToggle.textContent = snapshot.paused ? "Resume simulation" : "Pause simulation";
        pauseToggle.disabled = snapshot.finished;
    }
    renderBuilding(snapshot);
    renderMovementSummary(snapshot);
    renderFinishedAlert(snapshot);
}
function renderFinishedAlert(snapshot) {
    let alert = document.querySelector("#finished-alert");
    if (!snapshot.finished) {
        alert?.remove();
        return;
    }
    if (alert) {
        return;
    }
    alert = document.createElement("div");
    alert.id = "finished-alert";
    alert.className = "finished-alert";
    alert.innerHTML = `
        <p>${snapshot.status_message}</p>
        <button type="button" id="restart-button">Restart simulation</button>
    `;
    const buildingPanel = document.querySelector(".building-panel");
    if (buildingPanel) {
        buildingPanel.prepend(alert);
    }
    alert.querySelector("#restart-button")?.addEventListener("click", async () => {
        try {
            const snapshot = await postJson("/api/restart", {});
            renderSnapshot(snapshot);
        }
        catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to restart.";
            }
        }
    });
}
async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({ detail: "Request failed." }));
        throw new Error(String(errorBody.detail ?? "Request failed."));
    }
    return await response.json();
}
async function fetchInitialSnapshot() {
    try {
        const response = await fetch("/api/state");
        if (!response.ok) {
            throw new Error("Failed to load simulation state.");
        }
        const snapshot = await response.json();
        renderSnapshot(snapshot);
    }
    catch (error) {
        if (statusMessage) {
            statusMessage.textContent = error instanceof Error ? error.message : "Failed to load simulation state.";
        }
    }
}
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);
    socket.addEventListener("message", (event) => {
        const snapshot = JSON.parse(event.data);
        renderSnapshot(snapshot);
    });
    socket.addEventListener("error", () => {
        if (statusMessage) {
            statusMessage.textContent = "Live updates disconnected. Retrying...";
        }
    });
    socket.addEventListener("close", () => {
        window.setTimeout(connectWebSocket, 1000);
    });
}
function bindControls() {
    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (!originSelect || !destinationSelect) {
            return;
        }
        const payload = {
            origin_floor: Number(originSelect.value),
            destination_floor: Number(destinationSelect.value),
        };
        try {
            const snapshot = await postJson("/api/passengers", payload);
            renderSnapshot(snapshot);
        }
        catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to add passenger.";
            }
        }
    });
    pauseToggle?.addEventListener("click", async () => {
        const paused = pauseToggle.textContent?.includes("Pause") ?? true;
        try {
            const snapshot = await postJson("/api/control", { paused });
            renderSnapshot(snapshot);
        }
        catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to change simulation state.";
            }
        }
    });
    restartToggle?.addEventListener("click", async () => {
        try {
            const snapshot = await postJson("/api/restart", {});
            renderSnapshot(snapshot);
        }
        catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to restart.";
            }
        }
    });
}
populateFloorOptions();
bindControls();
void fetchInitialSnapshot();
connectWebSocket();
