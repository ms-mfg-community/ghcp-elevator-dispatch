type Passenger = {
    id: string;
    direction: "up" | "down";
};

type FloorState = {
    floor: number;
    waiting_passengers: Passenger[];
};

type ElevatorState = {
    id: string;
    current_floor: number;
    direction: "up" | "down" | "idle";
    door_state: "open" | "closed";
    available_capacity: number;
    capacity: number;
    passengers: Passenger[];
    scheduled_stops: number[];
};

type Snapshot = {
    tick: number;
    paused: boolean;
    queued_requests: number;
    status_message: string;
    floors: FloorState[];
    elevators: ElevatorState[];
};

const buildingView = document.querySelector<HTMLDivElement>("#building-view");
const dashboard = document.querySelector<HTMLDivElement>("#elevator-dashboard");
const statusMessage = document.querySelector<HTMLParagraphElement>("#status-message");
const tickValue = document.querySelector<HTMLElement>("#tick-value");
const queuedValue = document.querySelector<HTMLElement>("#queued-value");
const form = document.querySelector<HTMLFormElement>("#passenger-form");
const originSelect = document.querySelector<HTMLSelectElement>("#origin-floor");
const destinationSelect = document.querySelector<HTMLSelectElement>("#destination-floor");
const pauseToggle = document.querySelector<HTMLButtonElement>("#pause-toggle");

function populateFloorOptions(): void {
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

function renderBuilding(snapshot: Snapshot): void {
    if (!buildingView) {
        return;
    }

    const shafts = snapshot.elevators.length;
    const floorCount = snapshot.floors.length;
    const floorRows = snapshot.floors
        .map((floorState) => {
            const shaftCells = snapshot.elevators.map(() => '<div class="shaft-cell"></div>').join("");
            return `
        <div class="floor-label">
          <div>Floor ${floorState.floor}</div>
          <div class="waiting-area">${renderWaitingPassengers(floorState.waiting_passengers)}</div>
        </div>
        ${shaftCells}
      `;
        })
        .join("");

    buildingView.innerHTML = floorRows;

    snapshot.elevators.forEach((elevator, index) => {
        const cab = document.createElement("div");
        const travelPercent = ((elevator.current_floor - 1) / (floorCount - 1 || 1)) * 100;
        cab.className = `elevator-cab ${elevator.door_state === "open" ? "open" : ""}`.trim();
        cab.style.bottom = `calc(${travelPercent}% - 43px)`;
        cab.style.left = `calc(${80 + index * ((100 - 80) / shafts)}% + 12px)`;
        cab.style.width = `calc((100% - 80px) / ${shafts} - 24px)`;
        cab.innerHTML = `
      <div class="cab-header">
        <strong>${elevator.id}</strong>
        <span>${elevator.direction}</span>
      </div>
      <div class="passenger-dots">${renderCabPassengers(elevator.passengers)}</div>
    `;
        buildingView.append(cab);
    });
}

function renderDashboard(snapshot: Snapshot): void {
    if (!dashboard) {
        return;
    }

    dashboard.innerHTML = snapshot.elevators
        .map(
            (elevator) => `
        <article class="dashboard-card">
          <header>
            <strong>${elevator.id}</strong>
            <span>Floor ${elevator.current_floor}</span>
          </header>
          <p>Direction: ${elevator.direction}</p>
          <p>Doors: ${elevator.door_state}</p>
          <p>Passengers: ${elevator.passengers.length}/${elevator.capacity}</p>
          <p>Stops: ${elevator.scheduled_stops.join(", ") || "none"}</p>
        </article>
      `,
        )
        .join("");
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
    }

    renderBuilding(snapshot);
    renderDashboard(snapshot);
}

async function postJson(url: string, payload: Record<string, unknown>): Promise<void> {
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

function connectWebSocket(): void {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

    socket.addEventListener("message", (event) => {
        const snapshot = JSON.parse(event.data) as Snapshot;
        renderSnapshot(snapshot);
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
            await postJson("/api/passengers", payload);
        } catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to add passenger.";
            }
        }
    });

    pauseToggle?.addEventListener("click", async () => {
        const paused = pauseToggle.textContent?.includes("Pause") ?? true;
        try {
            await postJson("/api/control", { paused });
        } catch (error) {
            if (statusMessage) {
                statusMessage.textContent = error instanceof Error ? error.message : "Failed to change simulation state.";
            }
        }
    });
}

populateFloorOptions();
bindControls();
connectWebSocket();
