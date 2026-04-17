# Project Structure & File Index

## 📁 Estrutura Completa do Projeto

```
video-dublagem-automatica/
│
├── 📄 Arquivos Raiz (Configuração & Documentação)
│   ├── requirements.txt              ← Dependências Python
│   ├── .env.example                  ← Exemplo de configuração
│   ├── .gitignore                    ← Git ignore rules
│   ├── setup.py                      ← Setup de instalação (futuro)
│   ├── docker-compose.yml            ← Docker Compose config
│   ├── Dockerfile                    ← Docker image build
│   ├── quick_start.sh                ← Script de início rápido
│   ├── run.sh                        ← Script para rodar app
│   ├── test_setup.py                 ← Validação de setup
│   ├── LICENSE                       ← MIT License
│   ├── README.md                     ← Documentação principal
│   ├── API_DOCUMENTATION.md          ← Documentação da API
│   ├── YOUTUBE_SETUP.md              ← Setup do YouTube
│   ├── INTEGRATION_EXAMPLES.md       ← Exemplos de integração
│   ├── CHECKLIST.md                  ← Checklist de preparação
│   ├── ROADMAP.md                    ← Roadmap do produto
│   ├── CONTRIBUTING.md               ← Guia de contribuição
│   └── PROJECT_INDEX.md              ← Este arquivo
│
├── 📂 app/ (Aplicação Principal)
│   ├── __init__.py
│   ├── main.py                       ← FastAPI app + entry point
│   │
│   ├── 📂 config/ (Configuração)
│   │   ├── __init__.py
│   │   └── settings.py               ← Variáveis de ambiente & config
│   │
│   ├── 📂 routes/ (Endpoints da API)
│   │   ├── __init__.py
│   │   └── process.py                ← Endpoints /api/processar, /api/status
│   │
│   ├── 📂 services/ (Lógica de Negócio)
│   │   ├── __init__.py
│   │   ├── downloader.py             ← Download de vídeos (yt-dlp)
│   │   ├── transcription.py          ← Transcrição (Whisper)
│   │   ├── translation.py            ← Tradução (GPT)
│   │   ├── tts.py                    ← Síntese de voz (TTS)
│   │   ├── video_processing.py       ← Processamento de vídeo (FFmpeg)
│   │   └── youtube_uploader.py       ← Upload para YouTube (API oficial)
│   │
│   └── 📂 utils/ (Utilitários)
│       ├── __init__.py
│       └── ffmpeg.py                 ← Wrapper FFmpeg com timeout
│
├── 📂 storage/ (Arquivos de Mídia)
│   ├── input/                        ← Vídeos baixados
│   ├── audio/                        ← Áudios extraídos e processados
│   └── output/                       ← Vídeos finais dublados
│
├── 📂 credentials/ (Credenciais - NÃO COMMITAR)
│   └── client_secret.json            ← OAuth2 do YouTube
│
├── 📂 tests/ (Testes - Futuro)
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_transcription.py
│   ├── test_translation.py
│   ├── test_tts.py
│   ├── test_video_processing.py
│   └── test_youtube_uploader.py
│
└── 📄 dev_utils.py                   ← Utilitários de desenvolvimento
```

---

## 📋 Descrição dos Arquivos

### Raiz do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `requirements.txt` | Todas as dependências Python do projeto |
| `.env.example` | Template para variáveis de ambiente |
| `.gitignore` | Arquivos ignorados pelo Git |
| `Dockerfile` | Build de imagem Docker |
| `docker-compose.yml` | Orquestração de containers |
| `quick_start.sh` | Setup rápido em um comando |
| `run.sh` | Script para rodar aplicação |
| `test_setup.py` | Valida se tudo está funcionando |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | **PRINCIPAL** - Leia primeiro! |
| `API_DOCUMENTATION.md` | Documentação completa da API |
| `YOUTUBE_SETUP.md` | Passo a passo para configurar YouTube |
| `INTEGRATION_EXAMPLES.md` | Exemplos em Python, JS, cURL |
| `CHECKLIST.md` | Validação de preparação |
| `ROADMAP.md` | Versões futuras e plano |
| `CONTRIBUTING.md` | Como contribuir |
| `LICENSE` | MIT License |

### Aplicação - main.py

```
main.py
├── FastAPI app
├── CORS middleware
├── Exception handlers
├── Startup/shutdown events
├── Endpoints raiz
└── Router inclusions
```

### Aplicação - config/settings.py

```
settings.py
├── Paths (storage, credentials)
├── API Keys (OpenAI, YouTube)
├── Modelos IA (Whisper, GPT, TTS)
├── Video settings (codec, bitrate)
└── Server settings
```

### Aplicação - routes/process.py

```
process.py
├── Models Pydantic (requests/responses)
├── Endpoint POST /api/processar
├── Endpoint GET /api/status
├── Endpoint GET /api/health
└── Background task processor
```

### Serviços

