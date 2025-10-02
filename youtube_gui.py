import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading

# Dictionnaire pour suivre les barres de progression
progress_bars = {}

def telecharger(url, dossier, mode="video"):
    try:
        # Options selon le mode
        if mode == "video":
            options = {
                'outtmpl': f'{dossier}/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'progress_hooks': [lambda d: maj_progression(d, url)]
            }
        else:  # audio
            options = {
                'outtmpl': f'{dossier}/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
                ],
                'progress_hooks': [lambda d: maj_progression(d, url)]
            }

        ajouter_historique(url, mode)
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de télécharger {url}\n{e}")

def lancer_telechargement(mode="video"):
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("Attention", "Veuillez entrer un lien YouTube")
        return

    dossier = filedialog.askdirectory()
    if not dossier:
        return

    # Lancer le téléchargement dans un thread
    threading.Thread(target=telecharger, args=(url, dossier, mode), daemon=True).start()

def ajouter_historique(url, mode):
    frame = tk.Frame(frame_history)
    frame.pack(fill="x", pady=3)

    label = tk.Label(frame, text=f"{'🎬 Vidéo' if mode=='video' else '🎵 Audio'} : {url[:50]}...", anchor="w")
    label.pack(side="top", fill="x")

    bar = ttk.Progressbar(frame, length=500, mode="determinate")
    bar.pack(side="top", pady=2)
    bar["value"] = 0

    progress_bars[url] = bar

def maj_progression(d, url):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            pourcentage = downloaded * 100 / total
            progress_bars[url]["value"] = pourcentage
    elif d['status'] == 'finished':
        progress_bars[url]["value"] = 100

# --- Interface Tkinter ---
root = tk.Tk()
root.title("YouTube Downloader Flex (progression)")
root.geometry("650x500")
root.resizable(False, False)

label = tk.Label(root, text="Lien YouTube :", font=("Arial", 12))
label.pack(pady=10)

entry_url = tk.Entry(root, width=65)
entry_url.pack(pady=5)

frame_btns = tk.Frame(root)
frame_btns.pack(pady=10)

btn_video = tk.Button(frame_btns, text="Télécharger Vidéo", command=lambda: lancer_telechargement("video"), bg="orange", fg="white", font=("Arial", 12))
btn_video.grid(row=0, column=0, padx=10)

btn_audio = tk.Button(frame_btns, text="Télécharger Audio (mp3)", command=lambda: lancer_telechargement("audio"), bg="green", fg="white", font=("Arial", 12))
btn_audio.grid(row=0, column=1, padx=10)

label_historique = tk.Label(root, text="Historique des téléchargements :", font=("Arial", 12))
label_historique.pack(pady=10)

# Zone historique avec scrollbar
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
scrollbar.pack(side="right", fill="y")

frame_history = scrollable_frame

root.mainloop()
