const form = document.getElementById("dub-form");
const submitButton = document.getElementById("submit-button");
const statusBadge = document.getElementById("status-badge");
const statusTitle = document.getElementById("status-title");
const statusMessage = document.getElementById("status-message");
const currentStep = document.getElementById("current-step");
const progressValue = document.getElementById("progress-value");
const progressBar = document.getElementById("progress-bar");
const resultEmpty = document.getElementById("result-empty");
const resultContent = document.getElementById("result-content");
const videoPreview = document.getElementById("video-preview");
const resultVideo = document.getElementById("result-video");
const resultMessage = document.getElementById("result-message");
const youtubeLink = document.getElementById("youtube-link");
const localFileLink = document.getElementById("local-file-link");
const transcriptionOutput = document.getElementById("transcription-output");
const copyTranscriptionButton = document.getElementById("copy-transcription");

let pollTimer = null;

const statusTitles = {
  idle: "Pronto para receber um video",
  queued: "Seu video entrou na fila",
  processing: "Seu video esta sendo traduzido e dublado",
  completed: "Video finalizado com sucesso",
  completed_local_only: "Video finalizado localmente",
  error: "O processamento encontrou um problema",
};

function normalizeStatus(status) {
  if (status === "completed_local_only") {
    return "completed_local_only";
  }
  return ["idle", "queued", "processing", "completed", "error"].includes(status)
    ? status
    : "idle";
}

function setBadge(status) {
  const normalized = normalizeStatus(status);
  statusBadge.className = `status-badge ${normalized}`;
  statusBadge.textContent = normalized === "completed_local_only" ? "Concluido" : (
    normalized === "idle" ? "Aguardando" :
    normalized === "queued" ? "Na fila" :
    normalized === "processing" ? "Processando" :
    normalized === "completed" ? "Concluido" :
    "Erro"
  );
  statusTitle.textContent = statusTitles[normalized];
}

function updateStatusUi(data) {
  const progress = Number.isFinite(data.progress) ? data.progress : 0;
  setBadge(data.status || "idle");
  statusMessage.textContent = data.message || "Sem detalhes no momento.";
  currentStep.textContent = data.current_step || "Aguardando proximo processamento";
  progressValue.textContent = `${progress}%`;
  progressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
}

function toggleResult(show) {
  resultEmpty.classList.toggle("hidden", show);
  resultContent.classList.toggle("hidden", !show);
}

function updateResultUi(result) {
  if (!result) {
    toggleResult(false);
    return;
  }

  toggleResult(true);
  resultMessage.textContent = result.message || "Processamento concluido.";

  if (result.youtube_url) {
    youtubeLink.href = result.youtube_url;
    youtubeLink.classList.remove("hidden");
  } else {
    youtubeLink.classList.add("hidden");
  }

  if (result.local_file_url) {
    localFileLink.href = result.local_file_url;
    localFileLink.classList.remove("hidden");
    videoPreview.classList.remove("hidden");
    if (resultVideo.getAttribute("src") !== result.local_file_url) {
      resultVideo.src = result.local_file_url;
      resultVideo.load();
    }
  } else {
    localFileLink.classList.add("hidden");
    videoPreview.classList.add("hidden");
    resultVideo.removeAttribute("src");
    resultVideo.load();
  }

  transcriptionOutput.textContent = result.transcription || "Transcricao nao disponivel.";
}

async function fetchStatus() {
  const response = await fetch("/api/status");
  if (!response.ok) {
    throw new Error("Nao foi possivel consultar o status.");
  }
  return response.json();
}

async function fetchResult() {
  const response = await fetch("/api/resultado");
  if (!response.ok) {
    throw new Error("Nao foi possivel consultar o resultado.");
  }
  return response.json();
}

async function syncUi() {
  try {
    const [statusData, resultData] = await Promise.all([fetchStatus(), fetchResult()]);
    updateStatusUi(statusData);
    updateResultUi(resultData.result);

    if (!["queued", "processing"].includes(statusData.status) && pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
      submitButton.disabled = false;
      submitButton.textContent = "Traduzir e dublar agora";
    }
  } catch (error) {
    statusMessage.textContent = error.message;
  }
}

function startPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
  }

  pollTimer = setInterval(syncUi, 2500);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    video_url: formData.get("video_url"),
    titulo: formData.get("titulo"),
    descricao: formData.get("descricao") || "",
    privacidade: formData.get("privacidade") || "public",
    tags: String(formData.get("tags") || "")
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    velocidade_fala: Number(formData.get("velocidade_fala") || 1),
    voz_tts: formData.get("voz_tts") || "nova",
  };

  submitButton.disabled = true;
  submitButton.textContent = "Enviando video...";
  toggleResult(false);

  try {
    const response = await fetch("/api/processar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || "Nao foi possivel iniciar o processamento.");
    }

    setBadge("queued");
    statusMessage.textContent = data.message || "Video enviado para processamento.";
    currentStep.textContent = "Fila de processamento";
    progressValue.textContent = "0%";
    progressBar.style.width = "0%";
    submitButton.textContent = "Processando...";

    await syncUi();
    startPolling();
  } catch (error) {
    submitButton.disabled = false;
    submitButton.textContent = "Traduzir e dublar agora";
    setBadge("error");
    statusMessage.textContent = error.message;
    statusTitle.textContent = statusTitles.error;
  }
});

copyTranscriptionButton.addEventListener("click", async () => {
  const text = transcriptionOutput.textContent.trim();
  if (!text) {
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    copyTranscriptionButton.textContent = "Copiado";
    setTimeout(() => {
      copyTranscriptionButton.textContent = "Copiar texto";
    }, 1500);
  } catch (_) {
    copyTranscriptionButton.textContent = "Falhou ao copiar";
    setTimeout(() => {
      copyTranscriptionButton.textContent = "Copiar texto";
    }, 1500);
  }
});

syncUi();
