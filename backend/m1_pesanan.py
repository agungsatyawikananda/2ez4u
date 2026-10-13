class Pesanan:
    """Kelas untuk menyimpan atribut data pesanan."""

    def __init__(
        self,
        oid,
        pelanggan,
        resto,
        menu,
        harga,
        prioritas,
        t_masuk_detik=0,
        t_selesai_detik=None,
        status="ANTRE",
    ):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas  # 1: VIP, 2: PRIORITAS, 3: REGULER
        self.t_masuk_detik = t_masuk_detik
        self.t_selesai_detik = t_selesai_detik
        self.status = status

    def __repr__(self):
        return f"<Pesanan {self.oid} | {self.pelanggan} | {self.resto} | P:{self.prioritas}>"


class DynamicArray:
    """Implementasi Dynamic Array buatan sendiri dengan perbesaran kapasitas 2x (Amortized O(1))."""

    def __init__(self, capacity=4):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _resize(self, new_capacity):
        """Alokasi memori baru berukuran 2x lipat dan salin data lama."""
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def get(self, index):
        """Lihat pesanan ke-i (Kompleksitas O(1))."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[index]

    def append(self, val):
        """Tambah REGULER: Masuk paling belakang (Amortized O(1))."""
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = val
        self.size += 1

    def prepend(self, val):
        """Tambah VIP: Masuk paling depan / index 0 (Kompleksitas O(n))."""
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i - 1]
        self.data[0] = val
        self.size += 1

    def insert(self, index, val):
        """Tambah PRIORITAS: Masuk ke posisi tengah (Kompleksitas O(n))."""
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
        self.data[index] = val
        self.size += 1

    def delete(self, index):
        """Hapus pesanan ke-i (Kompleksitas O(n))."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        removed_item = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        return removed_item

    def __len__(self):
        return self.size


class Node:
    """Simpul untuk Linked List."""

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    """Implementasi Singly Linked List dengan pointer head & tail."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get(self, index):
        """Lihat pesanan ke-i (Kompleksitas O(n))."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        curr = self.head
        for _ in range(index):
            curr = curr.next
        return curr.data

    def append(self, val):
        """Tambah REGULER: Masuk paling belakang via tail pointer (Kompleksitas O(1))."""
        new_node = Node(val)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def prepend(self, val):
        """Tambah VIP: Masuk paling depan (Kompleksitas O(1))."""
        new_node = Node(val)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def insert(self, index, val):
        """Tambah PRIORITAS: Masuk ke posisi tengah (Kompleksitas O(n))."""
        if index < 0 or index > self.size:
            raise IndexError("Indeks di luar jangkauan")
        if index == 0:
            self.prepend(val)
            return
        if index == self.size:
            self.append(val)
            return

        new_node = Node(val)
        curr = self.head
        for _ in range(index - 1):
            curr = curr.next

        new_node.next = curr.next
        curr.next = new_node
        self.size += 1

    def delete(self, index):
        """Hapus pesanan ke-i (Kompleksitas O(n))."""
        if index < 0 or index >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        if index == 0:
            removed_data = self.head.data
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return removed_data

        curr = self.head
        for _ in range(index - 1):
            curr = curr.next

        removed_data = curr.next.data
        curr.next = curr.next.next
        if curr.next is None:
            self.tail = curr
        self.size -= 1
        return removed_data

    def __len__(self):
        return self.size


def muat_data_pesanan(filepath, limit=None):
    """Membaca file pesanan.csv dan mengembalikan DynamicArray dan LinkedList."""
    arr = DynamicArray()
    ll = LinkedList()

    with open(filepath, "r", encoding="utf-8") as f:
        header = f.readline()  # Lewati baris header CSV
        count = 0
        for line in f:
            if limit and count >= limit:
                break
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) >= 8:
                oid = parts[0]
                pelanggan = parts[1]
                resto = parts[2]
                menu = parts[3]
                harga = int(parts[4])
                prioritas = int(parts[5])
                t_masuk = int(parts[6])
                t_selesai = int(parts[7]) if parts[7] else None
                status = parts[8] if len(parts) > 8 else "ANTRE"

                p = Pesanan(
                    oid,
                    pelanggan,
                    resto,
                    menu,
                    harga,
                    prioritas,
                    t_masuk,
                    t_selesai,
                    status,
                )

                arr.append(p)
                ll.append(p)
                count += 1

    return arr, ll

def muat_data_pesanan(filepath, limit=None):
    """Membaca file pesanan.csv dan mengembalikan DynamicArray dan LinkedList."""
    arr = DynamicArray()
    ll = LinkedList()

    with open(filepath, "r", encoding="utf-8") as f:
        header = f.readline()  # Lewati baris header CSV
        count = 0
        for line in f:
            if limit and count >= limit:
                break
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            # Menggunakan indeks dari belakang (indeks negatif) agar aman dari
            # nama pelanggan yang mengandung tanda koma (gelar/nama).
            if len(parts) >= 9:
                oid = parts[0].strip()
                pelanggan = ",".join(parts[1:-7]).strip()
                resto = parts[-7].strip()
                menu = parts[-6].strip()
                harga = int(parts[-5].strip())
                prioritas = int(parts[-4].strip())
                t_masuk = int(parts[-3].strip())
                t_selesai_raw = parts[-2].strip()
                t_selesai = int(t_selesai_raw) if t_selesai_raw else None
                status = parts[-1].strip()

                p = Pesanan(
                    oid,
                    pelanggan,
                    resto,
                    menu,
                    harga,
                    prioritas,
                    t_masuk,
                    t_selesai,
                    status,
                )

                arr.append(p)
                ll.append(p)
                count += 1

    return arr, ll