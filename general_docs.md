# 🏐 rebote - sistema de replay instantâneo

um sistema de replay instantâneo criado para quadras esportivas como futsal, vôlei e beach tênis.  
desenvolvido com foco em acessibilidade, praticidade e integração com o estilo de vida esportivo do interior.

## 🚀 funcionalidades implementadas

- 🎥 interface de captura contínua simulada (buffer de 30 segundos)
- 🔘 salvamento por botão virtual (simula ESP32/botão físico)
- 📺 reprodução instantânea na tela local
- 💾 armazenamento automático do replay no backend
- 🌐 acesso aos replays via interface web
- 📱 interface responsiva para desktop e mobile
- 🎯 sistema de mocks para testes sem hardware

## 🛠️ tecnologias utilizadas

### frontend
- **Next.js 15.3.3** - framework React com Turbopack
- **TypeScript** - tipagem estática
- **Tailwind CSS** - estilização
- **Radix UI** - componentes acessíveis
- **Lucide React** - ícones

### backend
- **Flask** - framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - banco de dados
- **Flask-CORS** - suporte a requisições cross-origin

## 📁 estrutura do projeto

```
rebote/
├── rebote-frontend/          # aplicação frontend Next.js
│   ├── src/
│   │   ├── app/             # páginas da aplicação
│   │   ├── components/      # componentes React
│   │   ├── lib/            # utilitários e mocks
│   │   └── hooks/          # hooks customizados
│   ├── package.json
│   └── next.config.ts
│
└── rebote-backend/          # aplicação backend Flask
    ├── src/
    │   ├── models/         # modelos de dados
    │   ├── routes/         # rotas da API
    │   ├── static/         # arquivos estáticos
    │   ├── database/       # banco de dados SQLite
    │   ├── replays/        # arquivos de replay salvos
    │   └── main.py         # ponto de entrada
    ├── venv/               # ambiente virtual Python
    └── requirements.txt
```

## 🚀 como rodar o projeto

### pré-requisitos
- Node.js 20+ 
- Python 3.11+
- npm ou yarn

### 1. configurando o backend

```bash
# navegar para o diretório do backend
cd rebote-backend

# ativar o ambiente virtual
source venv/bin/activate

# instalar dependências (já instaladas no template)
pip install -r requirements.txt

# iniciar o servidor Flask
python src/main.py
```

o backend estará rodando em `http://localhost:5000`

### 2. configurando o frontend

```bash
# navegar para o diretório do frontend
cd rebote-frontend

# instalar dependências
npm install

# iniciar o servidor de desenvolvimento
npm run dev
```

o frontend estará rodando em `http://localhost:9002`

## 🧪 testando o sistema

### teste básico de funcionamento

1. **acesse** `http://localhost:9002` no navegador
2. **clique** no botão verde "SALVAR" para simular o acionamento do botão físico
3. **aguarde** o processamento (2-3 segundos)
4. **visualize** o replay gerado na tela
5. **teste** o botão "gravar novamente" para voltar à tela inicial

### teste da API backend

```bash
# verificar status do sistema
curl -X GET http://localhost:5000/api/replay/status

# simular trigger de replay
curl -X POST http://localhost:5000/api/replay/trigger

# listar replays salvos
curl -X GET http://localhost:5000/api/replay/list
```

## 🎯 sistema de mocks

### mock de vídeo
o arquivo `src/lib/mocks/video.ts` simula:
- captura de vídeo de 30 segundos
- processamento e salvamento
- geração de URLs para vídeo e poster
- integração com o backend real

### mock de hardware
- **botão físico**: simulado pelo botão "SALVAR" na interface
- **câmera**: simulada com vídeos placeholder
- **ESP32/Raspberry Pi**: simulado pelas chamadas HTTP ao backend

## 📡 endpoints da API

### `GET /api/replay/status`
retorna o status do sistema de replay

### `POST /api/replay/trigger`
simula o acionamento do botão físico e salva um replay

### `GET /api/replay/list`
lista todos os replays salvos

### `GET /api/replay/video/<id>`
retorna o arquivo de vídeo do replay

### `GET /api/replay/poster/<id>`
retorna a imagem poster do replay

### `DELETE /api/replay/<id>`
deleta um replay específico

## 🔧 configurações importantes

### next.config.ts
```typescript
// configuração para proxy das chamadas da API
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:5000/api/:path*',
    },
  ];
}
```

### CORS no backend
```python
# habilitado para permitir requisições do frontend
CORS(app)
```

## 🎮 simulando hardware real

### para simular o ESP32:
```bash
# simular acionamento do botão
curl -X POST http://localhost:5000/api/replay/trigger
```

### para simular a câmera:
- o sistema usa vídeos placeholder
- em produção, seria integrado com FFmpeg para captura real

### para simular o Raspberry Pi:
- o backend Flask simula o processamento
- em produção, executaria comandos FFmpeg reais

## 🚀 próximos passos para produção

### hardware necessário
1. **câmera USB ou IP cam** - para captura real de vídeo
2. **Raspberry Pi 4** - para processamento e orquestração
3. **ESP32** - para o botão físico wireless
4. **tela HDMI/touchscreen** - para exibição
5. **armazenamento** - SSD/pendrive para os replays

### software adicional
1. **FFmpeg** - para captura e processamento de vídeo real
2. **MQTT ou HTTP** - comunicação ESP32 ↔ Raspberry Pi
3. **player de vídeo** - omxplayer ou VLC para reprodução
4. **servidor web** - nginx para produção

### exemplo de integração FFmpeg
```bash
# captura contínua em buffer circular
ffmpeg -i /dev/video0 -f segment -segment_time 30 -segment_wrap 2 -reset_timestamps 1 replay%03d.mp4
```

## 📱 interface responsiva

o sistema foi desenvolvido com design responsivo:
- **desktop**: interface completa com todos os controles
- **mobile**: adaptada para telas menores
- **touchscreen**: otimizada para interação por toque

## 🎨 design minimalista

seguindo as especificações:
- texto em letras minúsculas
- interface limpa e focada
- cores contrastantes para boa visibilidade
- feedback visual claro para ações do usuário

## 🔍 logs e monitoramento

### logs do backend
- todas as operações são logadas no console
- erros são capturados e retornados via API
- status do sistema disponível via endpoint

### logs do frontend
- erros de rede são logados no console do navegador
- fallback automático para mocks em caso de falha

## 🛡️ tratamento de erros

### frontend
- fallback para mocks se o backend estiver indisponível
- tela de erro com opção de tentar novamente
- loading states durante processamento

### backend
- validação de dados de entrada
- tratamento de exceções com mensagens claras
- códigos de status HTTP apropriados

## 📊 banco de dados

### modelo Replay
```python
class Replay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, default=30.0)
    file_size = db.Column(db.Integer)
    status = db.Column(db.String(50), default='saved')
```

---

**desenvolvido com ❤️.**

