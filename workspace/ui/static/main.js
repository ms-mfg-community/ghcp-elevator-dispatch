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
    buildingView.innerHTML = `
        <div class="building-labels">${floorLabels}</div>
        <div class="shaft-grid"><div class="shaft-cells">${shaftCells}</div></div>
        <div class="floor-metadata">${floorMetadata}</div>
    `;
    const shaftGrid = buildingView.querySelector(".shaft-grid");
    if (!shaftGrid) {
        return;
    }
    snapshot.elevators.forEach((elevator, index) => {
        const shaftTrack = document.createElement("div");
        shaftTrack.className = "shaft-track";
        shaftTrack.style.gridColumn = String(index + 1);
        shaftTrack.style.gridRow = `1 / ${floorCount + 1}`;
        const cab = document.createElement("div");
        cab.className = `elevator-cab ${elevator.door_state === "open" ? "open" : ""}`.trim();
        cab.style.bottom = `calc(${elevator.current_floor - 1} * var(--floor-height) + (var(--floor-height) - var(--cab-size)) / 2)`;
        cab.innerHTML = `
      <div class="cab-header">
        <strong>${elevator.id}</strong>
        <span>${elevator.direction}</span>
      </div>
      <div class="passenger-dots">${renderCabPassengers(elevator.passengers)}</div>
    `;
        shaftTrack.append(cab);
        shaftGrid.append(shaftTrack);
    });
}
function renderMovementSummary(snapshot) {
    if (!movementSummary) {
        return;
    }
    const totalMoved = snapshot.elevators.reduce((total, elevator) => total + elevator.passengers_moved, 0);
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
    }
    renderBuilding(snapshot);
    renderMovementSummary(snapshot);
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
}
function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);
    socket.addEventListener("message", (event) => {
        const snapshot = JSON.parse(event.data);
        renderSnapshot(snapshot);
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
            await postJson("/api/passengers", payload);
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
            await postJson("/api/control", { paused });
        }
        catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to change simulation state.";
            }
        }
    });
}
populateFloorOptions();
bindControls();
connectWebSocket();
