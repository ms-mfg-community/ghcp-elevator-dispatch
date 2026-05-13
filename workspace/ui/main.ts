type Passenger = {
    id: string;
    direction: "up" | "down";
};

type FloorState = {
    floor: number;
    label: string;
    waiting_passengers: Passenger[];
};

type ElevatorState = {
    id: string;
    current_floor: number;
    direction: "up" | "down" | "idle";
    door_state: "open" | "closed";
    available_capacity: number;
    capacity: number;
    passengers_moved: number;
    passengers: Passenger[];
    scheduled_stops: number[];
};

type Snapshot = {
    tick: number;
    paused: boolean;
    finished: boolean;
    queued_requests: number;
    average_passenger_wait_time_seconds: number;
    wait_time_updated_tick: number;
    status_message: string;
    floors: FloorState[];
    elevators: ElevatorState[];
};

const buildingView = document.querySelector<HTMLDivElement>("#building-view");
const movementSummary = document.querySelector<HTMLDivElement>("#movement-summary");
const statusMessage = document.querySelector<HTMLParagraphElement>("#status-message");
const tickValue = document.querySelector<HTMLElement>("#tick-value");
const queuedValue = document.querySelector<HTMLElement>("#queued-value");
const form = document.querySelector<HTMLFormElement>("#passenger-form");
const originSelect = document.querySelector<HTMLSelectElement>("#origin-floor");
const destinationSelect = document.querySelector<HTMLSelectElement>("#destination-floor");
const pauseToggle = document.querySelector<HTMLButtonElement>("#pause-toggle");
const restartToggle = document.querySelector<HTMLButtonElement>("#restart-toggle");
const supportedFloors = [-1, 1, 2, 3, 4, 5];
const displayFloors = [5, 4, 3, 2, 1, -1];

function formatFloor(floor: number): string {
    return floor === -1 ? "B1" : `Floor ${floor}`;
}

function displayFloorLabel(floorState: FloorState): string {
    return floorState.floor === -1 ? "B1" : floorState.label || formatFloor(floorState.floor);
}

function visualFloorRank(floor: number): number {
    const rank = displayFloors.indexOf(floor);
    return rank >= 0 ? rank : displayFloors.length;
}

function sortFloorsForDisplay(floors: FloorState[]): FloorState[] {
    return [...floors].sort((left, right) => visualFloorRank(left.floor) - visualFloorRank(right.floor));
}

function floorPositionExpression(floor: number, floors: FloorState[]): string {
    const floorRowIndex = floors.findIndex((floorState) => floorState.floor === floor);
    const floorBottomIndex = floorRowIndex >= 0 ? floors.length - 1 - floorRowIndex : 0;
    return `clamp(0px, calc(${floorBottomIndex} * var(--floor-height) + (var(--floor-height) - var(--cab-size)) / 2), calc(var(--floor-count) * var(--floor-height) - var(--cab-size)))`;
}

function shaftOffsetExpression(index: number): string {
    if (index === 0) {
        return "0px";
    }

    return `calc(${Array.from({ length: index }, () => "var(--shaft-width)").join(" + ")})`;
}

function populateFloorOptions(): void {
    if (!originSelect || !destinationSelect) {
        return;
    }

    [originSelect, destinationSelect].forEach((select) => {
        select.innerHTML = "";
        supportedFloors.forEach((floor) => {
            const option = document.createElement("option");
            option.value = String(floor);
            option.textContent = formatFloor(floor);
            select.append(option);
        });
    });

    destinationSelect.value = "5";
}

function renderWaitingPassengers(waitingPassengers: Passenger[]): string {
    return waitingPassengers
        .map(() => '<span class="passenger-dot waiting" aria-hidden="true"></span>')
        .join("");
}

function renderCabPassengers(passengers: Passenger[]): string {
    return passengers
        .map(() => '<span class="passenger-dot" aria-hidden="true"></span>')
        .join("");
}

