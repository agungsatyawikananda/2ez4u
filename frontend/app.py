import sys
import time

# Agar folder backend bisa dibaca oleh python
sys.path.append("backend")
from m1_pesanan import Pesanan, muat_data_pesanan

print("=== MEMUAT DATA PESANAN ===")
start = time.time()
# Mencoba muat 10.000 data pertama dulu untuk tes
array_pesanan, list_pesanan = muat_data_pesanan("data/pesanan.csv", limit=10000)
end = time.time()
print(
    f"Selesai muat {len(array_pesanan)} data dalam {end - start:.4f} detik.\n"
)

# Pesanan uji baru
p_vip = Pesanan("O-999999", "Budi", "Kafe-Teknik", "Kopi", 15000, 1)

print("=== UJI TAMBAH PESANAN VIP (DI DEPAN) ===")
# 1. Tes di Array
t0 = time.time()
array_pesanan.prepend(p_vip)
t1 = time.time()
print(f"Array Prepend (VIP)      : {(t1 - t0) * 1000:.4f} ms")

# 2. Tes di Linked List
t0 = time.time()
list_pesanan.prepend(p_vip)
t1 = time.time()
print(f"Linked List Prepend (VIP): {(t1 - t0) * 1000:.4f} ms")