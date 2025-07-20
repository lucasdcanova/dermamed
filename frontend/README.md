# DermaMed Frontend

Interface web simples para testar o sistema de análise dermatológica DermaMed.

## 🚀 Como Executar

### 1. Certifique-se que o backend está rodando:
```bash
cd ../backend
python run_dev.py
```

### 2. Inicie o servidor frontend:
```bash
cd frontend
python server.py
```

### 3. Acesse no navegador:
```
http://localhost:3000
```

## 🔑 Credenciais de Teste

- **Usuário**: `demo_doctor`
- **Senha**: `demo123`

## 📱 Funcionalidades

### 1. Upload de Imagem
- Clique ou arraste uma imagem dermatológica
- Formatos suportados: JPG, PNG, BMP
- Tamanho máximo: 50MB

### 2. Dados Clínicos (Opcional)
- Idade do paciente
- Sexo
- Localização da lesão
- Duração dos sintomas
- Histórico clínico

### 3. Análise com IA
- Diagnóstico principal com confiança
- Diagnósticos diferenciais
- Avaliação de risco
- Critérios ABCDE
- Recomendações médicas

### 4. Modo Demonstração
- Clique em "Testar com Dados de Demonstração"
- Não requer login ou imagem

## 🎨 Interface

### Tela Principal
- Upload de imagem com drag & drop
- Formulário de dados clínicos
- Botões de ação

### Resultados
- Cards organizados com informações
- Medidores visuais de confiança
- Alertas de compliance médico
- Recomendações detalhadas

## 🔧 Tecnologias

- **HTML5** - Estrutura
- **CSS3** - Estilização responsiva
- **JavaScript** - Lógica e integração com API
- **Fetch API** - Comunicação com backend

## 📋 Estrutura de Arquivos

```
frontend/
├── index.html      # Página principal
├── styles.css      # Estilos
├── app.js          # Lógica JavaScript
├── server.py       # Servidor HTTP simples
└── README.md       # Este arquivo
```

## 🛠️ Desenvolvimento

### Modificar estilos:
Edite `styles.css` - O servidor atualiza automaticamente

### Modificar lógica:
Edite `app.js` - Recarregue a página no navegador

### API Endpoints utilizados:
- `POST /api/v1/auth/token` - Login
- `GET /api/v1/auth/me` - Verificar autenticação
- `POST /api/v1/analysis/` - Análise de imagem
- `POST /api/v1/analysis/demo` - Demonstração

## 🐛 Troubleshooting

### CORS Error
Certifique-se que o backend está configurado para aceitar requests de `http://localhost:3000`

### 401 Unauthorized
Faça login novamente - o token pode ter expirado

### Network Error
Verifique se o backend está rodando em `http://localhost:8000`

## 📱 Responsivo

A interface se adapta automaticamente para:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (<768px)