#### downloader.py
- `VideoDownloader.download_video()` - Baixa vídeo
- `VideoDownloader.get_video_info()` - Obtém informações
- `VideoDownloader.cleanup_input_file()` - Limpa arquivo

#### transcription.py
- `TranscriptionService.transcribe_audio()` - Transcreve com Whisper
- `TranscriptionService._extract_segments()` - Extrai segmentos com timing

#### translation.py
- `TranslationService.translate_text()` - Traduz com GPT
- `TranslationService.translate_segments()` - Traduz múltiplos segmentos
- `TranslationService.optimize_for_dubbing()` - Otimiza para dublagem

#### tts.py
- `TTSService.generate_audio()` - Gera áudio TTS
- `TTSService.generate_segments_audio()` - Gera áudio para segmentos
- `TTSService.batch_generate_audio()` - Batch TTS

#### video_processing.py
- `VideoProcessor.extract_audio_from_video()` - Extrai áudio
- `VideoProcessor.create_dubbed_video()` - Substitui áudio
- `VideoProcessor.merge_audio_files()` - Mescla múltiplos áudios
- `VideoProcessor.process_video_pipeline()` - Pipeline completo

#### youtube_uploader.py
- `YouTubeUploader.upload_video()` - Faz upload para YouTube
- `YouTubeUploader.get_channel_info()` - Obtém info do canal
- `YouTubeUploader.update_video_metadata()` - Atualiza metadados
- `YouTubeUploader._set_video_thumbnail()` - Define thumbnail

### Utilitários

#### ffmpeg.py
- `FFmpegHandler.extract_audio()` - Extrai áudio de vídeo
- `FFmpegHandler.replace_audio()` - Substitui áudio
- `FFmpegHandler.get_video_info()` - Obtém informações
- `FFmpegHandler.get_duration()` - Duração do vídeo
- `FFmpegHandler.mux_audio_video()` - Combina streams

### Desenvolvimento

| Arquivo | Descrição |
|---------|-----------|
| `dev_utils.py` | Utilitários de dev (cleanup, stats) |
| `INTEGRATION_EXAMPLES.md` | Exemplos em várias linguagens |

---

## 🔄 Fluxo de Processamento

```
1. POST /api/processar
   ↓
2. VideoDownloader.download_video()
   ↓
3. VideoProcessor.extract_audio_from_video()
   ↓
4. TranscriptionService.transcribe_audio()
   ↓
5. TranslationService.translate_segments()
   ↓
6. TranslationService.optimize_for_dubbing()
   ↓
7. TTSService.generate_segments_audio()
   ↓
8. VideoProcessor.process_video_pipeline()
   ↓
9. YouTubeUploader.upload_video()
   ↓
10. Retorna sucesso com URL YouTube
```

---

## 📦 Dependências por Serviço

```
downloader.py
└─ yt-dlp         (download de vídeos)
└─ subprocess     (CLI tools)

transcription.py
└─ openai         (Whisper API)

translation.py
└─ openai         (GPT API)

tts.py
└─ openai         (TTS API)

video_processing.py
├─ ffmpeg.py      (FFmpeg wrapper)
├─ subprocess     (CLI tools)
└─ moviepy        (processamento de vídeo)

youtube_uploader.py
├─ google-auth    (OAuth2)
├─ google-auth-oauthlib
├─ google-api-python-client (YouTube API)
└─ pickle          (token storage)

main.py
└─ fastapi        (framework web)
└─ uvicorn        (ASGI server)
```

---

## 🔐 Arquivos Sensíveis (NÃO COMMITAR)

```
.env                          ← Chaves de API
credentials/client_secret.json ← OAuth2
credentials/token.pickle      ← Token de autenticação
storage/                      ← Arquivos de mídia
*.mp4, *.mp3, *.wav          ← Arquivos genericamente
.vscode/settings.json        ← Configurações locais
```

---

## 🚀 Ordem de Leitura Recomendada

1. **README.md** - Visão geral
2. **CHECKLIST.md** - Validação de setup
3. **app/main.py** - Entry point
4. **app/routes/process.py** - Endpoints
5. **app/services/** - Lógica
6. **app/utils/ffmpeg.py** - Utilitários
7. **API_DOCUMENTATION.md** - API completa
8. **INTEGRATION_EXAMPLES.md** - Como integrar

---

## 💻 Comandos Úteis

```bash
# Setup
./quick_start.sh

# Validação
python test_setup.py

# Rodar app
./run.sh
# ou
uvicorn app.main:app --reload

# Testes (futuro)
pytest tests/ -v

# Lint (futuro)
pylint app/
black app/

# Limpeza
rm -rf storage/*/
# e depois
./.gitkeep em diretórios
```

---

## 🎯 Próximos Passos

1. Leia **README.md**
2. Execute **test_setup.py**
3. Configure **.env** com suas chaves
4. Configure **credentials/client_secret.json**
5. Execute **run.sh**
6. Acesse **http://localhost:8000/docs**
7. Teste o endpoint `/api/processar`

---

**Versão:** 1.0.0  
**Última atualização:** 16 de Abril, 2024
