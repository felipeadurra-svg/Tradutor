"""
Documentação da API - Video Dublagem Automática

Esta documentação descreve todos os endpoints disponíveis na API.
"""

# ============================================================================
# ENDPOINTS DA API
# ============================================================================

API_ENDPOINTS = {
    "GET /": {
        "description": "Root endpoint com informações da API",
        "parameters": [],
        "response": {
            "name": "Video Dublagem Automática",
            "version": "1.0.0",
            "endpoints": {}
        }
    },

    "GET /docs": {
        "description": "Documentação interativa (Swagger UI)",
        "parameters": [],
        "note": "Acesse para experimentar os endpoints"
    },

    "GET /redoc": {
        "description": "Documentação (ReDoc)",
        "parameters": [],
        "note": "Alternativa para visualizar documentação"
    },

    "GET /info": {
        "description": "Informações detalhadas da aplicação",
        "parameters": [],
        "response": {
            "application": "Video Dublagem Automática",
            "version": "1.0.0",
            "features": [],
            "storage_info": {}
        }
    },

    "POST /api/processar": {
        "description": "Processa e dubla um vídeo",
        "parameters": {
            "video_url": {
                "type": "string",
                "required": True,
                "description": "URL do vídeo para processar"
            },
            "titulo": {
                "type": "string",
                "required": True,
                "description": "Título para o vídeo dublado no YouTube"
            },
            "descricao": {
                "type": "string",
                "required": False,
                "default": "",
                "description": "Descrição do vídeo para YouTube"
            },
            "privacidade": {
                "type": "string",
                "required": False,
                "default": "public",
                "enum": ["public", "private", "unlisted"],
                "description": "Configuração de privacidade no YouTube"
            },
            "tags": {
                "type": "array[string]",
                "required": False,
                "default": [],
                "description": "Tags/keywords para YouTube"
            },
            "velocidade_fala": {
                "type": "float",
                "required": False,
                "default": 1.0,
                "min": 0.25,
                "max": 4.0,
                "description": "Velocidade de fala (0.25 a 4.0)"
            },
            "voz_tts": {
                "type": "string",
                "required": False,
                "default": "nova",
                "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                "description": "Voz para síntese de texto"
            }
        },
        "request_body": {
            "content_type": "application/json",
            "example": {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "titulo": "Vídeo Incrível - Versão Dublada",
                "descricao": "Este vídeo foi automaticamente dublado para português",
                "privacidade": "public",
                "tags": ["dublagem", "ai", "português"],
                "velocidade_fala": 1.0,
                "voz_tts": "nova"
            }
        },
        "response": {
            "200": {
                "success": True,
                "message": "Vídeo enfileirado para processamento",
                "status": "queued"
            }
        }
    },

    "GET /api/status": {
        "description": "Obtém status atual do processamento",
        "parameters": [],
        "response": {
            "status": "processing",
            "message": "Gerando áudio em português",
            "progress": 65,
            "current_step": "Generating TTS audio"
        },
        "note": "Status values: idle, queued, processing, completed, error"
    },

    "GET /api/health": {
        "description": "Health check da aplicação",
        "parameters": [],
        "response": {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:45.123456"
        }
    }
}

# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

"""
EXEMPLO 1: Processar vídeo do YouTube

curl -X POST http://localhost:8000/api/processar \\
  -H "Content-Type: application/json" \\
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "titulo": "Rick Roll - Versão Dublada em Português",
    "descricao": "O famoso Rick Roll dublado em português!",
    "privacidade": "public",
    "tags": ["rickroll", "português", "dublagem"],
    "velocidade_fala": 1.0,
    "voz_tts": "nova"
  }'


EXEMPLO 2: Acompanhar progresso

curl http://localhost:8000/api/status

Response:
{
  "status": "processing",
  "progress": 35,
  "current_step": "Translating text",
  "message": "Traduzindo para português"
}


EXEMPLO 3: Health check

curl http://localhost:8000/api/health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}


EXEMPLO 4: Obter informações da API

curl http://localhost:8000/info
"""

# ============================================================================
# CÓDIGOS DE STATUS HTTP
# ============================================================================

