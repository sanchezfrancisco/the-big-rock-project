const I18N = {
  en: {
    title: "Semantic Code Navigator",
    subtitle: "Local-first retrieval engineering console",
    refresh: "Refresh",
    runtime: "Runtime",
    index_path_label: "Index Path",
    embedding_backend_label: "Embedding Backend",
    language_label: "Language",
    hybrid_weight_label: "Hybrid Weight",
    repo_path_label: "Repo Path",
    eval_dataset_label: "Eval Dataset",
    top_k_label: "Top K",
    weights_label: "Weights",
    cache_max_entries_label: "Cache Max Entries",
    index_section: "Index",
    index_repository: "Index Repository",
    ask_explain_section: "Ask & Explain",
    question_label: "Question",
    question_placeholder: "Where is retrieval scoring implemented?",
    ask_btn: "Ask",
    explain_btn: "Explain",
    eval_tune_section: "Eval & Tune",
    run_eval_btn: "Run Eval",
    run_tune_btn: "Run Tune",
    cache_section: "Cache",
    cache_stats_btn: "Cache Stats",
    cache_prune_btn: "Prune Cache",
    status_section: "Status",
    observability_section: "Observability",
    refresh_metrics_btn: "Refresh Metrics",
    suggestion_prefix: "Suggestion",
    suggestion_suffix: "(Tab to accept)",
  },
  es: {
    title: "Semantic Code Navigator",
    subtitle: "Consola local de ingenieria de recuperacion",
    refresh: "Actualizar",
    runtime: "Ejecucion",
    index_path_label: "Ruta del indice",
    embedding_backend_label: "Backend de embeddings",
    language_label: "Idioma",
    hybrid_weight_label: "Peso hibrido",
    repo_path_label: "Ruta del repositorio",
    eval_dataset_label: "Dataset de evaluacion",
    top_k_label: "Top K",
    weights_label: "Pesos",
    cache_max_entries_label: "Maximo de entradas de cache",
    index_section: "Indexacion",
    index_repository: "Indexar repositorio",
    ask_explain_section: "Pregunta y explica",
    question_label: "Pregunta",
    question_placeholder: "Donde esta implementada la logica de recuperacion?",
    ask_btn: "Preguntar",
    explain_btn: "Explicar",
    eval_tune_section: "Evaluar y ajustar",
    run_eval_btn: "Ejecutar evaluacion",
    run_tune_btn: "Ejecutar ajuste",
    cache_section: "Cache",
    cache_stats_btn: "Estadisticas cache",
    cache_prune_btn: "Podar cache",
    status_section: "Estado",
    observability_section: "Observabilidad",
    refresh_metrics_btn: "Actualizar metricas",
    suggestion_prefix: "Sugerencia",
    suggestion_suffix: "(Tab para aceptar)",
  },
};

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
    language: v("language") || "en",
  };
}

function currentLang() {
  const lang = v("language") || "en";
  return I18N[lang] ? lang : "en";
}

function t(key) {
  return I18N[currentLang()][key] || I18N.en[key] || key;
}

function applyI18n() {
  document.documentElement.lang = currentLang();
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const text = t(key);
    if (el.tagName === "LABEL") {
      const input = el.querySelector("input,select");
      if (input) {
        // Preserve controls; only replace label text node.
        el.childNodes[0].nodeValue = text;
      } else {
        el.textContent = text;
      }
    } else {
      el.textContent = text;
    }
  });
  const questionInput = document.getElementById("question");
  questionInput.placeholder = t("question_placeholder");
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
    language: v("language") || "en",
  });
  try {
    const payload = await getJson(`/suggest?${qp.toString()}`);
    suggestItems = payload.items || [];
    suggestIndex = 0;
    const isEs = (v("language") || "en") === "es";
    hint.textContent = suggestItems.length
      ? `${t("suggestion_prefix")}: ${suggestItems[0]} ${t("suggestion_suffix")}`
      : "";
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

document.getElementById("language").addEventListener("change", () => {
  applyI18n();
  refreshSuggestions().catch(() => {});
});

refreshStatus().catch((err) => out("statusOut", { error: String(err) }));
document.getElementById("metricsBtn").click();
applyI18n();
