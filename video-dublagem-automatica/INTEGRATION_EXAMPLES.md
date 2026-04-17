"""
Exemplos de integração com a API Video Dublagem Automática
"""

# ============================================================================
# INTEGRAÇÃO COM PYTHON
# ============================================================================

import requests
import time
from typing import Dict, Any

class VideoDubbingClient:
    """Cliente Python para Video Dublagem Automática"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    def process_video(
        self,
        video_url: str,
        titulo: str,
        descricao: str = "",
        privacidade: str = "public",
        tags: list = None,
        velocidade_fala: float = 1.0,
        voz_tts: str = "nova",
        wait_for_completion: bool = False,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Processar vídeo para dublagem
        
        Args:
            video_url: URL do vídeo
            titulo: Título do vídeo
            descricao: Descrição
            privacidade: public, private ou unlisted
            tags: Lista de tags
            velocidade_fala: Velocidade de fala (0.25-4.0)
            voz_tts: Voz para TTS
            wait_for_completion: Aguardar conclusão
            poll_interval: Intervalo de polling em segundos
            
        Returns:
            Resultado do processamento
        """
        
        payload = {
            "video_url": video_url,
            "titulo": titulo,
            "descricao": descricao,
            "privacidade": privacidade,
            "tags": tags or [],
            "velocidade_fala": velocidade_fala,
            "voz_tts": voz_tts
        }
        
        response = requests.post(
            f"{self.api_url}/api/processar",
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        if wait_for_completion:
            result = self._wait_for_completion(poll_interval)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do processamento"""
        response = requests.get(f"{self.api_url}/api/status")
        response.raise_for_status()
        return response.json()
    
    def _wait_for_completion(self, poll_interval: int = 5):
        """Aguardar conclusão do processamento"""
        while True:
            status = self.get_status()
            print(f"[{status['current_step']}] {status['progress']}% - {status['message']}")
            
            if status['status'] in ['completed', 'error']:
                return status
            
            time.sleep(poll_interval)


# Exemplo de uso
if __name__ == "__main__":
    client = VideoDubbingClient()
    
    # Processar vídeo
    result = client.process_video(
        video_url="https://www.youtube.com/watch?v=...",
        titulo="Meu Vídeo Dublado",
        descricao="Vídeo dublado automaticamente",
        tags=["dublagem", "ai"],
        wait_for_completion=True
    )
    
    print(f"Status: {result['success']}")
    print(f"URL YouTube: {result.get('youtube_url')}")


# ============================================================================
# INTEGRAÇÃO COM JAVASCRIPT/TYPESCRIPT (Frontend)
# ============================================================================

JAVASCRIPT_EXAMPLE = """
// Cliente TypeScript para Video Dublagem
class VideoDubbingClient {
  constructor(apiUrl = 'http://localhost:8000') {
    this.apiUrl = apiUrl;
  }

  async processVideo(options) {
    const {
      videoUrl,
      titulo,
      descricao = '',
      privacidade = 'public',
      tags = [],
      velocidadeFala = 1.0,
      vozTts = 'nova'
    } = options;

    const response = await fetch(`${this.apiUrl}/api/processar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        video_url: videoUrl,
        titulo,
        descricao,
        privacidade,
        tags,
        velocidade_fala: velocidadeFala,
        voz_tts: vozTts
      })
    });

    return await response.json();
  }

  async getStatus() {
    const response = await fetch(`${this.apiUrl}/api/status`);
    return await response.json();
  }

  async waitForCompletion(intervalMs = 5000) {
    const results = [];
    return new Promise((resolve) => {
      const interval = setInterval(async () => {
        const status = await this.getStatus();
        results.push(status);
        console.log(`[${status.current_step}] ${status.progress}% - ${status.message}`);
        
        if (['completed', 'error'].includes(status.status)) {
          clearInterval(interval);
          resolve(status);
        }
      }, intervalMs);
    });
  }
}

// Exemplo de uso em React
function DubbingForm() {
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const client = new VideoDubbingClient();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);

    try {
      const result = await client.processVideo({
        videoUrl: e.target.videoUrl.value,
        titulo: e.target.titulo.value,
        descricao: e.target.descricao.value
      });

      if (result.success) {
        const status = await client.waitForCompletion();
        setProgress(100);
        alert('Vídeo processado com sucesso!\\n' + status.message);
      }
    } catch (error) {
      alert('Erro: ' + error.message);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="url" name="videoUrl" placeholder="URL do vídeo" required />
      <input type="text" name="titulo" placeholder="Título" required />
      <textarea name="descricao" placeholder="Descrição"></textarea>
      <button disabled={processing}>
        {processing ? `Processando... ${progress}%` : 'Processar'}
      </button>
    </form>
  );
}
"""

# ============================================================================
# INTEGRAÇÃO COM CURL
# ============================================================================

CURL_EXAMPLE = """
# 1. Processar vídeo
curl -X POST http://localhost:8000/api/processar \\
  -H "Content-Type: application/json" \\
  -d '{
    "video_url": "https://www.youtube.com/watch?v=...",
    "titulo": "Meu Vídeo Dublado",
    "descricao": "Descrição aqui",
    "privacidade": "public",
    "tags": ["dublagem"],
    "velocidade_fala": 1.0,
    "voz_tts": "nova"
  }' | jq .

# 2. Acompanhar status
curl http://localhost:8000/api/status | jq .

# 3. Health check
curl http://localhost:8000/api/health | jq .

# 4. Script de polling
function wait_for_dubbing() {
  while true; do
    STATUS=$(curl -s http://localhost:8000/api/status | jq -r '.status')
    PROGRESS=$(curl -s http://localhost:8000/api/status | jq -r '.progress')
    echo "[$PROGRESS%] Status: $STATUS"
    
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "error" ]; then
      break
    fi
    
    sleep 5
  done
}

wait_for_dubbing
"""

# ============================================================================
# INTEGRAÇÃO COM DOCKER
# ============================================================================

DOCKER_COMPOSE_INTEGRATION = """
version: '3.8'

services:
  # Sua aplicação que vai chamar a API
  my-app:
    image: my-app:latest
    depends_on:
      - video-dublagem
    environment:
      - DUBBING_API_URL=http://video-dublagem:8000
    networks:
      - app-network

  # Serviço de dublagem
  video-dublagem:
    build:
      context: ./video-dublagem-automatica
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./credentials:/app/credentials:ro
      - ./storage:/app/storage
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge
"""

# ============================================================================
# INTEGRAÇÃO COM CI/CD (GitHub Actions)
# ============================================================================

GITHUB_ACTIONS_EXAMPLE = """
name: Test Video Dubbing API

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          apt-get install -y ffmpeg
      
      - name: Run setup test
        run: python test_setup.py
      
      - name: Start API server
        run: |
          uvicorn app.main:app --host 0.0.0.0 &
          sleep 5
      
      - name: Test API endpoints
        run: |
          curl http://localhost:8000/api/health
          curl http://localhost:8000/api/status
          curl http://localhost:8000/info
"""

# ============================================================================
# INTEGRAÇÃO COM WEBHOOKS (Notificação)
# ============================================================================

WEBHOOK_EXAMPLE = """
# Implementar webhook para notificação ao término

class WebhookNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def notify_completion(self, result: Dict[str, Any]):
        payload = {
            'status': 'completed',
            'video_id': result.get('video_id'),
            'youtube_url': result.get('youtube_url'),
            'timestamp': datetime.now().isoformat()
        }
        
        requests.post(self.webhook_url, json=payload)
    
    def notify_error(self, error: str):
        payload = {
            'status': 'error',
            'error_message': error,
            'timestamp': datetime.now().isoformat()
        }
        
        requests.post(self.webhook_url, json=payload)
"""

print(__doc__)
print("\nJavaScript Example:")
print(JAVASCRIPT_EXAMPLE)
print("\nCURL Example:")
print(CURL_EXAMPLE)
