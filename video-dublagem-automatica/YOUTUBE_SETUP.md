# GUIA DE CONFIGURAÇÃO DO YOUTUBE

## 1. Obter Credenciais OAuth2 do YouTube

### Passo 1: Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com
2. Clique em "Selecionar um projeto" → "Novo Projeto"
3. Nome: "Video Dublagem"
4. Clique em "Criar"
5. Aguarde o projeto ser criado (pode levar alguns minutos)

### Passo 2: Habilitar YouTube Data API v3

1. No menu lateral, vá para "APIs e Serviços" → "Biblioteca"
2. Procure por "YouTube Data API v3"
3. Clique no resultado
4. Clique em "Habilitar"

### Passo 3: Criar Credenciais OAuth2

1. Vá para "APIs e Serviços" → "Credenciais"
2. Clique em "Criar Credenciais" → "ID de cliente OAuth 2.0"
3. Tipo: "Aplicação para desktop"
4. Nome: "Video Dublagem"
5. Clique em "Criar"
6. Uma janela vai aparecer com seu Client ID e Client Secret
7. Clique em "Download JSON" (ícone de download)

### Passo 4: Salvar no Projeto

1. Renomeie o arquivo baixado para `client_secret.json`
2. Mova para o diretório `credentials/`:
   ```bash
   mv client_secret.json video-dublagem-automatica/credentials/
   ```

### Passo 5: Configurar Tela de Consentimento OAuth

1. Vá para "APIs e Serviços" → "Tela de Consentimento"
2. Selecione "Externo"
3. Preencha:
   - Nome do aplicativo: "Video Dublagem Automática"
   - Email de suporte: seu@email.com
   - Clique em "Salvar e continuar"

4. Na seção "Escopos", adicione:
   - `youtube.upload`
   - `youtube.readonly`
   - Clique em "Salvar e continuar"

5. Na seção "Usuários de teste", adicione sua conta do Google
6. Clique em "Salvar e continuar"

## 2. Primeira Execução (Autorização)

Ao primeiro uso, o sistema:

1. Abrirá uma janela do navegador
2. Pedirá permissão para acessar sua conta YouTube
3. Clique em "Permitir"
4. O token será salvo em `credentials/token.pickle`

⚠️ **NÃO COMPARTILHE `token.pickle` ou `client_secret.json`**

## 3. Limites e Quotas

O YouTube API tem limites diários (quotas):

- **Quota padrão**: 10.000 unidades/dia
- **Upload de vídeo**: 1.600 unidades por upload

Isso significa ~6 uploads por dia com quota padrão.

Para aumentar a quota:
1. Vá para Google Cloud Console
2. "APIs e Serviços" → "YouTube Data API v3"
3. Clique em "Gerenciar quota"
4. Solicite aumento de quota

## 4. Configuração de Canais Múltiplos

Para fazer upload em canais diferentes:

1. Crie credenciais OAuth2 no Google Cloud para cada canal
2. Mantenha múltiplos arquivos `client_secret_canal1.json`, etc.
3. Mude o caminho em `.env` conforme necessário

## 5. Troubleshooting

### Erro: "No module named google.auth"

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

### Erro: "The caller does not have permission"

- Verifique se YouTube Data API está habilitada
- Verifique se a conta Google foi adicionada aos "Usuários de teste"
- Tente remover `credentials/token.pickle` e fazer login novamente

### Erro: "Invalid client secret"

- Verifique se `client_secret.json` está no diretório correto
- Certifique-se de que é um arquivo JSON válido
- Baixe novamente do console

### Vídeo não aparece imediatamente no YouTube

- YouTube pode levar alguns minutos para processar
- Pode estar em "Processando" no estúdio do criador
- Se a privacidade for "private", não aparecerá na timeline

## 6. Boas Práticas

✅ **Recomendado:**
- Usar credenciais OAuth2 (mais seguro)
- Adicionar tags/categorias descritivas
- Usar descrição detalhada
- Fazer backup de `token.pickle`

❌ **Não fazer:**
- Compartilhar `client_secret.json`
- Fazer commit de credenciais no Git
- Usar credenciais em requisições de cliente HTTPS
- Armazenar tokens em local inseguro

## 7. Referências

- [Google Cloud Console](https://console.cloud.google.com)
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [YouTube API Quotas](https://developers.google.com/youtube/v3/docs/quota)

---

Depois de configurar tudo, você pode começar a dublar vídeos!
