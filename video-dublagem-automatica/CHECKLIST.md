# CHECKLIST DE PREPARAÇÃO - Video Dublagem Automática

## ✅ Pré-requisitos do Sistema

- [ ] Python 3.9 ou superior instalado
- [ ] pip atualizado: `pip install --upgrade pip`
- [ ] Virtual environment criado: `python -m venv venv`
- [ ] Virtual environment ativado: `source venv/bin/activate`

## ✅ Instalação de Dependências

- [ ] FFmpeg instalado: `ffmpeg -version`
- [ ] FFprobe instalado: `ffprobe -version`
- [ ] yt-dlp disponível: `yt-dlp --version`
- [ ] Python packages instalados: `pip install -r requirements.txt`

## ✅ Configuração de API Keys

### OpenAI API

- [ ] Conta criada em https://openai.com/api
- [ ] API Key gerada em https://platform.openai.com/api-keys
- [ ] Adicionada à variável `OPENAI_API_KEY` no `.env`
- [ ] Saldo/crédito disponível no OpenAI

### YouTube OAuth2

- [ ] Projeto criado em Google Cloud Console
- [ ] YouTube Data API v3 habilitada
- [ ] Credenciais OAuth2 criadas
- [ ] `client_secret.json` copiado para `credentials/`
- [ ] Tela de consentimento OAuth configurada
- [ ] Conta Google adicionada como "usuário de teste"

## ✅ Configuração de Arquivos

- [ ] `.env` criado do `.env.example`: `cp .env.example .env`
- [ ] `.env` preenchido com chaves corretas
- [ ] `credentials/client_secret.json` presente
- [ ] Diretórios de storage criados:
  - [ ] `storage/input/`
  - [ ] `storage/audio/`
  - [ ] `storage/output/`
  - [ ] `credentials/`

## ✅ Validação

- [ ] Executar teste de setup: `python test_setup.py`
- [ ] Todos os checks devem passar ✓

## ✅ Início

- [ ] Servidor iniciado: `uvicorn app.main:app --reload`
- [ ] API acessível em http://localhost:8000
- [ ] Swagger disponível em http://localhost:8000/docs
- [ ] Health check retorna status: `curl http://localhost:8000/api/health`

## ✅ Teste Inicial

- [ ] Testar endpoint `/` para confirmação
- [ ] Testar endpoint `/info` para informações
- [ ] Testar endpoint `/api/processar` com vídeo pequeno
- [ ] Acompanhar progresso em `/api/status`

## 📋 Teste Completo Passo a Passo

1. **Preparação**
   - [ ] Selecione um vídeo curto (1-5 minutos)
   - [ ] Verifique que é em inglês (default)
   - [ ] Verifique espaço em disco (mínimo 5GB)

2. **Envio do Request**
   - [ ] Execute requisição POST `/api/processar`
   - [ ] Confirme que recebeu `success: true`
   - [ ] Anote o status retornado

3. **Acompanhamento**
   - [ ] Monitore `/api/status` a cada 30 segundos
   - [ ] Anote as etapas: Download → Transcrição → Tradução → TTS → Vídeo → Upload
   - [ ] Verifique progresso em incremento gradual (0-100%)

4. **Verificação Final**
   - [ ] Vídeo apareceu no YouTube
   - [ ] Áudio está em português
   - [ ] Sincronização correta
   - [ ] Metadados (título, descrição) estão corretos

## 🆘 Troubleshooting

Se algo não funcionar:

1. **Verificar Logs**
   - [ ] Logs do stdout
   - [ ] Arquivo `app.log`
   - [ ] Mensagens de erro específicas

2. **Common Issues**
   - [ ] FFmpeg não encontrado → reinstalar FFmpeg
   - [ ] API key inválida → verificar `.env`
   - [ ] YouTube auth falho → refazer login OAuth2
   - [ ] Download falha → verificar URL do vídeo

3. **Recursos**
   - [ ] Consultar README.md
   - [ ] Consultar API_DOCUMENTATION.md
   - [ ] Consultar YOUTUBE_SETUP.md

## 📈 Otimizações (Após teste inicial)

- [ ] Ajustar velocidade de fala (`velocidade_fala`)
- [ ] Testar diferentes vozes (`voz_tts`)
- [ ] Implementar caching (futuro)
- [ ] Adicionar rate limiting
- [ ] Configurar logs estruturados

## 🚀 Próximos Passos

- [ ] Deploy em produção
- [ ] Configurar monitoramento
- [ ] Implementar CI/CD
- [ ] Adicionar webhook de notificação
- [ ] Criar dashboard front-end

---

**Data de Início:** _______________

**Completado em:** _______________

**Notas:** 
_______________________________________________
_______________________________________________
