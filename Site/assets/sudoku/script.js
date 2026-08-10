const imageInput = document.querySelector("#imageInput");
const preview = document.querySelector("#preview");
const grid = document.querySelector("#grid");
const solutionGrid = document.querySelector("#solutionGrid");
const recognizeButton = document.querySelector("#recognizeButton");
const solveButton = document.querySelector("#solveButton");
const clearButton = document.querySelector("#clearButton");
const statusLabel = document.querySelector("#status");
const solutionStatus = document.querySelector("#solutionStatus");
const examplesList = document.querySelector("#examplesList");
const dropZone = document.querySelector(".drop-zone");
const API_BASE_URL = window.SUDOKU_API_BASE_URL || "";

let selectedExample = null;
let hasGridInput = false;

function apiUrl(path) {
    return `${API_BASE_URL}${path}`;
}

function emptyGrid() {
    return Array.from({ length: 9 }, () => Array.from({ length: 9 }, () => 0));
}

function setStatus(text) {
    statusLabel.textContent = text;
}

function setSolutionStatus(text) {
    solutionStatus.textContent = text;
}

function renderGrid(container, values, editable = true) {
    container.innerHTML = "";

    for (let row = 0; row < 9; row += 1) {
        for (let col = 0; col < 9; col += 1) {
            const input = document.createElement("input");
            input.className = "sudoku-cell";
            input.inputMode = "numeric";
            input.maxLength = 1;
            input.dataset.row = row;
            input.dataset.col = col;
            input.value = values[row][col] === 0 ? "" : String(values[row][col]);
            input.readOnly = !editable;

            if (values[row][col] !== 0) {
                input.classList.add("given");
            }

            input.addEventListener("input", () => {
                input.value = input.value.replace(/[^1-9]/g, "").slice(0, 1);
                input.classList.toggle("given", input.value !== "");
                if (container === grid) {
                    hasGridInput = readGrid(grid).some((gridRow) => gridRow.some((value) => value !== 0));
                    updateButtons();
                    if (hasGridInput) {
                        setStatus("Grid ready. Check digits, then solve.");
                    }
                }
            });

            container.appendChild(input);
        }
    }
}

function updateButtons() {
    const hasImage = Boolean(imageInput.files[0] || selectedExample);
    recognizeButton.disabled = !hasImage;
    solveButton.disabled = !hasGridInput;
}

function readGrid(container) {
    const values = emptyGrid();
    container.querySelectorAll(".sudoku-cell").forEach((input) => {
        const row = Number(input.dataset.row);
        const col = Number(input.dataset.col);
        values[row][col] = input.value ? Number(input.value) : 0;
    });
    return values;
}

async function recognizeUploadedImage() {
    const file = imageInput.files[0];
    if (!file && !selectedExample) {
        setStatus("Choose an image first");
        return;
    }

    setStatus("Recognizing...");
    recognizeButton.disabled = true;

    try {
        let response;
        if (selectedExample) {
            response = await fetch(apiUrl(`/api/recognize-example/${encodeURIComponent(selectedExample)}`), {
                method: "POST",
            });
        } else {
            const formData = new FormData();
            formData.append("file", file);
            response = await fetch(apiUrl("/api/recognize"), {
                method: "POST",
                body: formData,
            });
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Recognition failed");
        }

        renderGrid(grid, data.grid, true);
        renderGrid(solutionGrid, emptyGrid(), false);
        hasGridInput = data.grid.some((gridRow) => gridRow.some((value) => value !== 0));
        setStatus("Recognized. Check the grid.");
        setSolutionStatus("No solution yet");
        updateButtons();
    } catch (error) {
        setStatus(error.message);
    } finally {
        updateButtons();
    }
}

async function solveCurrentGrid() {
    setSolutionStatus("Solving...");
    solveButton.disabled = true;

    try {
        const response = await fetch(apiUrl("/api/solve"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ grid: readGrid(grid) }),
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Solving failed");
        }

        renderGrid(solutionGrid, data.grid, false);
        setSolutionStatus("Solved");
    } catch (error) {
        setSolutionStatus(error.message);
    } finally {
        solveButton.disabled = false;
    }
}

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    selectedExample = null;

    if (!file) {
        preview.style.display = "none";
        preview.removeAttribute("src");
        setStatus("Waiting for image");
        updateButtons();
        return;
    }

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
    setStatus("Image ready. Press Recognize.");
    updateButtons();
});

dropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");

    const file = event.dataTransfer.files[0];
    if (!file) {
        return;
    }

    const transfer = new DataTransfer();
    transfer.items.add(file);
    imageInput.files = transfer.files;
    imageInput.dispatchEvent(new Event("change"));
});

examplesList.addEventListener("click", (event) => {
    const button = event.target.closest(".example-button");
    if (!button) {
        return;
    }

    selectedExample = button.dataset.filename;
    imageInput.value = "";
    preview.src = button.dataset.src;
    preview.style.display = "block";
    examplesList.querySelectorAll(".example-button").forEach((exampleButton) => {
        exampleButton.classList.toggle("selected", exampleButton === button);
    });
    setStatus("Sample selected. Recognizing...");
    updateButtons();
    recognizeUploadedImage();
});

recognizeButton.addEventListener("click", recognizeUploadedImage);
solveButton.addEventListener("click", solveCurrentGrid);
clearButton.addEventListener("click", () => {
    selectedExample = null;
    imageInput.value = "";
    preview.style.display = "none";
    preview.removeAttribute("src");
    examplesList.querySelectorAll(".example-button").forEach((button) => {
        button.classList.remove("selected");
    });
    renderGrid(grid, emptyGrid(), true);
    renderGrid(solutionGrid, emptyGrid(), false);
    hasGridInput = false;
    setStatus("Waiting for image");
    setSolutionStatus("No solution yet");
    updateButtons();
});

renderGrid(grid, emptyGrid(), true);
renderGrid(solutionGrid, emptyGrid(), false);
updateButtons();
