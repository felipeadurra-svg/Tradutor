# Video Dublagem Automática 🎬🎙️

Um sistema completo de dublagem automática de vídeos usando IA, desenvolvido com Python e FastAPI.

## 🌟 Características

✅ **Download Automático** - Baixa vídeos de qualquer URL usando yt-dlp  
✅ **Transcrição Inteligente** - Usa OpenAI Whisper para transcrição de áudio  
✅ **Tradução com IA** - Traduz para português brasileiro com otimização para dublagem  
✅ **Síntese de Voz** - Gera áudio natural em português com TTS  
✅ **Processamento de Vídeo** - Sincroniza áudio usando FFmpeg  
✅ **Upload YouTube** - Publica automaticamente no YouTube  
✅ **API REST** - Endpoints bem documentados com Swagger  
✅ **Processamento em Background** - Não bloqueia requisições  
✅ **Status em Tempo Real** - Acompanhe o progresso do processamento  
✅ **Modular e Escalável** - Arquitetura pronta para produção  

## 📋 Requisitos

### Sistema Operacional
- Linux, macOS ou Windows (com WSL2 recomendado)
- 8GB RAM mínimo (16GB recomendado)
- 50GB espaço livre em disco

### Software Obrigatório
- Python 3.9+
- FFmpeg e FFprobe
- yt-dlp

### Chaves de API
- **OpenAI API Key** (para Whisper, GPT, TTS)
- **YouTube OAuth2 Credentials** (para upload)

## 🚀 Instalação Rápida

### 1. Clonar/Criar Projeto
```bash
cd /home/felipe/Project
cd video-dublagem-automatica
```

### 2. Criar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate    # Windows
```

### 3. Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Instalar FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS (com Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
- Baixe de https://ffmpeg.org/download.html
- Ou use: `choco install ffmpeg`

**Verificar instalação:**
```bash
ffmpeg -version
ffprobe -version
yt-dlp --version
```

### 5. Configurar API Keys

**OpenAI:**
1. Acesse https://platform.openai.com/api-keys
2. Crie nova API key
3. Copie a chave

**YouTube OAuth2:**
1. Acesse https://console.cloud.google.com
2. Crie novo projeto
3. Ative YouTube Data API v3
4. Crie credenciais OAuth2 (Aplicação de Desktop)
5. Baixe `client_secret.json`
6. Coloque em `credentials/client_secret.json`

### 6. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
```

Edite `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
YOUTUBE_CREDENTIALS_FILE=credentials/client_secret.json
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### 7. Executar Aplicação
```bash
uvicorn app.main:app --reload
```

Acesse:
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger Docs**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

## 📖 Guia de Uso

### Endpoint Principal: POST `/api/processar`

**Request Example:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "titulo": "Video Incrível - Versão Dublada",
  "descricao": "Este vídeo foi automaticamente dublado para português",
  "privacidade": "public",
  "tags": ["dublagem", "ai", "português"],
  "velocidade_fala": 1.0,
  "voz_tts": "nova"
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Vídeo enfileirado para processamento. Acompanhe em /api/status",
  "status": "queued",
  "video_id": null,
  "youtube_url": null
}
```

### Acompanhar Status: GET `/api/status`

**Response Example:**
```json
{
  "status": "processing",
  "message": "Gerando áudio em português",
  "progress": 65,
  "current_step": "Generating TTS audio"
}
```

### Health Check: GET `/api/health`

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Informações da Aplicação: GET `/info`

```json
{
  "application": "Video Dublagem Automática",
  "version": "1.0.0",
  "features": [...]
}
```

## 🗂️ Estrutura do Projeto

```
video-dublagem-automatica/
├── app/                              # Aplicação principal
│   ├── __init__.py
│   ├── main.py                       # FastAPI app
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configurações
│   ├── routes/
│   │   ├── __init__.py
│   │   └── process.py               # Endpoints da API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── downloader.py            # Download de vídeos
│   │   ├── transcription.py         # Transcrição com Whisper
│   │   ├── translation.py           # Tradução com GPT
│   │   ├── tts.py                   # Síntese de voz
│   │   ├── video_processing.py      # Processamento de vídeo
│   │   └── youtube_uploader.py      # Upload para YouTube
│   └── utils/
│       ├── __init__.py
│       └── ffmpeg.py                # Wrapper FFmpeg
│
├── storage/                          # Armazenamento de arquivos
│   ├── input/                       # Vídeos baixados
│   ├── audio/                       # Áudios extraídos
│   └── output/                      # Vídeos finais
│
├── credentials/                      # Credenciais (não commitar)
│   └── client_secret.json           # OAuth2 do YouTube
│
├── .env                              # Variáveis de ambiente (não commitar)
├── .env.example                      # Exemplo de .env
├── requirements.txt                  # Dependências Python
├── README.md                         # Este arquivo
└── app.log                           # Log de execução
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```env
# API Keys
OPENAI_API_KEY=sk-...                          # Obrigatório
YOUTUBE_CREDENTIALS_FILE=credentials/client_secret.json

