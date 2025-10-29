# 🎧 MediaControl v2.1 — Controle Global de Mídia para Linux

Uma aplicação leve em **Python + Tkinter**, desenvolvida para **controlar players de mídia** e o **volume do sistema** no Linux de forma simples e visual.

Compatível com **Spotify, Chrome, Firefox, Brave, VLC** e qualquer outro player que utilize o protocolo **MPRIS** via `playerctl`.

---

## 🚀 Principais Recursos

- 🎶 Listagem automática dos players ativos
- ▶️ Play / Pause / Próximo / Anterior
- ⏩ Avanço e retrocesso de 10 segundos
- 🔊 Controle global de volume (`pactl`)
- 🔄 Atualização automática da interface a cada 3 segundos
- 🌙 Tema escuro opcional (`--dark`)
- 🧩 Interface moderna e responsiva em Tkinter
- 💬 Suporte a PipeWire e PulseAudio
- 🪶 Encerramento limpo da GUI (sem erros ao fechar)
- 🧱 Código modular e otimizado para distribuição

---

## 🧰 Requisitos e Dependências

O MediaControl verifica automaticamente se as dependências estão instaladas.  
Caso falte alguma, será exibida uma mensagem de orientação no terminal.

### 🔧 Pacotes necessários

| Tipo | Pacote / Comando |
|------|------------------|
| Player backend | `playerctl` |
| Controle de volume | `pulseaudio-utils` ou `pipewire-pulse` |
| Interface gráfica | `python3-tk` |

### 💡 Instalação no Debian / Ubuntu / Mint

```bash
sudo apt update
sudo apt install playerctl pulseaudio-utils python3-tk
```

🖥️ Execução
```bash
python3 mediacontrol.py
```

Opções:

| Parâmetro | Descrição |
|------|------------------|
| --dark | Ativa o tema escuro |
| --debug| Mostra logs detalhados no terminal |



Exemplo:
```bash
python3 mediacontrol.py --dark --debug
```