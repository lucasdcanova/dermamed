# Guia de Acesso ao MedGemma

## Passo a Passo Completo

### 1. Criar Conta no Hugging Face
1. Acesse https://huggingface.co/join
2. Preencha o formulário de cadastro
3. Confirme seu email

### 2. Solicitar Acesso ao MedGemma
1. Faça login no Hugging Face
2. Acesse um dos modelos:
   - **Para nossa aplicação**: https://huggingface.co/google/medgemma-4b-it
   - Alternativa maior: https://huggingface.co/google/medgemma-27b-text-it
3. Clique em "Agree and access repository"
4. Aceite os termos de uso da Health AI Developer Foundation
5. O acesso é concedido **imediatamente**

### 3. Gerar Token de API
1. No Hugging Face, clique no seu avatar → Settings
2. No menu lateral, clique em "Access Tokens"
3. Clique em "New token"
4. Configure:
   - Name: `dermamed-medgemma`
   - Type: `Read`
5. Clique em "Generate a token"
6. **IMPORTANTE**: Copie o token imediatamente (começa com `hf_`)

### 4. Configurar no DermaMed

```bash
# No diretório backend
cd backend

# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env
# Substitua hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx pelo seu token real
nano .env  # ou use seu editor preferido
```

### 5. Testar o Acesso

```python
# test_medgemma_access.py
from transformers import AutoTokenizer
import os
from dotenv import load_dotenv

load_dotenv()

try:
    tokenizer = AutoTokenizer.from_pretrained(
        "google/medgemma-4b-it",
        use_auth_token=os.getenv("HUGGINGFACE_TOKEN")
    )
    print("✅ Acesso ao MedGemma confirmado!")
except Exception as e:
    print(f"❌ Erro ao acessar MedGemma: {e}")
```

## Versões Disponíveis

### MedGemma 4B (Recomendado para DermaMed)
- **Modelo**: `google/medgemma-4b-it`
- **Tipo**: Multimodal (texto + imagem)
- **RAM**: ~16GB
- **GPU**: 8GB+ VRAM
- **Ideal para**: Análise de imagens dermatológicas

### MedGemma 27B
- **Modelo**: `google/medgemma-27b-text-it`
- **Tipo**: Apenas texto
- **RAM**: ~64GB
- **GPU**: 24GB+ VRAM
- **Uso**: Casos mais complexos, apenas texto

## Requisitos de Hardware

### Desenvolvimento Local (MedGemma 4B)
- **CPU**: 8+ cores
- **RAM**: 32GB (mínimo 16GB)
- **GPU**: NVIDIA com 8GB+ VRAM
- **Armazenamento**: 50GB livres

### Produção
- **GPU**: NVIDIA A100 ou similar
- **RAM**: 64GB+
- **Considerações**: Use quantização para reduzir requisitos

## Troubleshooting

### Erro: "Access to model is restricted"
- Certifique-se de estar logado no Hugging Face
- Verifique se aceitou os termos de uso
- Confirme que o token tem permissão de leitura

### Erro: "Invalid token"
- Verifique se copiou o token completo
- O token deve começar com `hf_`
- Gere um novo token se necessário

### Download Lento
- O modelo tem ~8GB (4B) ou ~54GB (27B)
- Use conexão estável
- O modelo é baixado apenas na primeira vez

## Notas Importantes

1. **Uso Responsável**: MedGemma é para pesquisa e desenvolvimento
2. **Não para Diagnóstico**: Sempre inclua disclaimers médicos
3. **Privacidade**: Nunca envie dados de pacientes para a Hugging Face
4. **Cache Local**: O modelo é baixado e armazenado localmente

## Próximos Passos

Após configurar o acesso:

1. Execute o servidor: `python run_dev.py`
2. Teste o endpoint de demo: http://localhost:8000/api/v1/analysis/demo
3. Faça upload de uma imagem de teste
4. Verifique os logs para confirmar o carregamento do modelo