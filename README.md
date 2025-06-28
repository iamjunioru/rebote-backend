# 🏐 rebote

um sistema de replay instantâneo criado para quadras esportivas como futsal, vôlei e beach tênis.  
está sendo desenvolvido com foco em acessibilidade, praticidade e integração com o estilo de vida esportivo do interior.

---

## 🚀 funcionalidades principais

- 🎥 **captura contínua de vídeo** - buffer circular de 30 segundos
- 🔘 **salvamento por botão físico** - trigger via esp32 ou raspberry pi
- 📺 **reprodução instantânea** - exibição automática na tela local
- 💾 **armazenamento automático** - organização de replays por data/hora
- 🌐 **acesso via web** - interface para gerenciar e baixar replays
- ⚙️ **configuração flexível** - ajustes de buffer, qualidade e limpeza automática

---

## 🛠️ como executar localmente (modo de teste)

### pré-requisitos
- python 3.7+ instalado
- navegador web moderno

### passo 1: preparar o ambiente

```bash
# navegar para a pasta do projeto
cd project_rebote

# instalar dependências
pip install -r requirements.txt
```

### passo 2: adicionar vídeo de teste

copie qualquer arquivo de vídeo mp4 para `static/simulated_buffer.mp4`  
este arquivo será usado para simular o buffer da câmera.

**exemplo usando curl para baixar um vídeo de teste:**
```bash
# baixar vídeo de exemplo (substitua pela url de um vídeo mp4 pequeno)
curl -o static/simulated_buffer.mp4 "https://sample-videos.com/zip/10/mp4/SampleVideo_720x480_1mb.mp4"
```

### passo 3: executar o servidor

```bash
python app.py
```

o servidor iniciará em `http://localhost:5000`

### passo 4: testar o sistema

1. **acessar o painel**: abra `http://localhost:5000` no navegador
2. **capturar replay**: clique no botão "capturar replay!"
3. **visualizar replays**: veja os replays salvos na galeria
4. **configurar sistema**: clique no ícone de engrenagem para ajustar configurações

---

## 📁 estrutura do projeto

```
project_rebote/
├── app.py              # servidor flask principal
├── config.json         # configurações do sistema
├── requirements.txt    # dependências python
├── replays/           # pasta onde ficam os replays salvos
├── static/            # arquivos estáticos
│   └── simulated_buffer.mp4  # vídeo de simulação
└── templates/         # interface web
    ├── index.html     # página principal
    ├── style.css      # estilos da aplicação
    └── main_new.js    # lógica javascript
```

---

## 🎮 modos de teste disponíveis

### 1. **modo simulação completa** (atual)
- usa vídeo mockado como buffer
- botão web simula trigger físico
- ideal para desenvolvimento e testes de interface

### 2. **modo híbrido** (futuro)
- câmera real + botão web
- câmera real + botão físico simulado

### 3. **modo produção** (objetivo final)
- câmera real + esp32/raspberry pi
- sistema completo de hardware

---

## 🔧 configurações disponíveis

as configurações ficam em `config.json` e podem ser alteradas via interface web:

```json
{
  "buffer_duration_seconds": 30,    // duração do buffer em segundos
  "max_replays_storage": 50,        // máximo de replays armazenados
  "auto_cleanup_days": 7,           // dias para limpeza automática
  "video_quality": "medium",        // qualidade do vídeo
  "enable_auto_play": true,         // reprodução automática
  "camera_source": "mock"           // fonte da câmera (mock/usb/ip)
}
```

---

## 🌐 endpoints da api

### status do sistema
- `GET /api/status` - retorna estado atual do sistema

### controle de replays
- `POST /api/trigger` - aciona salvamento de replay
- `GET /api/replays` - lista todos os replays
- `GET /api/replays/{filename}` - serve arquivo de vídeo
- `DELETE /api/replays/{filename}` - remove replay específico

### configurações
- `GET /api/config` - obtém configurações atuais
- `PUT /api/config` - atualiza configurações

### controle do sistema
- `POST /api/system/recording` - liga/desliga gravação

---

## 🎯 roadmap para implementação real

### hardware necessário
1. **câmera**: webcam usb ou câmera ip
2. **computador**: raspberry pi 4 ou mini pc
3. **botão físico**: conectado ao gpio do raspberry pi
4. **tela**: monitor hdmi ou display touch
5. **armazenamento**: cartão sd classe 10 ou ssd

### software para produção
1. **captura de vídeo**: ffmpeg com buffer circular
2. **detecção de botão**: gpio monitoring no raspberry pi
3. **streaming**: configuração de câmera ip ou v4l2
4. **otimizações**: compressão de vídeo e gestão de armazenamento

### exemplo de comando ffmpeg para buffer real:
```bash
ffmpeg -i /dev/video0 -f segment -segment_time 30 -segment_wrap 2 -reset_timestamps 1 -y buffer_%03d.mp4
```

---

## 🤝 como contribuir

1. **testar o sistema** - execute localmente e reporte bugs
2. **melhorar interface** - sugestões de ui/ux são bem-vindas
3. **otimizar código** - refatorações e melhorias de performance
4. **documentar hardware** - guias de montagem e configuração
5. **expandir funcionalidades** - novas features e integrações

---

## 💡 objetivo

levar tecnologia de replay esportivo a quadras e arenas do interior, oferecendo uma solução prática, acessível e regionalmente conectada com o cenário esportivo local.

---

## 🛠️ tecnologias utilizadas

- **backend**: python + flask
- **frontend**: html5 + css3 + javascript (vanilla)
- **vídeo**: html5 video api
- **ui**: tailwind css + lucide icons
- **futuro**: ffmpeg + raspberry pi + esp32

---

## 📱 compatibilidade

- ✅ navegadores modernos (chrome, firefox, safari, edge)
- ✅ dispositivos móveis (responsivo)
- ✅ tablets e desktops
- ✅ raspberry pi (produção)

---

**versão atual**: 1.0.0 (modo de desenvolvimento)  
**próxima versão**: 1.1.0 (integração com hardware real)

*desenvolvido com 💚.*