# Aplicação
DEBUG=False                                     # Modo debug
HOST=0.0.0.0                                   # Host do servidor
PORT=8000                                      # Porta
LOG_LEVEL=INFO                                 # Nível de log

# FFmpeg
FFMPEG_PATH=ffmpeg                             # Caminho FFmpeg
FFPROBE_PATH=ffprobe                           # Caminho FFprobe
```

### Modelos IA Configuráveis

Em `app/config/settings.py`:

```python
WHISPER_MODEL = "whisper-1"        # Modelo de transcrição
GPT_MODEL = "gpt-4"                # Modelo de tradução
TTS_MODEL = "tts-1-hd"            # Modelo TTS (qualidade alta)
TTS_VOICE = "nova"                # Voz: alloy, echo, fable, onyx, nova, shimmer
```

### Vozes TTS Disponíveis

- **nova** - Voz feminina natural (recomendada)
- **alloy** - Voz neutra
- **echo** - Voz profunda
- **fable** - Voz infantil
- **onyx** - Voz masculina profunda
- **shimmer** - Voz feminina brilhante

## 🐛 Troubleshooting

### "FFmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verificar
ffmpeg -version
```

### "OPENAI_API_KEY not configured"
1. Verifique arquivo `.env`
2. Copie key correto de https://platform.openai.com
3. Reinicie aplicação

### "YouTube upload failed"
1. Verifique `credentials/client_secret.json`
2. Execute fluxo OAuth2 novamente
3. Verifique quotas no Google Cloud Console

### "Audio extraction failed"
- Verifique se FFmpeg está instalado
- Teste: `ffprobe <video_path>`
- Verifique formato do vídeo

### Erro: "Chunksize exceeded"
Reduz tamanho de chunk em `youtube_uploader.py`:
```python
MediaFileUpload(video_path, chunksize=5 * 1024 * 1024)  # 5MB
```

## 📊 Monitoramento

### Logs em Tempo Real
```bash
tail -f app.log
```

### Dashboard (Future)
Logs estruturados em JSON para análise:
```bash
tail -f app.log | grep "ERROR\|WARNING"
```

## 🚨 Tratamento de Erros

Todos os serviços implementam:
- ✅ Validação de entrada
- ✅ Retry automático para falhas transitórias
- ✅ Logging detalhado
- ✅ Respostas de erro claras
- ✅ Cleanup automático de arquivos temporários

## 🔐 Segurança

⚠️ **Importante:**

1. **Nunca commite `.env` ou `credentials/`**
   ```bash
   git add .gitignore
   ```

2. **Proteja suas API keys**
   - Use variáveis de ambiente
   - Rotacione periodicamente
   - Use subnets/VPCs em produção

3. **Limite de requisições**
   - Implemente rate limiting para produção
   - Use firewalls/proxies reversos

## 📈 Performance

### Tempos Estimados (por 10 min de vídeo)

| Etapa | Duração |
|-------|---------|
| Download | 2-5 min |
| Transcrição | 3-8 min |
| Tradução | 1-3 min |
| TTS | 2-5 min |
| Video Processing | 1-2 min |
| YouTube Upload | 3-10 min |
| **Total** | **12-33 min** |

### Otimização

1. Use SSD para storage
2. Aumente RAM para processamento paralelo
3. Use GPU para FFmpeg (se disponível)
4. Cache de tradução (implementar em produção)

## 🚀 Deploy em Produção

### Docker (Recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Gunicorn + Nginx

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Systemd Service

```ini
[Unit]
Description=Video Dublagem Automática
After=network.target

[Service]
Type=notify
User=app
WorkingDirectory=/opt/app
ExecStart=/opt/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📝 Roadmap

- [ ] Sistema de fila (Redis)
- [ ] Cache de tradução
- [ ] Suporte múltiplas idiomas
- [ ] Processing paralelo
- [ ] Dashboard web
- [ ] Suporte a Stream ao vivo
- [ ] Modelo TTS customizado
- [ ] Sincronização de lábios (lip-sync)

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/feature-name`)
3. Commit mudanças (`git commit -am 'Add feature'`)
4. Push para branch (`git push origin feature/feature-name`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja LICENSE para detalhes

## 👨‍💻 Autor

Desenvolvido com ❤️ por Felipe

## 📞 Suporte

- 📧 Email: seu-email@example.com
- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions

---

**Versão:** 1.0.0  
**Última atualização:** 16 de Abril, 2024  
**Status:** ✅ Pronto para Produção