function describeWaitingPassengers(waitingPassengers: Passenger[]): string {
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

function renderFloorMetadata(floorState: FloorState, elevators: ElevatorState[]): string {
    const elevatorsOnFloor = elevators.filter((elevator) => elevator.current_floor === floorState.floor);
    const basementClass = floorState.floor === -1 ? " basement-floor" : "";
    const elevatorStatus = elevatorsOnFloor.length === 0
        ? "No elevator at this floor"
        : elevatorsOnFloor
            .map((elevator) => {
                const stops = elevator.scheduled_stops.length > 0
                    ? elevator.scheduled_stops.map(formatFloor).join(", ")
                    : "none";
                return `${elevator.id}: ${elevator.direction}, doors ${elevator.door_state}, riders ${elevator.passengers.length}/${elevator.capacity}, stops ${stops}`;
            })
            .join("; ");

    return `
        <div class="floor-meta${basementClass}">
            <strong>${displayFloorLabel(floorState)}</strong>
            <span>${describeWaitingPassengers(floorState.waiting_passengers)}</span>
            <span>${elevatorStatus}</span>
        </div>
    `;
}

function renderBuilding(snapshot: Snapshot): void {
    if (!buildingView) {
        return;
    }

    const floors = sortFloorsForDisplay(snapshot.floors);
    const floorCount = floors.length;
    const elevatorIds = snapshot.elevators.map((elevator) => elevator.id).join(",");
    const floorIds = floors.map((floorState) => String(floorState.floor)).join(",");
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

    const buildingLabels = buildingView.querySelector<HTMLDivElement>(".building-labels");
    const shaftGrid = buildingView.querySelector<HTMLDivElement>(".shaft-grid");
    const shaftCellsContainer = buildingView.querySelector<HTMLDivElement>(".shaft-cells");
    const floorMetadataContainer = buildingView.querySelector<HTMLDivElement>(".floor-metadata");

    if (!buildingLabels || !shaftGrid || !shaftCellsContainer || !floorMetadataContainer) {
        return;
    }

    buildingView.style.setProperty("--floor-count", String(floorCount));
    const rowTemplate = `repeat(${floorCount}, var(--floor-height))`;
    buildingLabels.style.gridTemplateRows = rowTemplate;
    shaftGrid.style.gridTemplateRows = rowTemplate;
    shaftGrid.style.gridTemplateColumns = `repeat(${snapshot.elevators.length}, var(--shaft-width))`;
    shaftGrid.style.width = `calc(${snapshot.elevators.length} * var(--shaft-width))`;
    shaftCellsContainer.style.gridTemplateRows = rowTemplate;
    shaftCellsContainer.style.gridTemplateColumns = `repeat(${snapshot.elevators.length}, var(--shaft-width))`;

    const floorLabels = floors
        .map((floorState) => {
            const basementClass = floorState.floor === -1 ? " basement-floor" : "";
            return `
                <div class="floor-label${basementClass}">
                    <div>${displayFloorLabel(floorState)}</div>
                    <div class="waiting-area">${renderWaitingPassengers(floorState.waiting_passengers)}</div>
                </div>
            `;
        })
        .join("");
    const shaftCells = floors
        .flatMap((floorState) => {
            const basementClass = floorState.floor === -1 ? " basement-floor" : "";
            return snapshot.elevators.map(() => `<div class="shaft-cell${basementClass}"></div>`);
        })
        .join("");
    const floorMetadata = floors
        .map((floorState) => renderFloorMetadata(floorState, snapshot.elevators))
        .join("");

    buildingLabels.innerHTML = floorLabels;
    shaftCellsContainer.innerHTML = shaftCells;
    floorMetadataContainer.innerHTML = floorMetadata;

    snapshot.elevators.forEach((elevator, index) => {
        let shaftTrack = shaftGrid.querySelector<HTMLDivElement>(`[data-elevator-id="${elevator.id}"]`);
        let cab = shaftTrack?.querySelector<HTMLDivElement>(".elevator-cab");

        if (!shaftTrack || !cab) {
            shaftTrack = document.createElement("div");
            shaftTrack.className = "shaft-track";
            shaftTrack.dataset.elevatorId = elevator.id;

            cab = document.createElement("div");
            shaftTrack.append(cab);
            shaftGrid.append(shaftTrack);
        }

        shaftTrack.style.gridColumn = "";
        shaftTrack.style.gridRow = "";
        shaftTrack.style.left = shaftOffsetExpression(index);
        const cabColorClass = `cab-${elevator.id}`;
        cab.className = `elevator-cab ${cabColorClass} ${elevator.door_state === "open" ? "open" : ""}`.trim();
        cab.style.bottom = floorPositionExpression(elevator.current_floor, floors);
        cab.innerHTML = `
      <div class="cab-header">
        <strong>${elevator.id}</strong>
        <span>${elevator.direction}</span>
      </div>
      <div class="passenger-dots">${renderCabPassengers(elevator.passengers)}</div>
    `;
    });
}

function renderMovementSummary(snapshot: Snapshot): void {
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

function renderSnapshot(snapshot: Snapshot): void {
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

function renderFinishedAlert(snapshot: Snapshot): void {
    let alert = document.querySelector<HTMLDivElement>("#finished-alert");
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
        } catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to restart.";
            }
        }
    });
}

async function postJson(url: string, payload: Record<string, unknown>): Promise<Snapshot> {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({ detail: "Request failed." }));
        throw new Error(String(errorBody.detail ?? "Request failed."));
    }

    return await response.json() as Snapshot;
}

async function fetchInitialSnapshot(): Promise<void> {
    try {
        const response = await fetch("/api/state");
        if (!response.ok) {
            throw new Error("Failed to load simulation state.");
        }
        const snapshot = await response.json() as Snapshot;
        renderSnapshot(snapshot);
    } catch (error) {
        if (statusMessage) {
            statusMessage.textContent = error instanceof Error ? error.message : "Failed to load simulation state.";
        }
    }
}

function connectWebSocket(): void {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

    socket.addEventListener("message", (event) => {
        const snapshot = JSON.parse(event.data) as Snapshot;
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

function bindControls(): void {
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
        } catch (error) {
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
        } catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to change simulation state.";
            }
        }
    });

    restartToggle?.addEventListener("click", async () => {
        try {
            const snapshot = await postJson("/api/restart", {});
            renderSnapshot(snapshot);
        } catch (error) {
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
