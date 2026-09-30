const task = document.getElementById("task");
const standardFields = document.getElementById("standard-fields");
const learningFields = document.getElementById("learning-fields");
const inputText = document.getElementById("input-text");
const topic = document.getElementById("topic");
const level = document.getElementById("level");
const goal = document.getElementById("goal");
const submitBtn = document.getElementById("submit-btn");
const result = document.getElementById("result");
const statusEl = document.getElementById("status");
const copyBtn = document.getElementById("copy-btn");

let latestCopyText = "";

task.addEventListener("change", () => {
    const isLearn = task.value === "learn";
    standardFields.classList.toggle("hidden", isLearn);
    learningFields.classList.toggle("hidden", !isLearn);
    result.className = "result empty";
    result.textContent = "Your result will appear here.";
    copyBtn.disabled = true;
});

submitBtn.addEventListener("click", runTask);

copyBtn.addEventListener("click", async () => {
    if (!latestCopyText) return;
    try {
        await navigator.clipboard.writeText(latestCopyText);
        statusEl.textContent = "Copied";
        setTimeout(() => statusEl.textContent = "Ready", 1200);
    } catch {
        statusEl.textContent = "Copy failed";
    }
});

async function runTask() {
    const selected = task.value;
    let endpoint = "";
    let body = {};

    if (selected === "learn") {
        if (!topic.value.trim()) {
            showError("Please enter a topic.");
            return;
        }
        endpoint = "/learn/recommendations";
        body = {
            topic: topic.value.trim(),
            level: level.value,
            goal: goal.value.trim()
        };
    } else {
        const text = inputText.value.trim();
        if (!text) {
            showError("Please enter some text.");
            return;
        }
        endpoint = `/${selected}`;
        body = { text };
    }

    setLoading(true);

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed.");
        }

        renderResult(selected, data);
        statusEl.textContent = "Completed";
    } catch (error) {
        showError(error.message);
    } finally {
        setLoading(false);
    }
}

function renderResult(selected, data) {
    result.className = "result";
    result.innerHTML = "";
    latestCopyText = "";

    if (selected === "qa") {
        result.textContent = data.answer;
        latestCopyText = data.answer;
    } else if (selected === "explain") {
        result.textContent = data.explanation;
        latestCopyText = data.explanation;
    } else if (selected === "summarize") {
        result.textContent = data.summary;
        latestCopyText = data.summary;
    } else if (selected === "learn") {
        result.textContent = data.recommendations;
        latestCopyText = data.recommendations;
    } else if (selected === "quiz") {
        renderQuiz(data.questions);
        latestCopyText = data.questions.map((q, i) =>
            `${i + 1}. ${q.question}\n${q.options.map((o, j) => `${String.fromCharCode(65 + j)}. ${o}`).join("\n")}\nAnswer: ${q.correct_answer}\nExplanation: ${q.explanation}`
        ).join("\n\n");
    }

    copyBtn.disabled = !latestCopyText;
}

function renderQuiz(questions) {
    questions.forEach((q, index) => {
        const box = document.createElement("div");
        box.className = "quiz-question";

        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}. ${q.question}`;
        box.appendChild(heading);

        q.options.forEach(option => {
            const button = document.createElement("button");
            button.className = "quiz-option";
            button.textContent = option;

            button.addEventListener("click", () => {
                const buttons = box.querySelectorAll(".quiz-option");
                buttons.forEach(b => b.disabled = true);

                if (option === q.correct_answer) {
                    button.classList.add("correct");
                } else {
                    button.classList.add("wrong");
                    buttons.forEach(b => {
                        if (b.textContent === q.correct_answer) {
                            b.classList.add("correct");
                        }
                    });
                }

                const explanation = document.createElement("p");
                explanation.className = "quiz-explanation";
                explanation.textContent = `Answer: ${q.correct_answer}. ${q.explanation}`;
                box.appendChild(explanation);
            });

            box.appendChild(button);
        });

        result.appendChild(box);
    });
}

function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.textContent = isLoading ? "Generating..." : "Generate";
    statusEl.textContent = isLoading ? "Working..." : "Ready";
}

function showError(message) {
    result.className = "result";
    result.textContent = `Error: ${message}`;
    copyBtn.disabled = true;
    statusEl.textContent = "Error";
    setTimeout(() => statusEl.textContent = "Ready", 1800);
}
