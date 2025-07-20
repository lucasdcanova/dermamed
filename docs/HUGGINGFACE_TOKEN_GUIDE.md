# Como Obter seu Token do Hugging Face

## Passo a Passo com Imagens

### 1️⃣ Criar Conta no Hugging Face

1. Acesse: https://huggingface.co/join
2. Preencha o formulário:
   - Username (nome de usuário único)
   - Email
   - Password
3. Clique em "Sign Up"
4. Confirme seu email

### 2️⃣ Fazer Login

1. Acesse: https://huggingface.co/login
2. Entre com seu email e senha
3. Você será redirecionado para sua página inicial

### 3️⃣ Acessar Configurações

1. Clique no seu **avatar** no canto superior direito
2. No menu dropdown, clique em **"Settings"**
   
   ```
   🔽 Seu Nome
   ├── Your Profile
   ├── Settings        ← Clique aqui
   ├── Your Organizations
   └── Sign Out
   ```

### 4️⃣ Criar Token de Acesso

1. No menu lateral esquerdo, clique em **"Access Tokens"**
   
   ```
   Settings
   ├── Profile
   ├── Account
   ├── Access Tokens  ← Clique aqui
   ├── Billing
   └── Notifications
   ```

2. Clique no botão **"New token"** (azul)

3. Configure o token:
   - **Name**: `dermamed` (ou qualquer nome descritivo)
   - **Role**: Selecione `read` (apenas leitura)
   
   ```
   Token name: dermamed
   
   What can this token do?
   ○ Fine-grained (custom)
   ● Read                    ← Selecione esta opção
   ○ Write
   ```

4. Clique em **"Generate a token"**

### 5️⃣ Copiar o Token

⚠️ **IMPORTANTE**: O token será mostrado APENAS UMA VEZ!

1. Após gerar, você verá algo como:
   ```
   Your new token:
   hf_AbCdEfGhIjKlMnOpQrStUvWxYz123456789
   ```

2. Clique no botão **"Copy"** para copiar
3. **Guarde em local seguro** - você não poderá ver novamente!

### 6️⃣ Configurar no DermaMed

1. No terminal, navegue até o backend:
   ```bash
   cd backend
   ```

2. Crie o arquivo `.env` se não existir:
   ```bash
   cp .env.example .env
   ```

3. Edite o arquivo `.env`:
   ```bash
   nano .env  # ou use seu editor preferido
   ```

4. Localize a linha:
   ```
   HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. Substitua pelo seu token real:
   ```
   HUGGINGFACE_TOKEN=hf_AbCdEfGhIjKlMnOpQrStUvWxYz123456789
   ```

6. Salve o arquivo (Ctrl+X, Y, Enter no nano)

## 🔐 Segurança do Token

### O que FAZER:
- ✅ Guardar o token em arquivo `.env`
- ✅ Adicionar `.env` ao `.gitignore`
- ✅ Usar variáveis de ambiente
- ✅ Criar tokens diferentes para dev/prod

### O que NÃO fazer:
- ❌ Compartilhar o token publicamente
- ❌ Commitar o token no Git
- ❌ Usar o token no código diretamente
- ❌ Compartilhar screenshots com o token

## 🧪 Testar o Token

Execute o script de teste:

```bash
cd backend
python test_medgemma_api.py
```

Se tudo estiver correto, você verá:
```
✅ MedGemma API connection successful!
```

## 🔧 Troubleshooting

### Erro: "Invalid token"
- Verifique se copiou o token completo
- Certifique-se que começa com `hf_`
- Tente gerar um novo token

### Erro: "401 Unauthorized"
- Token pode estar expirado
- Verifique se está logado no Hugging Face
- Confirme que aceitou os termos do MedGemma

### Erro: "Access denied"
1. Acesse: https://huggingface.co/google/medgemma-4b-it
2. Clique em "Agree and access repository"
3. Aceite os termos
4. Tente novamente

## 📋 Checklist

- [ ] Conta criada no Hugging Face
- [ ] Email confirmado
- [ ] Token gerado com permissão `read`
- [ ] Token salvo no arquivo `.env`
- [ ] Termos do MedGemma aceitos
- [ ] Teste de conexão funcionando

## 🔄 Renovar Token

Se precisar de um novo token:

1. Vá para Settings → Access Tokens
2. Encontre o token antigo
3. Clique em "Revoke" (revogar)
4. Crie um novo token seguindo os passos acima

## 🆘 Suporte

Se tiver problemas:
1. Verifique a documentação: https://huggingface.co/docs/hub/security-tokens
2. Fórum da comunidade: https://discuss.huggingface.co/
3. Status da API: https://status.huggingface.co/