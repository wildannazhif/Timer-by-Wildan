import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import pygame # Untuk memainkan audio

# Nama file musik yang akan digunakan (HARUS ada di folder yang sama)
DEFAULT_ALARM_SOUND = "musik.mp3"

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timer Otomatis Musik")
        # self.root.geometry("400x250") # Mungkin perlu sedikit lebih kecil

        # Inisialisasi Pygame Mixer
        try:
            pygame.mixer.init()
        except pygame.error as e:
            messagebox.showerror("Error Pygame", f"Tidak bisa menginisialisasi Pygame Mixer: {e}\nPastikan driver audio Anda berfungsi.")
            self.root.quit()
            return

        # Variabel state
        self.remaining_time = tk.IntVar(value=0) # dalam detik
        self.selected_duration_minutes = tk.IntVar(value=1) # default 1 menit
        self.is_running = False
        self.timer_id = None
        # Langsung set path musik, tidak perlu variabel label lagi
        self.alarm_sound_path = DEFAULT_ALARM_SOUND

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # --- UI Elements ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 2. Tampilan Waktu (Dibuat lebih awal)
        self.time_label = ttk.Label(
            main_frame,
            text="00:00",
            font=("Helvetica", 48, "bold"),
            padding="10"
        )

        # 1. Pemilihan Durasi
        duration_frame = ttk.Frame(main_frame, padding="0 0 0 10")
        duration_frame.pack(fill=tk.X)

        ttk.Label(duration_frame, text="Pilih Durasi:").pack(side=tk.LEFT, padx=5)
        minute_options = [f"{i} menit" for i in range(1, 31)]
        self.duration_combobox = ttk.Combobox(
            duration_frame,
            values=minute_options,
            state="readonly",
            width=10
        )
        self.duration_combobox.set("1 menit")
        self.duration_combobox.pack(side=tk.LEFT, padx=5)
        self.duration_combobox.bind("<<ComboboxSelected>>", self.update_selected_duration)
        self.update_selected_duration() # Panggil sekali di awal

        # Packing TIME_LABEL setelah duration_frame
        self.time_label.pack(pady=20)

        # 3. Tombol Kontrol
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self.start_timer,
            width=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = ttk.Button(
            button_frame,
            text="Reset",
            command=self.reset_timer,
            state=tk.DISABLED,
            width=10
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 4. Pemilihan Musik Alarm (DIHAPUS)
        # music_frame, select_music_button, music_label dihapus

        # --- Pemeriksaan file musik di awal ---
        self.check_music_file_exists()

        # Set initial state display
        self.update_display()

    def check_music_file_exists(self):
        """Memeriksa apakah file musik default ada dan memberi peringatan jika tidak."""
        if not os.path.isfile(self.alarm_sound_path):
            messagebox.showwarning(
                "File Musik Tidak Ditemukan",
                f"File '{self.alarm_sound_path}' tidak ditemukan di folder yang sama.\n"
                f"Timer akan berfungsi, tetapi alarm tidak akan berbunyi (hanya bell sistem).\n\n"
                f"Harap letakkan file '{self.alarm_sound_path}' di folder aplikasi."
            )

    def update_selected_duration(self, event=None):
        """Update variable selected_duration_minutes berdasarkan pilihan combobox."""
        try:
            selected_text = self.duration_combobox.get()
            minutes = int(selected_text.split()[0])
            self.selected_duration_minutes.set(minutes)
            if not self.is_running:
                self.remaining_time.set(minutes * 60)
                self.update_display()
        except (ValueError, IndexError):
            self.selected_duration_minutes.set(1)
            if not self.is_running:
                 self.remaining_time.set(60)
                 self.update_display()
        except AttributeError:
            print("Warning: Mencoba update display sebelum time_label siap.")


    def format_time(self, total_seconds):
        """Format detik menjadi string MM:SS."""
        if total_seconds < 0:
            total_seconds = 0
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update_display(self):
        """Update label waktu."""
        if hasattr(self, 'time_label') and self.time_label:
             time_str = self.format_time(self.remaining_time.get())
             self.time_label.config(text=time_str)

    # Fungsi select_music() DIHAPUS

    def start_timer(self):
        """Mulai countdown timer."""
        if self.is_running:
            return

        # Tidak perlu cek alarm_sound_path karena sudah di-set
        # Pemeriksaan keberadaan file dilakukan saat play_alarm atau di awal

        self.update_selected_duration()
        duration_seconds = self.selected_duration_minutes.get() * 60
        if duration_seconds <= 0:
             messagebox.showwarning("Durasi Tidak Valid", "Pilih durasi yang valid (1-30 menit).")
             return

        self.remaining_time.set(duration_seconds)
        print(f"Timer dimulai untuk {duration_seconds} detik.")

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        self.duration_combobox.config(state=tk.DISABLED)
        # Tidak perlu disable tombol pilih musik

        self.update_display()
        self.countdown()

    def countdown(self):
        """Loop utama countdown, dipanggil setiap detik."""
        if not self.is_running:
            return

        current_seconds = self.remaining_time.get()

        if current_seconds > 0:
            self.remaining_time.set(current_seconds - 1)
            self.update_display()
            self.timer_id = self.root.after(1000, self.countdown)
        else:
            print("Waktu habis!")
            self.play_alarm()
            messagebox.showinfo("Timer Selesai", "Waktu habis!")
            self.reset_timer(keep_selection=True)

    def play_alarm(self):
        """Memainkan suara alarm default (musik.mp3)."""
        # Path sudah di-set ke self.alarm_sound_path = "musik.mp3"
        try:
            print(f"Mencoba memainkan alarm: {self.alarm_sound_path}")
            pygame.mixer.music.load(self.alarm_sound_path)
            pygame.mixer.music.play(loops=0)
        except pygame.error as e:
            # Error bisa karena file tidak ada atau format tidak didukung
            messagebox.showerror("Error Alarm", f"Tidak bisa memainkan '{self.alarm_sound_path}': {e}\nPastikan file ada di folder yang sama dan formatnya didukung (mp3, wav, ogg).")
            print(f"Error memainkan {self.alarm_sound_path}, membunyikan bell sistem.")
            self.root.bell() # Bunyikan bell sistem sebagai fallback


    def reset_timer(self, keep_selection=False):
        """Menghentikan dan mereset timer."""
        print("Timer direset.")
        self.is_running = False

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        pygame.mixer.music.stop()

        if keep_selection:
             self.update_selected_duration()
        else:
             self.duration_combobox.set("1 menit")
             self.update_selected_duration()

        self.update_display()

        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self.duration_combobox.config(state="readonly")
        # Tidak perlu enable tombol pilih musik

# --- Main Execution ---
if __name__ == "__main__":
    # Pastikan aplikasi tahu di mana mencari file musik.mp3
    # Mengubah direktori kerja ke direktori skrip (penting jika dijalankan dari tempat lain)
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname) # Pindah ke direktori skrip

    root = tk.Tk()
    app = TimerApp(root)

    def on_closing():
        if hasattr(app, 'is_running') and app.is_running:
             if messagebox.askokcancel("Keluar", "Timer masih berjalan. Yakin ingin keluar?"):
                 if hasattr(app, 'reset_timer'): app.reset_timer()
                 if pygame.mixer.get_init(): pygame.mixer.quit()
                 root.destroy()
        else:
            if pygame.mixer.get_init(): pygame.mixer.quit()
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()