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
from backend.m3_laporan import (
    linear_search, binary_search,
    insertion_sort, merge_sort
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
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        sidebar = ttk.Frame(main, width=240)
        main.add(sidebar, weight=1)

        canvas = tk.Canvas(sidebar, borderwidth=0)
        scrollbar = ttk.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        self.nav_box = ttk.Frame(canvas)
        self.nav_box.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.nav_box, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._build_sidebar_menu()

        right = ttk.Frame(main)
        main.add(right, weight=4)

        self.content_frame = ttk.LabelFrame(right, text=" Area Kerja / Output ", padding=10)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        cmd_frame = ttk.LabelFrame(right, text=" Command Log & Execution Time ", padding=5)
        cmd_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.cmd_tree = ttk.Treeview(cmd_frame, columns=("cmd", "modul", "time"), show="headings", height=5)
        self.cmd_tree.heading("cmd", text="Perintah")
        self.cmd_tree.heading("modul", text="Modul Backend")
        self.cmd_tree.heading("time", text="Waktu Eksekusi")
        self.cmd_tree.column("cmd", width=350)
        self.cmd_tree.column("modul", width=180)
        self.cmd_tree.column("time", width=120, anchor="e")

        c_scroll = ttk.Scrollbar(cmd_frame, orient="vertical", command=self.cmd_tree.yview)
        self.cmd_tree.configure(yscrollcommand=c_scroll.set)
        self.cmd_tree.pack(side="left", fill="both", expand=True)
        c_scroll.pack(side="right", fill="y")

        self.show_view_array()

    def _build_sidebar_menu(self):
        def header(text):
            ttk.Label(self.nav_box, text=text, font=("Arial", 9, "bold"), foreground="#004080").pack(anchor="w", pady=(10, 2), padx=5)

        def btn(text, cmd):
            ttk.Button(self.nav_box, text=text, command=cmd).pack(fill="x", padx=5, pady=1)

        header("DATA")
        btn("Muat / Reload Data CSV", self._load_csv_data)

        header("M1 - DATA PESANAN")
        btn("Array - Lihat Pesanan ke-i", self.show_view_array)
        btn("Array - Tambah Reguler", lambda: self.show_add_order("Array", "REGULER"))
        btn("Array - Tambah Prioritas", lambda: self.show_add_order("Array", "PRIORITAS"))
        btn("Array - Tambah VIP", lambda: self.show_add_order("Array", "VIP"))
        btn("Array - Hapus Pesanan", lambda: self.show_delete_order("Array"))

        btn("LinkedList - Lihat Pesanan ke-i", self.show_view_linkedlist)
        btn("LinkedList - Tambah Reguler", lambda: self.show_add_order("LinkedList", "REGULER"))
        btn("LinkedList - Tambah Prioritas", lambda: self.show_add_order("LinkedList", "PRIORITAS"))
        btn("LinkedList - Tambah VIP", lambda: self.show_add_order("LinkedList", "VIP"))
        btn("LinkedList - Hapus Pesanan", lambda: self.show_delete_order("LinkedList"))

        header("M2 - STACK & QUEUE")
        btn("Stack - Hitung Kasir (Postfix)", self.show_kasir)
        btn("Queue - Enqueue", self.show_enqueue)
        btn("Queue - Dequeue Naif", self.show_dequeue_naive)
        btn("Queue - Dequeue Circular", self.show_dequeue_circular)
        btn("Stack - Undo", self.do_undo)
        btn("Stack - Redo", self.do_redo)

        header("M3 - SORTING & SEARCHING")
        btn("Searching - Linear Search", self.show_linear_search)
        btn("Searching - Binary Search", self.show_binary_search)
        btn("Sorting - Bubble Sort vs Quick Sort", self.show_sorting_demo)

    def log_command(self, cmd_name, modul_name, waktu_ms):
        self.cmd_tree.insert("", 0, values=(cmd_name, modul_name, f"{waktu_ms:.3f} ms"))

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _load_csv_data(self):
        start = time.time()
        self.arr_pesanan, self.list_pesanan = DynamicArray(), LinkedList()
        self.q_naif, self.q_circular = AntreanNaif(200000), AntreanMelingkar(200000)

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

        self.log_command(f"Load {count} Data CSV", "Backend Data", (time.time() - start) * 1000)

    # --- VIEWS M1 ---

    def _render_get_ui(self, title, ds_obj, ds_name):
        self._clear_content()
        ttk.Label(self.content_frame, text=f"{ds_name}: Lihat Pesanan ke-i", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(self.content_frame, text=f"Total data: {ds_obj.size:,} pesanan", font=("Arial", 9)).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w", pady=(0, 10))

        ttk.Label(f_form, text="Indeks (i):").grid(row=0, column=0, sticky="w")
        ent_idx = ttk.Entry(f_form, width=15)
        ent_idx.grid(row=0, column=1, padx=5)
        ent_idx.insert(0, "0")

        lbl_res = ttk.Label(self.content_frame, text="Detail Pesanan:\n-", font=("Arial", 9), relief=tk.SOLID, padding=8)
        lbl_res.pack(fill=tk.X, anchor="w", pady=5)

        def submit():
            try:
                idx = int(ent_idx.get())
                if not (0 <= idx < ds_obj.size):
                    messagebox.showerror("Error", f"Indeks harus 0 - {ds_obj.size - 1}")
                    return
                start = time.time()
                item = ds_obj.get(idx)
                elapsed = (time.time() - start) * 1000
                lbl_res.config(text=f"Detail Indeks {idx}:\n{item}")
                self.log_command(f"{ds_name} Get (i={idx})", f"M1 - {ds_name}", elapsed)
            except ValueError:
                messagebox.showerror("Error", "Masukkan angka indeks yang valid.")

        ttk.Button(f_form, text="Lihat Pesanan", command=submit).grid(row=0, column=2, padx=5)

    def show_view_array(self): self._render_get_ui("Array", self.arr_pesanan, "DynamicArray")
    def show_view_linkedlist(self): self._render_get_ui("LinkedList", self.list_pesanan, "LinkedList")

    def show_add_order(self, ds_type, priority):
        self._clear_content()
        ttk.Label(self.content_frame, text=f"Tambah {priority} ke {ds_type}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Nama Pelanggan:").grid(row=0, column=0, sticky="w", pady=2)
        ent_nama = ttk.Entry(f_form, width=30)
        ent_nama.grid(row=0, column=1, padx=5, pady=2)
        ent_nama.insert(0, "Pelanggan Baru")

        def submit():
            nama = ent_nama.get()
            item = f"ORD-NEW,{nama},resto-01,menu-01,20000,1,00:00:00,,ANTRE"
            ds = self.arr_pesanan if ds_type == "Array" else self.list_pesanan
            start = time.time()

            if priority == "VIP": ds.prepend(item)
            elif priority == "PRIORITAS": ds.insert(ds.size // 2, item)
            else: ds.append(item)

            self.log_command(f"Insert {priority} ({ds_type})", f"M1 - {ds_type}", (time.time() - start) * 1000)
            messagebox.showinfo("Berhasil", f"Pesanan {priority} berhasil ditambahkan!")

        ttk.Button(f_form, text="Tambahkan Pesanan", command=submit).grid(row=1, column=1, sticky="w", pady=10)

    def show_delete_order(self, ds_type):
        self._clear_content()
        ttk.Label(self.content_frame, text=f"Hapus Pesanan dari {ds_type}", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Indeks Hapus:").grid(row=0, column=0, sticky="w")
        ent_idx = ttk.Entry(f_form, width=15)
        ent_idx.grid(row=0, column=1, padx=5)
        ent_idx.insert(0, "0")

        def submit():
            try:
                idx = int(ent_idx.get())
                ds = self.arr_pesanan if ds_type == "Array" else self.list_pesanan
                start = time.time()
                ds.delete(idx)
                self.log_command(f"Delete Index {idx} ({ds_type})", f"M1 - {ds_type}", (time.time() - start) * 1000)
                messagebox.showinfo("Berhasil", f"Pesanan indeks {idx} dihapus!")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal: {e}")

        ttk.Button(f_form, text="Hapus Elemen", command=submit).grid(row=1, column=1, sticky="w", pady=10)

    # --- VIEWS M2 ---

    def show_kasir(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Hitung Struk Kasir (Postfix Evaluator)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Infix:").grid(row=0, column=0, sticky="w")
        ent_expr = ttk.Entry(f_form, width=45)
        ent_expr.grid(row=0, column=1, padx=5)
        ent_expr.insert(0, "(3 * 12000) + (2 * 8500) - 5000")

        lbl_pf = ttk.Label(self.content_frame, text="Hasil Postfix : -", font=("Arial", 10))
        lbl_pf.pack(anchor="w", pady=(10, 2))
        lbl_tot = ttk.Label(self.content_frame, text="Total Belanja : Rp 0", font=("Arial", 11, "bold"), foreground="#006600")
        lbl_tot.pack(anchor="w", pady=2)

        def submit():
            start = time.time()
            pf = ke_postfix(ent_expr.get())
            tot = hitung(pf)
            lbl_pf.config(text=f"Hasil Postfix : {' '.join(pf)}")
            lbl_tot.config(text=f"Total Belanja : Rp {tot:,}")
            self.log_command("ke_postfix & hitung", "M2 - Stack Kasir", (time.time() - start) * 1000)

        ttk.Button(f_form, text="Proses & Hitung", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def show_enqueue(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Enqueue Pesanan Baru", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Data Pesanan:").grid(row=0, column=0, sticky="w")
        ent_data = ttk.Entry(f_form, width=40)
        ent_data.grid(row=0, column=1, padx=5)
        ent_data.insert(0, "ORD-99999,Pelanggan_Baru,resto-01,menu-01,15000,1,ANTRE")

        lbl_st = ttk.Label(self.content_frame, text=f"Queue Size -> Naif: {self.q_naif.size():,}, Circular: {self.q_circular.size():,}", font=("Arial", 9))
        lbl_st.pack(anchor="w", pady=10)

        def submit():
            item = ent_data.get()
            start = time.time()
            self.q_naif.enqueue(item)
            self.q_circular.enqueue(item)
            self.undo_redo.catat_aksi("ENQUEUE", item)
            lbl_st.config(text=f"Queue Size -> Naif: {self.q_naif.size():,}, Circular: {self.q_circular.size():,}")
            self.log_command("enqueue", "M2 - Queue", (time.time() - start) * 1000)
            messagebox.showinfo("Berhasil", "Data masuk ke antrean!")

        ttk.Button(f_form, text="Enqueue Pesanan", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def show_dequeue_naive(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Dequeue Naif (O(n) - Geser Elemen)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Jumlah Dequeue:").grid(row=0, column=0, sticky="w")
        ent_k = ttk.Entry(f_form, width=10)
        ent_k.grid(row=0, column=1, padx=5)
        ent_k.insert(0, "1")

        lbl_res = ttk.Label(self.content_frame, text=f"Sisa Naif: {self.q_naif.size():,} | Total Geseran: {self.q_naif.total_geseran:,}", font=("Arial", 9))
        lbl_res.pack(anchor="w", pady=10)

        def submit():
            try:
                k = int(ent_k.get())
                start = time.time()
                for _ in range(k):
                    item = self.q_naif.dequeue()
                    if item: self.undo_redo.catat_aksi("DEQUEUE", item)
                lbl_res.config(text=f"Sisa Naif: {self.q_naif.size():,} | Total Geseran: {self.q_naif.total_geseran:,}")
                self.log_command(f"dequeue naif ({k}x)", "M2 - AntreanNaif", (time.time() - start) * 1000)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal: {e}")

        ttk.Button(f_form, text="Jalankan Dequeue Naif", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def show_dequeue_circular(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Dequeue Circular (O(1) - Pointer Shift)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Jumlah Dequeue:").grid(row=0, column=0, sticky="w")
        ent_k = ttk.Entry(f_form, width=10)
        ent_k.grid(row=0, column=1, padx=5)
        ent_k.insert(0, "1")

        lbl_res = ttk.Label(self.content_frame, text=f"Sisa Circular: {self.q_circular.size():,} | Front: {self.q_circular.front} | Rear: {self.q_circular.rear}", font=("Arial", 9))
        lbl_res.pack(anchor="w", pady=10)

        def submit():
            try:
                k = int(ent_k.get())
                start = time.time()
                for _ in range(k):
                    item = self.q_circular.dequeue()
                    if item: self.undo_redo.catat_aksi("DEQUEUE", item)
                lbl_res.config(text=f"Sisa Circular: {self.q_circular.size():,} | Front: {self.q_circular.front} | Rear: {self.q_circular.rear}")
                self.log_command(f"dequeue circular ({k}x)", "M2 - AntreanMelingkar", (time.time() - start) * 1000)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal: {e}")

        ttk.Button(f_form, text="Jalankan Dequeue Circular", command=submit).grid(row=1, column=1, sticky="w", pady=5)

    def do_undo(self):
        start = time.time()
        aksi = self.undo_redo.undo_last()
        if aksi:
            self.log_command(f"Undo ({aksi[0]})", "M2 - ManajerUndoRedo", (time.time() - start) * 1000)
            messagebox.showinfo("Undo Berhasil", f"Aksi dibatalkan: {aksi[0]}\nSisa Antrean: {self.q_circular.size():,}")
        else:
            messagebox.showwarning("Warning", "Tidak ada riwayat undo.")

    def do_redo(self):
        start = time.time()
        aksi = self.undo_redo.redo_last()
        if aksi:
            self.log_command(f"Redo ({aksi[0]})", "M2 - ManajerUndoRedo", (time.time() - start) * 1000)
            messagebox.showinfo("Redo Berhasil", f"Aksi diulangi: {aksi[0]}\nSisa Antrean: {self.q_circular.size():,}")
        else:
            messagebox.showwarning("Warning", "Tidak ada riwayat redo.")

    # --- VIEWS M3: SEARCHING & SORTING ---

    def show_linear_search(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Linear Search - O(n)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Target Order ID:").grid(row=0, column=0, sticky="w")
        ent_target = ttk.Entry(f_form, width=25)
        ent_target.grid(row=0, column=1, padx=5)
        ent_target.insert(0, "ORD-15000")

        lbl_res = ttk.Label(self.content_frame, text="Hasil Pencarian:\n-", font=("Arial", 9), relief=tk.SOLID, padding=8)
        lbl_res.pack(fill=tk.X, anchor="w", pady=10)

        def submit():
            target = ent_target.get().strip()
            start = time.time()
            idx = linear_search(self.arr_pesanan, target, col_idx=0)
            elapsed = (time.time() - start) * 1000

            if idx != -1:
                lbl_res.config(text=f"Ditemukan pada Indeks: {idx}\nData: {self.arr_pesanan.get(idx)}")
            else:
                lbl_res.config(text=f"Data ID '{target}' tidak ditemukan.")

            self.log_command(f"Linear Search '{target}'", "M3 - LinearSearch", elapsed)

        ttk.Button(f_form, text="Cari Data", command=submit).grid(row=0, column=2, padx=5)

    def show_binary_search(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Binary Search - O(log n)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Target Order ID:").grid(row=0, column=0, sticky="w")
        ent_target = ttk.Entry(f_form, width=25)
        ent_target.grid(row=0, column=1, padx=5)
        ent_target.insert(0, "ORD-15000")

        lbl_info = ttk.Label(self.content_frame, text="Catatan: Binary Search membutuhkan data terurut.", font=("Arial", 8, "italic"), foreground="#888888")
        lbl_info.pack(anchor="w", pady=(2, 5))

        lbl_res = ttk.Label(self.content_frame, text="Hasil Pencarian:\n-", font=("Arial", 9), relief=tk.SOLID, padding=8)
        lbl_res.pack(fill=tk.X, anchor="w", pady=5)

        def submit():
            target = ent_target.get().strip()
            start = time.time()
            idx = binary_search(self.arr_pesanan, target, col_idx=0)
            elapsed = (time.time() - start) * 1000

            if idx != -1:
                lbl_res.config(text=f"Ditemukan pada Indeks: {idx}\nData: {self.arr_pesanan.get(idx)}")
            else:
                lbl_res.config(text=f"Data ID '{target}' tidak ditemukan (Pastikan data terurut ID).")

            self.log_command(f"Binary Search '{target}'", "M3 - BinarySearch", elapsed)

        ttk.Button(f_form, text="Cari Data", command=submit).grid(row=0, column=2, padx=5)

    def show_sorting_demo(self):
        self._clear_content()
        ttk.Label(self.content_frame, text="Pengujian Sorting: Insertion Sort O(n^2) vs Merge Sort O(n log n)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        f_form = ttk.Frame(self.content_frame)
        f_form.pack(fill=tk.X, anchor="w")

        ttk.Label(f_form, text="Jumlah Data Uji:").grid(row=0, column=0, sticky="w")
        ent_sample = ttk.Entry(f_form, width=10)
        ent_sample.grid(row=0, column=1, padx=5)
        ent_sample.insert(0, "1000")

        lbl_res = ttk.Label(self.content_frame, text="Status Sorting:\nSilakan pilih metode di bawah untuk memulai pengujian.", font=("Arial", 9), relief=tk.SOLID, padding=8)
        lbl_res.pack(fill=tk.X, anchor="w", pady=10)

        def _make_sample(sample_size):
            sample_arr = DynamicArray(sample_size)
            limit = min(sample_size, self.arr_pesanan.size)
            for i in range(limit):
                sample_arr.append(self.arr_pesanan.get(i))
            return sample_arr

        def run_insertion():
            try:
                n = int(ent_sample.get())
                sample = _make_sample(n)
                start = time.time()
                insertion_sort(sample, col_idx=4, is_numeric=True)
                elapsed = (time.time() - start) * 1000
                lbl_res.config(text=f"Insertion Sort Selesai!\nJumlah Data: {sample.size:,} | Waktu Eksekusi: {elapsed:.2f} ms\nData Teratas: {sample.get(0)}")
                self.log_command(f"Insertion Sort ({sample.size:,} data)", "M3 - InsertionSort", elapsed)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal Insertion Sort: {e}")

        def run_merge():
            try:
                n = int(ent_sample.get())
                sample = _make_sample(n)
                start = time.time()
                merge_sort(sample, col_idx=4, is_numeric=True)
                elapsed = (time.time() - start) * 1000
                lbl_res.config(text=f"Merge Sort Selesai!\nJumlah Data: {sample.size:,} | Waktu Eksekusi: {elapsed:.2f} ms\nData Teratas: {sample.get(0)}")
                self.log_command(f"Merge Sort ({sample.size:,} data)", "M3 - MergeSort", elapsed)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal Merge Sort: {e}")

        f_btns = ttk.Frame(self.content_frame)
        f_btns.pack(anchor="w", pady=5)
        ttk.Button(f_btns, text="Jalankan Insertion Sort O(n^2)", command=run_insertion).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(f_btns, text="Jalankan Merge Sort O(n log n)", command=run_merge).pack(side=tk.LEFT)


def launch_app():
    root = tk.Tk()
    app = EZ4UApp(root)
    root.mainloop()