HTTP_STATUS_CODES = {
    "200": "OK - Requisição bem-sucedida",
    "201": "Created - Recurso criado",
    "400": "Bad Request - Parâmetros inválidos",
    "401": "Unauthorized - Autenticação necessária",
    "403": "Forbidden - Permissão negada",
    "404": "Not Found - Recurso não encontrado",
    "422": "Unprocessable Entity - Validação de dados falhou",
    "500": "Internal Server Error - Erro no servidor",
    "503": "Service Unavailable - Serviço indisponível"
}

# ============================================================================
# MODELOS DE RESPOSTA
# ============================================================================

RESPONSE_MODELS = {
    "ProcessVideoResponse": {
        "success": "bool",
        "message": "str",
        "video_id": "str | null",
        "youtube_url": "str | null",
        "local_file_path": "str | null",
        "duration": "float | null",
        "transcription": "str | null",
        "status": "str"
    },

    "ProcessingStatusResponse": {
        "status": "str",
        "message": "str",
        "progress": "int (0-100)",
        "current_step": "str"
    }
}

# ============================================================================
# GUIAS DE INTEGRAÇÃO
# ============================================================================

"""
INTEGRAÇÃO COM PYTHON

import requests

# Processar vídeo
response = requests.post(
    'http://localhost:8000/api/processar',
    json={
        'video_url': 'https://www.youtube.com/watch?v=...',
        'titulo': 'Meu Vídeo Dublado',
        'descricao': 'Descripção aqui'
    }
)

print(response.json())

# Acompanhar progresso
import time
while True:
    status = requests.get('http://localhost:8000/api/status').json()
    print(f"Progress: {status['progress']}% - {status['current_step']}")
    if status['status'] in ['completed', 'error']:
        break
    time.sleep(5)


INTEGRAÇÃO COM JAVASCRIPT

const response = await fetch('http://localhost:8000/api/processar', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    video_url: 'https://www.youtube.com/watch?v=...',
    titulo: 'Meu Vídeo Dublado',
    descricao: 'Descricção'
  })
});

const data = await response.json();
console.log(data);

// Poll status
const pollStatus = setInterval(async () => {
  const status = await fetch('http://localhost:8000/api/status').then(r => r.json());
  console.log(`Progress: ${status.progress}%`);
  if (['completed', 'error'].includes(status.status)) {
    clearInterval(pollStatus);
  }
}, 5000);


INTEGRAÇÃO COM CURL

# Processar
curl -X POST http://localhost:8000/api/processar \\
  -H "Content-Type: application/json" \\
  -d @video_request.json

# Status
curl http://localhost:8000/api/status

# Pretty print
curl http://localhost:8000/api/status | jq .
"""

# ============================================================================
# TRATAMENTO DE ERROS
# ============================================================================

ERROR_RESPONSES = {
    "invalid_url": {
        "status": 400,
        "detail": "URL de vídeo inválida"
    },
    "api_key_missing": {
        "status": 500,
        "detail": "OPENAI_API_KEY não configurada"
    },
    "youtube_auth_failed": {
        "status": 500,
        "detail": "Falha na autenticação com YouTube"
    },
    "download_failed": {
        "status": 400,
        "detail": "Erro ao baixar vídeo. URL válida?"
    },
    "transcription_failed": {
        "status": 500,
        "detail": "Erro na transcrição. Arquivo de áudio válido?"
    },
    "translation_failed": {
        "status": 500,
        "detail": "Erro na tradução. API key válida?"
    },
    "tts_failed": {
        "status": 500,
        "detail": "Erro na geração de áudio TTS"
    },
    "upload_failed": {
        "status": 500,
        "detail": "Erro ao fazer upload para YouTube"
    }
}

# ============================================================================
# RATE LIMITING (Futura implementação)
# ============================================================================

"""
PLANO DE RATE LIMITING:

1. Limite total: 100 requisições por hora por IP
2. Limite de processamento: 5 vídeos simultâneos
3. Limite de tamanho: 500MB por vídeo
4. Timeout: 2 horas por vídeo

Implementar com Redis/Memcache em produção.
"""

print(__doc__)
