# frontend/ui.py
import time
import tkinter as tk
from tkinter import ttk, messagebox

from backend.m1_pesanan import DynamicArray, LinkedList
from backend.m2_antrean import (
    ke_postfix, hitung,
    AntreanNaif, AntreanMelingkar,
    ManajerUndoRedo
)

class EZ4UApp:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery Engine")
        self.root.geometry("1000x650")

        self.arr_pesanan = DynamicArray()
        self.list_pesanan = LinkedList()
        self.q_naif = AntreanNaif(200000)
        self.q_circular = AntreanMelingkar(200000)
        self.undo_redo = ManajerUndoRedo(self.q_naif, self.q_circular)

        self._build_layout()
        self._load_csv_data()

    def _build_layout(self):
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        sidebar = ttk.Frame(main_paned, width=240)
        main_paned.add(sidebar, weight=1)

        canvas = tk.Canvas(sidebar, borderwidth=0)
        scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        self.nav_box = ttk.Frame(canvas)
        self.nav_box.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.nav_box, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_sidebar_menu()

        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=4)

        self.content_frame = ttk.LabelFrame(right_frame, text=" Area Kerja / Output ", padding=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        cmd_frame = ttk.LabelFrame(right_frame, text=" Command Log & Execution Time ", padding=5)
        cmd_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.cmd_tree = ttk.Treeview(cmd_frame, columns=("cmd", "modul", "time"), show="headings", height=5)
        self.cmd_tree.heading("cmd", text="Perintah")
        self.cmd_tree.heading("modul", text="Modul Backend")
        self.cmd_tree.heading("time", text="Waktu Eksekusi")
        self.cmd_tree.column("cmd", width=350)
        self.cmd_tree.column("modul", width=180)
        self.cmd_tree.column("time", width=120, anchor="e")

        cmd_scroll = ttk.Scrollbar(cmd_frame, orient="vertical", command=self.cmd_tree.yview)
        self.cmd_tree.configure(yscrollcommand=cmd_scroll.set)
        self.cmd_tree.pack(side="left", fill="both", expand=True)
        cmd_scroll.pack(side="right", fill="y")

        self.show_view_array()

    def _build_sidebar_menu(self):
        def add_header(text):
            lbl = ttk.Label(self.nav_box, text=text, font=("Arial", 9, "bold"), foreground="#004080")
            lbl.pack(anchor="w", pady=(10, 2), padx=5)

        def add_btn(text, cmd):
            btn = ttk.Button(self.nav_box, text=text, command=cmd)
            btn.pack(fill="x", padx=5, pady=1)

        add_header("DATA")
        add_btn("Muat / Reload Data CSV", self._load_csv_data)

        add_header("M1 - DATA PESANAN")
        add_btn("Array - Lihat Pesanan ke-i", self.show_view_array)
        add_btn("Array - Tambah Reguler", lambda: self.show_add_order("Array", "REGULER"))
        add_btn("Array - Tambah Prioritas", lambda: self.show_add_order("Array", "PRIORITAS"))
        add_btn("Array - Tambah VIP", lambda: self.show_add_order("Array", "VIP"))
        add_btn("Array - Hapus Pesanan", lambda: self.show_delete_order("Array"))

        add_btn("LinkedList - Lihat Pesanan ke-i", self.show_view_linkedlist)
        add_btn("LinkedList - Tambah Reguler", lambda: self.show_add_order("LinkedList", "REGULER"))
        add_btn("LinkedList - Tambah Prioritas", lambda: self.show_add_order("LinkedList", "PRIORITAS"))
        add_btn("LinkedList - Tambah VIP", lambda: self.show_add_order("LinkedList", "VIP"))
        add_btn("LinkedList - Hapus Pesanan", lambda: self.show_delete_order("LinkedList"))

        add_header("M2 - STACK & QUEUE")
        add_btn("Stack - Hitung Kasir (Postfix)", self.show_kasir)
        add_btn("Queue - Enqueue", self.show_enqueue)
        add_btn("Queue - Dequeue Naif", self.show_dequeue_naive)
        add_btn("Queue - Dequeue Circular", self.show_dequeue_circular)
        add_btn("Stack - Undo", self.do_undo)
        add_btn("Stack - Redo", self.do_redo)

    def log_command(self, cmd_name, modul_name, waktu_ms):
        self.cmd_tree.insert("", 0, values=(cmd_name, modul_name, f"{waktu_ms:.3f} ms"))

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _load_csv_data(self):
        start = time.time()
        self.arr_pesanan = DynamicArray()
        self.list_pesanan = LinkedList()
        self.q_naif = AntreanNaif(200000)
        self.q_circular = AntreanMelingkar(200000)

        count = 0
        try:
            with open("data/pesanan.csv", "r", encoding="utf-8") as f:
                f.readline()
                for line in f:
                    line = line.strip()
                    if line:
                        self.arr_pesanan.append(line)
                        self.list_pesanan.append(line)
                        self.q_naif.enqueue(line)
                        self.q_circular.enqueue(line)
                        count += 1
        except Exception:
            pass

        elapsed = (time.time() - start) * 1000
        self.log_command(f"Load {count} Data CSV", "Backend Data", elapsed)

    # =========================================================
    # FITUR M1: DYNAMIC ARRAY & LINKEDLIST (AKSES INDEKS KE-i)
    # =========================================================

    def show_view_array(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Array: Lihat Pesanan ke-i", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text=f"Total data tersedia: {self.arr_pesanan.size:,} pesanan", font=("Arial", 9)).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w", pady=(0, 10))

        ttk.Label(f_form, text="Indeks pesanan (i):").grid(row=0, column=0, sticky="w")
        ent_idx = ttk.Entry(f_form, width=15)
        ent_idx.grid(row=0, column=1, padx=5)
        ent_idx.insert(0, "0")

        lbl_result = ttk.Label(self.content_frame, text="Detail Pesanan:\n-", font=("Arial", 9), justify="left", relief=tk.SOLID, padding=8)
        lbl_result.pack(fill=tk.X, anchor="w", pady=5)

        def submit():
            try:
                idx = int(ent_idx.get())
                if idx < 0 or idx >= self.arr_pesanan.size:
                    messagebox.showerror("Indeks Tidak Valid", f"Indeks harus di antara 0 sampai {self.arr_pesanan.size - 1}")
                    return

                start = time.time()
                item = self.arr_pesanan.get(idx)
                elapsed = (time.time() - start) * 1000

                lbl_result.config(text=f"Detail Pesanan pada Indeks {idx}:\n{item}")
                self.log_command(f"Array Get (i={idx})", "M1 - DynamicArray", elapsed)
            except ValueError:
                messagebox.showerror("Eror", "Masukkan angka indeks yang valid.")

        ttk.Button(f_form, text="Lihat Pesanan", command=submit).grid(row=0, column=2, padx=5)

    def show_view_linkedlist(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="LinkedList: Lihat Pesanan ke-i", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text=f"Total data tersedia: {self.list_pesanan.size:,} pesanan", font=("Arial", 9)).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w", pady=(0, 10))

        ttk.Label(f_form, text="Indeks pesanan (i):").grid(row=0, column=0, sticky="w")
        ent_idx = ttk.Entry(f_form, width=15)
        ent_idx.grid(row=0, column=1, padx=5)
        ent_idx.insert(0, "0")

        lbl_result = ttk.Label(self.content_frame, text="Detail Pesanan:\n-", font=("Arial", 9), justify="left", relief=tk.SOLID, padding=8)
        lbl_result.pack(fill=tk.X, anchor="w", pady=5)

        def submit():
            try:
                idx = int(ent_idx.get())
                if idx < 0 or idx >= self.list_pesanan.size:
                    messagebox.showerror("Indeks Tidak Valid", f"Indeks harus di antara 0 sampai {self.list_pesanan.size - 1}")
                    return

                start = time.time()
                item = self.list_pesanan.get(idx)
                elapsed = (time.time() - start) * 1000

                lbl_result.config(text=f"Detail Pesanan pada Indeks {idx}:\n{item}")
                self.log_command(f"LinkedList Get (i={idx})", "M1 - LinkedList", elapsed)
            except ValueError:
                messagebox.showerror("Eror", "Masukkan angka indeks yang valid.")

        ttk.Button(f_form, text="Lihat Pesanan", command=submit).grid(row=0, column=2, padx=5)

    def show_add_order(self, ds_type, priority):
        self._clear_content()
        ttk.Label(self.content_frame, text=f"Tambah Pesanan {priority} ke {ds_type}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        frame_form = ttk.Frame(self.content_frame)
        frame_form.pack(fill=tk.X, anchor="w")

        ttk.Label(frame_form, text="Nama Pelanggan:").grid(row=0, column=0, sticky="w", pady=2)
        ent_nama = ttk.Entry(frame_form, width=30)
        ent_nama.grid(row=0, column=1, padx=5, pady=2)
        ent_nama.insert(0, "Pelanggan Baru")

        ttk.Label(frame_form, text="Nama Menu:").grid(row=1, column=0, sticky="w", pady=2)
        ent_menu = ttk.Entry(frame_form, width=30)
        ent_menu.grid(row=1, column=1, padx=5, pady=2)
        ent_menu.insert(0, "Nasi Goreng")

        def submit():
            nama = ent_nama.get()
            menu = ent_menu.get()
            item_str = f"ORD-NEW,{nama},resto-01,{menu},20000,1,00:00:00,,ANTRE"

            start = time.time()
            if ds_type == "Array":
                if priority == "VIP": self.arr_pesanan.prepend(item_str)
                elif priority == "PRIORITAS": self.arr_pesanan.insert(self.arr_pesanan.size // 2, item_str)
                else: self.arr_pesanan.append(item_str)
            else:
                if priority == "VIP": self.list_pesanan.prepend(item_str)
                elif priority == "PRIORITAS": self.list_pesanan.insert(self.list_pesanan.size // 2, item_str)
                else: self.list_pesanan.append(item_str)

            elapsed = (time.time() - start) * 1000
            self.log_command(f"Insert {priority} ({ds_type})", f"M1 - {ds_type}", elapsed)
            messagebox.showinfo("Berhasil", f"Pesanan {priority} berhasil dimasukkan ke {ds_type}!")

        ttk.Button(frame_form, text="Tambahkan Pesanan", command=submit).grid(row=2, column=1, sticky="w", pady=10)

    def show_delete_order(self, ds_type):
        self._clear_content()
        ttk.Label(self.content_frame, text=f"Hapus Pesanan dari {ds_type}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        frame_form = ttk.Frame(self.content_frame)
        frame_form.pack(fill=tk.X, anchor="w")

        ttk.Label(frame_form, text="Indeks yang ingin dihapus:").grid(row=0, column=0, sticky="w")
        ent_idx = ttk.Entry(frame_form, width=15)
        ent_idx.grid(row=0, column=1, padx=5)
        ent_idx.insert(0, "0")

        def submit():
            try:
                idx = int(ent_idx.get())
                start = time.time()
                if ds_type == "Array": self.arr_pesanan.delete(idx)
                else: self.list_pesanan.delete(idx)
                elapsed = (time.time() - start) * 1000

                self.log_command(f"Delete Index {idx} ({ds_type})", f"M1 - {ds_type}", elapsed)
                messagebox.showinfo("Berhasil", f"Elemen indeks {idx} berhasil dihapus dari {ds_type}!")
            except Exception as e:
                messagebox.showerror("Eror", f"Gagal menghapus: {e}")

        ttk.Button(frame_form, text="Hapus Elemen", command=submit).grid(row=1, column=1, sticky="w", pady=10)

    # =========================================================
    # FITUR M2: KASIR, QUEUE NAIF/CIRCULAR, UNDO/REDO
    # =========================================================

    def show_kasir(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Hitung Struk Kasir (Stack Infix ke Postfix)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Ekspresi Infix:").grid(row=0, column=0, sticky="w")
        ent_expr = ttk.Entry(f_form, width=45)
        ent_expr.grid(row=0, column=1, padx=5, pady=2)
        ent_expr.insert(0, "(3 * 12000) + (2 * 8500) - 5000")

        lbl_postfix = ttk.Label(self.content_frame, text="Hasil Postfix : -", font=("Arial", 10))
        lbl_postfix.pack(anchor="w", pady=(10, 2))

        lbl_total = ttk.Label(self.content_frame, text="Total Belanja : Rp 0", font=("Arial", 11, "bold"), foreground="#006600")
        lbl_total.pack(anchor="w", pady=2)

        def hitung_struk():
            expr = ent_expr.get()
            start = time.time()

            postfix_arr = ke_postfix(expr)
            total_val = hitung(postfix_arr)

            elapsed = (time.time() - start) * 1000

            lbl_postfix.config(text=f"Hasil Postfix : {' '.join(postfix_arr)}")
            lbl_total.config(text=f"Total Belanja : Rp {total_val:,}")
            self.log_command("ke_postfix & hitung", "M2 - Stack Kasir", elapsed)

        ttk.Button(f_form, text="Proses & Hitung", command=hitung_struk).grid(row=1, column=1, sticky="w", pady=5)

    def show_enqueue(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Enqueue Pesanan Baru ke Queue", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Data Pesanan:").grid(row=0, column=0, sticky="w")
        ent_data = ttk.Entry(f_form, width=40)
        ent_data.grid(row=0, column=1, padx=5)
        ent_data.insert(0, "ORD-99999,Pelanggan_Baru,resto-01,menu-01,15000,1,ANTRE")

        lbl_status = ttk.Label(
            self.content_frame,
            text=f"Status Queue Saat Ini:\n- Antrean Naif Size    : {self.q_naif.size():,}\n- Antrean Circular Size: {self.q_circular.size():,}",
            font=("Arial", 9)
        )
        lbl_status.pack(anchor="w", pady=10)

        def submit():
            item = ent_data.get()
            start = time.time()

            self.q_naif.enqueue(item)
            self.q_circular.enqueue(item)
            self.undo_redo.catat_aksi("ENQUEUE", item)

            elapsed = (time.time() - start) * 1000

            lbl_status.config(
                text=f"Status Queue Saat Ini:\n- Antrean Naif Size    : {self.q_naif.size():,}\n- Antrean Circular Size: {self.q_circular.size():,}"
            )
            self.log_command("enqueue", "M2 - Queue", elapsed)
            messagebox.showinfo("Berhasil", "Data berhasil di-enqueue ke kedua antrean!")

        ttk.Button(f_form, text="Enqueue Pesanan", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def show_dequeue_naive(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Dequeue pada Antrean Naif (O(n) - Geser Elemen)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Jumlah Dequeue:").grid(row=0, column=0, sticky="w")
        ent_k = ttk.Entry(f_form, width=10)
        ent_k.grid(row=0, column=1, padx=5)
        ent_k.insert(0, "1")

        lbl_res = ttk.Label(
            self.content_frame,
            text=f"Sisa Antrean Naif  : {self.q_naif.size():,}\nTotal Elemen Digeser: {self.q_naif.total_geseran:,}",
            font=("Arial", 9)
        )
        lbl_res.pack(anchor="w", pady=10)

        def submit():
            try:
                k = int(ent_k.get())
                start = time.time()

                for _ in range(k):
                    item = self.q_naif.dequeue()
                    if item:
                        self.undo_redo.catat_aksi("DEQUEUE", item)

                elapsed = (time.time() - start) * 1000

                lbl_res.config(
                    text=f"Sisa Antrean Naif  : {self.q_naif.size():,}\nTotal Elemen Digeser: {self.q_naif.total_geseran:,}"
                )
                self.log_command(f"dequeue naif ({k}x)", "M2 - AntreanNaif", elapsed)
            except Exception as e:
                messagebox.showerror("Eror", f"Gagal Dequeue: {e}")

        ttk.Button(f_form, text="Jalankan Dequeue Naif", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def show_dequeue_circular(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Dequeue pada Antrean Circular (O(1) - Pointer Shift)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Jumlah Dequeue:").grid(row=0, column=0, sticky="w")
        ent_k = ttk.Entry(f_form, width=10)
        ent_k.grid(row=0, column=1, padx=5)
        ent_k.insert(0, "1")

        lbl_res = ttk.Label(
            self.content_frame,
            text=f"Sisa Antrean Circular: {self.q_circular.size():,}\nFront Index: {self.q_circular.front}\nRear Index : {self.q_circular.rear}",
            font=("Arial", 9)
        )
        lbl_res.pack(anchor="w", pady=10)

        def submit():
            try:
                k = int(ent_k.get())
                start = time.time()

                for _ in range(k):
                    item = self.q_circular.dequeue()
                    if item:
                        self.undo_redo.catat_aksi("DEQUEUE", item)

                elapsed = (time.time() - start) * 1000

                lbl_res.config(
                    text=f"Sisa Antrean Circular: {self.q_circular.size():,}\nFront Index: {self.q_circular.front}\nRear Index : {self.q_circular.rear}"
                )
                self.log_command(f"dequeue circular ({k}x)", "M2 - AntreanMelingkar", elapsed)
            except Exception as e:
                messagebox.showerror("Eror", f"Gagal Dequeue: {e}")

        ttk.Button(f_form, text="Jalankan Dequeue Circular", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def do_undo(self):
        start = time.time()
        aksi = self.undo_redo.undo_last()
        elapsed = (time.time() - start) * 1000

        if aksi:
            jenis, data = aksi
            self.log_command(f"Undo ({jenis})", "M2 - ManajerUndoRedo", elapsed)
            messagebox.showinfo("Undo Berhasil", f"Aksi dibatalkan: {jenis}\nPanjang Antrean Sekarang: {self.q_circular.size():,}")
        else:
            messagebox.showwarning("Undo Warning", "Tidak ada riwayat untuk di-undo.")

    def do_redo(self):
        start = time.time()
        aksi = self.undo_redo.redo_last()
        elapsed = (time.time() - start) * 1000

        if aksi:
            jenis, data = aksi
            self.log_command(f"Redo ({jenis})", "M2 - ManajerUndoRedo", elapsed)
            messagebox.showinfo("Redo Berhasil", f"Aksi diulangi: {jenis}\nPanjang Antrean Sekarang: {self.q_circular.size():,}")
        else:
            messagebox.showwarning("Redo Warning", "Tidak ada riwayat untuk di-redo.")


def launch_app():
    root = tk.Tk()
    app = EZ4UApp(root)
    root.mainloop()