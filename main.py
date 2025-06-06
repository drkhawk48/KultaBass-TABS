import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import sys
import tkinter.scrolledtext as st
from PIL import Image, ImageTk

# Función para resolver rutas dinámicas cuando se genera el .exe
def resource_path(relative_path):
    """ Devuelve la ruta absoluta, compatible con .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

TAB_FOLDER = "tablaturas"
ASSETS_FOLDER = resource_path("assets")

class KultaBassTabsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎸 KultaBass-TABS")
        self.root.geometry("1100x800")
        self.root.configure(bg="#1e1e2f")

        # Variables para scroll automático
        self.auto_scroll_active = False
        self.scroll_job = None
        self.current_lines = []
        self.scroll_speed = 1000  # ms por línea

        self.set_window_icon()

        self.create_widgets()
        self.load_saved_tabs()

    def set_window_icon(self):
        icon_path = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                print("[WARNING] No se pudo cargar el icono. Formato no compatible o inexistente.")

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#3c3c54")
        style.map("TButton",
                  background=[('active', '#505070')],
                  foreground=[('pressed', '#ffffff')])
        style.configure("Treeview", background="#2d2d3d", fieldbackground="#2d2d3d", foreground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        # Encabezado con logo
        header_frame = tk.Frame(self.root, bg="#1e1e2f")
        header_frame.pack(pady=10, fill=tk.X)

        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).resize((80, 80))
            logo_img = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(header_frame, image=logo_img, bg="#1e1e2f")
            logo_label.image = logo_img
            logo_label.pack(side=tk.LEFT, padx=10)

        title_label = tk.Label(
            header_frame,
            text="KultaBass-TABS",
            font=("Segoe UI", 32, "bold"),
            bg="#1e1e2f",
            fg="#ffffff"
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            self.root,
            text="dev dI-eGo",
            font=("Segoe UI", 13),
            bg="#1e1e2f",
            fg="#aaaaaa"
        )
        subtitle_label.pack()

        # Botones
        button_frame = tk.Frame(self.root, bg="#1e1e2f")
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(
            button_frame,
            text="➕ Añadir Tablatura",
            command=self.add_tab_file
        )
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.start_scroll_button = ttk.Button(
            button_frame,
            text="▶️ Iniciar Scroll",
            command=self.start_auto_scroll
        )
        self.start_scroll_button.pack(side=tk.LEFT, padx=5)

        self.stop_scroll_button = ttk.Button(
            button_frame,
            text="⏹️ Detener Scroll",
            command=self.stop_auto_scroll
        )
        self.stop_scroll_button.pack(side=tk.LEFT, padx=5)

        speed_frame = tk.Frame(button_frame, bg="#1e1e2f")
        speed_frame.pack(side=tk.LEFT, padx=5)

        self.speed_entry = ttk.Entry(speed_frame, width=5)
        self.speed_entry.insert(0, "1")
        self.speed_entry.pack(side=tk.LEFT)

        ttk.Label(speed_frame, text="líneas/s", foreground="white", background="#1e1e2f").pack(side=tk.LEFT)

        # Listado scrollable
        list_frame = tk.Frame(self.root, bg="#1e1e2f")
        list_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.tab_listbox = tk.Listbox(
            list_frame,
            bg="#2d2d3d",
            fg="#ffffff",
            selectbackground="#444466",
            selectforeground="#ffffff",
            font=("Consolas", 14),
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.tab_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tab_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tab_listbox.config(yscrollcommand=scrollbar.set)

        # Área de texto con scroll automático
        preview_frame = tk.Frame(self.root, bg="#2d2d3d")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tab_text_area = st.ScrolledText(
            preview_frame,
            bg="#111111",
            fg="#00ffaa",
            font=("Consolas", 14),
            wrap=tk.NONE
        )
        self.tab_text_area.pack(fill=tk.BOTH, expand=True)
        self.tab_text_area.config(state='disabled')

        # Evento click en lista
        self.tab_listbox.bind("<<ListboxSelect>>", self.on_select)

    def add_tab_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos TXT", "*.txt")])
        if not file_path:
            return

        filename = os.path.basename(file_path)
        dest_path = os.path.join(TAB_FOLDER, filename)

        if os.path.exists(dest_path):
            messagebox.showwarning("Archivo duplicado", "Esta tablatura ya está guardada.")
            return

        shutil.copy(file_path, dest_path)
        self.load_saved_tabs()
        messagebox.showinfo("Éxito", "Tablatura añadida correctamente.")

    def load_saved_tabs(self):
        self.tab_listbox.delete(0, tk.END)
        if not os.path.exists(TAB_FOLDER):
            os.makedirs(TAB_FOLDER)

        tabs = sorted([f for f in os.listdir(TAB_FOLDER) if f.endswith(".txt")])
        for tab in tabs:
            self.tab_listbox.insert(tk.END, tab)

    def on_select(self, event):
        selected = self.tab_listbox.curselection()
        if not selected:
            return

        filename = self.tab_listbox.get(selected[0])
        path = os.path.join(TAB_FOLDER, filename)

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
            self.current_lines = content.splitlines()

            self.tab_text_area.config(state='normal')
            self.tab_text_area.delete(1.0, tk.END)
            self.tab_text_area.insert(tk.END, "\n".join(self.current_lines))
            self.tab_text_area.config(state='disabled')

            self.stop_auto_scroll()  # Reiniciar scroll si estaba activo

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tablatura:\n{e}")

    def start_auto_scroll(self):
        try:
            speed = float(self.speed_entry.get())
            self.scroll_speed = int(1000 / speed)
        except:
            self.scroll_speed = 1000

        if not hasattr(self, 'current_lines') or len(self.current_lines) == 0:
            messagebox.showwarning("Advertencia", "No hay tablatura cargada.")
            return

        self.auto_scroll_active = True
        self._auto_scroll()

    def stop_auto_scroll(self):
        self.auto_scroll_active = False
        if self.scroll_job:
            self.root.after_cancel(self.scroll_job)
        self.tab_text_area.yview_moveto(0.0)  # Volver arriba

    def _auto_scroll(self):
        if not self.auto_scroll_active:
            return

        self.tab_text_area.yview_scroll(1, tk.UNITS)
        self.scroll_job = self.root.after(self.scroll_speed, self._auto_scroll)

    def on_closing(self):
        self.stop_auto_scroll()
        self.root.destroy()


if __name__ == "__main__":
    if not os.path.exists(TAB_FOLDER):
        os.makedirs(TAB_FOLDER)

    root = tk.Tk()
    app = KultaBassTabsApp(root)

    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()