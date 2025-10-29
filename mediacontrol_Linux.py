#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎧 MediaControl — Controle global de mídia para Linux (Tkinter + playerctl + pactl)
Autor: Elias Vicini
Versão: 2.1 (2025)
"""

import subprocess
import tkinter as tk
from tkinter import ttk
import importlib.util
import shutil
import sys
import os
import argparse

# ============================================================
# === ARGUMENTOS DE EXECUÇÃO ===
# ============================================================

parser = argparse.ArgumentParser(description="Controle global de mídia")
parser.add_argument("--debug", action="store_true", help="Exibir logs detalhados")
parser.add_argument("--dark", action="store_true", help="Ativar tema escuro")
args = parser.parse_args()

DEBUG = args.debug


def log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


# ============================================================
# === VERIFICAÇÃO DE DEPENDÊNCIAS ===
# ============================================================

def check_cmd(cmd):
    """Verifica se um comando existe no PATH."""
    if shutil.which(cmd):
        return True
    print(f"[!] O comando '{cmd}' não foi encontrado no sistema.")
    print(f"→ Instale manualmente com: sudo apt install {cmd}")
    return False


def check_module(module_name):
    """Verifica se um módulo Python está disponível."""
    if importlib.util.find_spec(module_name) is None:
        print(f"[!] Módulo Python '{module_name}' ausente.")
        print(f"Tente instalar com: sudo apt install python3-{module_name}")
        return False
    return True


ok = True
ok &= check_cmd("playerctl")
ok &= check_cmd("pactl")
ok &= check_module("tkinter")

if not ok:
    print("\n[✗] Dependências ausentes. Corrija e execute novamente.\n")
    sys.exit(1)


PLAYERCTL = shutil.which("playerctl")
selected_player = None
player_list = []


# ============================================================
# === FUNÇÕES AUXILIARES ===
# ============================================================

def run_playerctl(*args, player=None):
    """Executa comandos playerctl e retorna o stdout limpo."""
    cmd = [PLAYERCTL]
    if player:
        cmd += ["-p", player]
    cmd += list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        log(f"Erro ao executar {cmd}: {e}")
        return None


def list_players():
    """Lista players ativos."""
    result = run_playerctl("-l")
    if not result:
        return []
    players = []
    for line in result.splitlines():
        line = line.strip()
        if not line or line.startswith("No players found"):
            continue
        players.append((line, get_friendly_name(line)))
    return players


def get_friendly_name(player_id):
    """Obtém um nome amigável (app + artista - título)."""
    data = run_playerctl("metadata", "--format", "{{xesam:artist}} - {{xesam:title}}", player=player_id)
    app = player_id.split(".")[0].capitalize()
    if data:
        short = data[:60] + ("..." if len(data) > 60 else "")
        return f"{app} → {short}"
    return app


def get_player_status(player):
    """Retorna o status textual do player."""
    status = run_playerctl("status", player=player)
    if status == "Playing":
        return "▶ Tocando"
    elif status == "Paused":
        return "⏸ Pausado"
    return "■ Parado"


def run_cmd(cmd):
    """Executa comando no player selecionado."""
    global selected_player
    if not selected_player:
        return None
    player = selected_player[0]
    return run_playerctl(*cmd.split(), player=player)


# ============================================================
# === CONTROLES DE MÍDIA E VOLUME ===
# ============================================================

def play_pause(): run_cmd("play-pause")
def next_track(): run_cmd("next")
def prev_track(): run_cmd("previous")
def seek_forward(): run_cmd("position 10+")
def seek_backward(): run_cmd("position 10-")

def vol_up(): set_volume("+5%")
def vol_down(): set_volume("-5%")


def set_volume(delta):
    """Ajusta volume (compatível com PulseAudio/PipeWire)."""
    subprocess.run(f"pactl set-sink-volume @DEFAULT_SINK@ {delta}", shell=True)


def get_volume():
    """Retorna volume atual."""
    try:
        r = subprocess.run("pactl get-sink-volume @DEFAULT_SINK@", shell=True,
                           capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if "Volume:" in line:
                vol = line.split("/")[1].strip()
                return vol
    except:
        pass
    return "--%"


# ============================================================
# === ATUALIZAÇÃO DE INTERFACE ===
# ============================================================

def update_info(force=False):
    global player_list, selected_player

    player_list = list_players()
    display_names = [name for _, name in player_list]
    player_combo["values"] = display_names

    if not display_names:
        player_combo.set("Nenhum player ativo")
        selected_player = None
    elif selected_player and not force:
        pass
    else:
        player_combo.current(0)
        selected_player = player_list[0] if player_list else None

    if not selected_player:
        title_var.set("Nenhum player selecionado")
        status_var.set("Selecione um player acima")
    else:
        title = run_cmd("metadata xesam:title") or "Título indisponível"
        artist = run_cmd("metadata xesam:artist") or ""
        status = get_player_status(selected_player[0])
        title_var.set(f"{title[:50]}{'...' if len(title) > 50 else ''}")
        status_var.set(f"{artist} {status}".strip())

    volume_var.set(get_volume())

    # Atualiza a cada 3s
    if root.winfo_exists():
        root.after(3000, update_info)


def on_player_select(event):
    global selected_player
    idx = player_combo.current()
    if idx >= 0 and idx < len(player_list):
        selected_player = player_list[idx]
        update_info(force=True)


# ============================================================
# === INTERFACE TKINTER ===
# ============================================================

root = tk.Tk()
root.title("🎧 Controle de Mídia")
root.geometry("400x650")
root.resizable(False, False)

# Tema claro/escuro
bg_color = "#2b2b2b" if args.dark else "#f4f4f4"
fg_color = "#f4f4f4" if args.dark else "#000000"
box_color = "#3c3c3c" if args.dark else "#ffffff"
accent = "#6aa84f" if args.dark else "#e0e0e0"

root.configure(bg=bg_color)

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff")
style.configure("TButton", font=("Segoe UI", 9), relief="flat", padding=8)

frame = tk.Frame(root, bg=bg_color, padx=20, pady=20)
frame.pack(expand=True, fill="both")

tk.Label(frame, text="🎶 Player ativo:", bg=bg_color, fg=fg_color,
         font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 3))

player_combo = ttk.Combobox(frame, state="readonly", width=50)
player_combo.pack(pady=3, fill="x")
player_combo.bind("<<ComboboxSelected>>", on_player_select)

info_frame = tk.Frame(frame, bg=box_color, bd=1, relief="solid")
info_frame.pack(fill="x", pady=12, ipady=8)

title_var = tk.StringVar(value="Carregando...")
status_var = tk.StringVar(value="")
volume_var = tk.StringVar(value="--%")

tk.Label(info_frame, textvariable=title_var, bg=box_color,
         font=("Segoe UI", 10, "bold"), wraplength=350, justify="center",
         fg=fg_color).pack(pady=(2, 6))
tk.Label(info_frame, textvariable=status_var, bg=box_color,
         font=("Segoe UI", 9), fg="#ccc" if args.dark else "#444").pack()
tk.Label(info_frame, textvariable=volume_var, bg=box_color,
         font=("Segoe UI", 9), fg="#aaa" if args.dark else "#666").pack(pady=(2, 3))

# Botões
btn_frame = tk.Frame(frame, bg=bg_color)
btn_frame.pack(pady=10, fill="x")


def make_button(text, cmd):
    b = tk.Button(
        btn_frame,
        text=text,
        command=cmd,
        bg=accent,
        activebackground="#b6d7a8" if args.dark else "#d0d0d0",
        relief="flat",
        font=("Segoe UI", 9),
        anchor="center",
        justify="center",
        pady=6
    )
    b.pack(pady=4, fill="x", expand=True)
    return b


make_button("⏯  Play / Pause", play_pause)
make_button("⏪  Retroceder 10s", seek_backward)
make_button("⏩  Avançar 10s", seek_forward)
make_button("🔉  Volume -", vol_down)
make_button("🔊  Volume +", vol_up)
make_button("⏮  Anterior", prev_track)
make_button("⏭  Próximo", next_track)

tk.Label(frame,
         text="Compatível com Spotify, Firefox, Chrome, etc.\nControle global de mídia e volume do sistema.",
         bg=bg_color, fg="#999" if args.dark else "#666",
         font=("Segoe UI", 8), justify="center").pack(pady=(15, 0))


def on_close():
    log("Encerrando aplicação...")
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
root.after(500, update_info)
root.mainloop()

