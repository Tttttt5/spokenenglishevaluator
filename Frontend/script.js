const API_URL = "http://127.0.0.1:8000/score";

const textarea = document.getElementById("transcript");
const scoreBtn = document.getElementById("scoreBtn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const overallEl = document.getElementById("overall");
const criteriaEl = document.getElementById("criteria");
const chartCanvas = document.getElementById("scoreChart");

let scoreChart = null; // Chart.js instance

scoreBtn.addEventListener("click", async () => {
  const text = textarea.value.trim();

  if (!text) {
    statusEl.textContent = "Please paste a transcript first.";
    return;
  }

  scoreBtn.disabled = true;
  statusEl.textContent = "Scoring in progress...";
  resultsEl.classList.add("hidden");
  criteriaEl.innerHTML = "";
  overallEl.innerHTML = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();

    renderOverall(data);
    renderChart(data);
    renderCriteria(data);

    resultsEl.classList.remove("hidden");
    statusEl.textContent = "Scoring complete.";
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error contacting server. Check if backend is running.";
  } finally {
    scoreBtn.disabled = false;
  }
});

function renderOverall(data) {
  overallEl.innerHTML = `
    <div><strong>Overall score:</strong> ${data.overall_score.toFixed(1)} / 100</div>
    <div><strong>Word count:</strong> ${data.word_count}</div>
  `;
}

function renderChart(data) {
  const labels = data.criteria.map(c => c.criterion);
  const scores = data.criteria.map(c => c.score);

  if (scoreChart) {
    scoreChart.destroy();
  }

  scoreChart = new Chart(chartCanvas, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Score",
          data: scores,
          borderWidth: 1
        }
      ]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
}

function renderCriteria(data) {
  data.criteria.forEach(c => {
    const div = document.createElement("div");
    div.className = "criteria-item";

    div.innerHTML = `
      <div class="criteria-header">
        <span class="criteria-name">${c.criterion}</span>
        <span class="criteria-score">${c.score.toFixed(1)} / 100</span>
      </div>
      <div class="criteria-details">
        <span><strong>Weight:</strong> ${c.weight}</span>
        ${
          typeof c.rule_score === "number" && typeof c.semantic_score === "number"
            ? `<span style="margin-left: 12px;"><strong>Rule-based:</strong> ${c.rule_score.toFixed(
                1
              )}</span>
               <span style="margin-left: 12px;"><strong>Semantic:</strong> ${c.semantic_score.toFixed(
                 1
               )}</span>`
            : ""
        }
      </div>
      <div class="criteria-feedback">
        ${c.feedback}
      </div>
    `;

    criteriaEl.appendChild(div);
  });
}