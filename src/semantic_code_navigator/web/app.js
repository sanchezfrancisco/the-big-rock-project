async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body}`);
  }
  return res.json();
}

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`HTTP ${res.status}: ${body}`);
  }
  return res.json();
}

const v = (id) => document.getElementById(id).value.trim();
const n = (id, fallback = 0) => Number(v(id) || String(fallback));
const out = (id, payload) => {
  document.getElementById(id).textContent = JSON.stringify(payload, null, 2);
};
let suggestItems = [];
let suggestIndex = 0;
let suggestTimer = null;

function runtimePayload() {
  return {
    embedding_backend: v("embeddingBackend"),
    hybrid_keyword_weight: n("hybridWeight", 0.35),
  };
}

async function refreshStatus() {
  const indexPath = v("indexPath");
  out("statusOut", await getJson(`/status?index_path=${encodeURIComponent(indexPath)}`));
}

document.getElementById("indexBtn").addEventListener("click", async () => {
  try {
    const payload = { repo_path: v("repoPath"), index_path: v("indexPath"), ...runtimePayload() };
    out("indexOut", await postJson("/index", payload));
    await refreshStatus();
  } catch (err) {
    out("indexOut", { error: String(err) });
  }
});

document.getElementById("askBtn").addEventListener("click", async () => {
  try {
    const payload = {
      question: v("question"),
      index_path: v("indexPath"),
      top_k: n("topK", 5),
      ...runtimePayload(),
    };
    out("askOut", await postJson("/ask", payload));
  } catch (err) {
    out("askOut", { error: String(err) });
  }
});

document.getElementById("explainBtn").addEventListener("click", async () => {
  try {
    const payload = {
      question: v("question"),
      index_path: v("indexPath"),
      top_k: n("topK", 5),
      ...runtimePayload(),
    };
    out("askOut", await postJson("/explain", payload));
  } catch (err) {
    out("askOut", { error: String(err) });
  }
});

document.getElementById("evalBtn").addEventListener("click", async () => {
  try {
    const payload = {
      dataset_path: v("datasetPath"),
      index_path: v("indexPath"),
      top_k: n("topK", 5),
      ...runtimePayload(),
    };
    out("evalOut", await postJson("/eval", payload));
  } catch (err) {
    out("evalOut", { error: String(err) });
  }
});

document.getElementById("tuneBtn").addEventListener("click", async () => {
  try {
    const weights = v("weights")
      .split(",")
      .map((x) => Number(x.trim()))
      .filter((x) => !Number.isNaN(x));
    const payload = {
      dataset_path: v("datasetPath"),
      index_path: v("indexPath"),
      top_k: n("topK", 5),
      weights,
      ...runtimePayload(),
    };
    out("evalOut", await postJson("/tune", payload));
  } catch (err) {
    out("evalOut", { error: String(err) });
  }
});

document.getElementById("cacheStatsBtn").addEventListener("click", async () => {
  try {
    const indexPath = v("indexPath");
    out("cacheOut", await getJson(`/cache/stats?index_path=${encodeURIComponent(indexPath)}`));
  } catch (err) {
    out("cacheOut", { error: String(err) });
  }
});

document.getElementById("cachePruneBtn").addEventListener("click", async () => {
  try {
    const payload = { index_path: v("indexPath"), max_entries: n("cacheMax", 2000) };
    out("cacheOut", await postJson("/cache/prune", payload));
  } catch (err) {
    out("cacheOut", { error: String(err) });
  }
});

document.getElementById("metricsBtn").addEventListener("click", async () => {
  try {
    const data = await getJson("/metrics/recent?limit=80");
    const items = data.items || [];
    const summary = {
      total_events: items.length,
      last_event: items.length ? items[items.length - 1].event : null,
    };
    out("metricsOut", { summary, items });
  } catch (err) {
    out("metricsOut", { error: String(err) });
  }
});

async function refreshSuggestions() {
  const question = document.getElementById("question").value.trim();
  const hint = document.getElementById("suggestHint");
  if (!question) {
    suggestItems = [];
    suggestIndex = 0;
    hint.textContent = "";
    return;
  }
  const qp = new URLSearchParams({
    q: question,
    index_path: v("indexPath"),
    top_k: "5",
    embedding_backend: v("embeddingBackend"),
    hybrid_keyword_weight: String(n("hybridWeight", 0.35)),
  });
  try {
    const payload = await getJson(`/suggest?${qp.toString()}`);
    suggestItems = payload.items || [];
    suggestIndex = 0;
    hint.textContent = suggestItems.length ? `Suggestion: ${suggestItems[0]} (Tab to accept)` : "";
  } catch (err) {
    hint.textContent = "";
  }
}

const questionEl = document.getElementById("question");
questionEl.addEventListener("input", () => {
  if (suggestTimer) clearTimeout(suggestTimer);
  suggestTimer = setTimeout(refreshSuggestions, 180);
});

questionEl.addEventListener("keydown", (event) => {
  if (event.key === "Tab" && suggestItems.length > 0) {
    event.preventDefault();
    questionEl.value = suggestItems[suggestIndex];
    document.getElementById("suggestHint").textContent = "";
    suggestItems = [];
    suggestIndex = 0;
  }
});

document.getElementById("statusQuickBtn").addEventListener("click", async () => {
  try {
    await refreshStatus();
  } catch (err) {
    out("statusOut", { error: String(err) });
  }
});

refreshStatus().catch((err) => out("statusOut", { error: String(err) }));
document.getElementById("metricsBtn").click();
