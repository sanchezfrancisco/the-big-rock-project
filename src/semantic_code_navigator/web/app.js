async function postJson(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

function out(id, payload) {
  document.getElementById(id).textContent = JSON.stringify(payload, null, 2);
}

function value(id) {
  return document.getElementById(id).value.trim();
}

document.getElementById("indexBtn").addEventListener("click", async () => {
  try {
    const payload = {
      repo_path: value("repoPath"),
      index_path: value("indexPath"),
    };
    out("indexOut", await postJson("/index", payload));
  } catch (err) {
    out("indexOut", { error: String(err) });
  }
});

document.getElementById("askBtn").addEventListener("click", async () => {
  try {
    const payload = {
      question: value("question"),
      index_path: value("indexPath"),
      top_k: Number(value("topK") || "5"),
    };
    out("askOut", await postJson("/ask", payload));
  } catch (err) {
    out("askOut", { error: String(err) });
  }
});

document.getElementById("explainBtn").addEventListener("click", async () => {
  try {
    const payload = {
      question: value("question"),
      index_path: value("indexPath"),
      top_k: Number(value("topK") || "5"),
    };
    out("askOut", await postJson("/explain", payload));
  } catch (err) {
    out("askOut", { error: String(err) });
  }
});

document.getElementById("statusBtn").addEventListener("click", async () => {
  try {
    const qp = new URLSearchParams({ index_path: value("indexPath") });
    const res = await fetch(`/status?${qp.toString()}`);
    out("statusOut", await res.json());
  } catch (err) {
    out("statusOut", { error: String(err) });
  }
});

