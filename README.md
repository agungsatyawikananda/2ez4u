# 2EZ4U Project Struktur Data & Analisa Algoritma
Anak Agung Ngurah Agung Satya Wikananda Kepakisan - 5024251007 - Departemen Teknik Komputer

## Deskripsi 
Proyek ini adalah sebuah aplikasi sistem pemrosesan data pesanan untuk layanan pengiriman makanan dan barang. Proyek ini berfokus pada implementasi dan evaluasi performa struktur data linier dalam mengelola alur transaksi berskala besar secara efisien.

## Cara Menjalankan
```bash
py app.py
```
## Diagram
[ Data Layer ] ──> [ Backend Layer ] ──> [ Frontend Layer ]
 pesanan.csv         m1_pesanan.py           app.py (CLI / GUI)
 peta.csv            (DynamicArray & 
                      LinkedList)
                      
## M1 Data Pesanan, Array vs Linked List
Milestone ini bertujuan untuk mengelola daftar pesanan berdasarkan tingkatan prioritas (REGULER, PRIORITAS, dan VIP) menggunakan dua pendekatan struktur data Dynamic Array dan Linked List

| Operasi | Dynamic Array | Linked List | Analisis Ringkas |
| :--- | :--- | :--- | :--- |
| **Akses Indeks (Get)** | **0.001 ms** | 0.045 ms | Array unggul karena akses memori langsung O(1), Linked List butuh traversal O(n). |
| **Tambah REGULER (Belakang)** | 0.020 ms | **0.010 ms** | Sama-sama cepat (O(1) amortized pada Array vs O(1) pointer tail pada Linked List). |
| **Tambah PRIORITAS (Tengah)** | 1.850 ms | **1.100 ms** | Keduanya O(n) karena butuh pencarian atau pergeseran elemen. |
| **Tambah VIP (Depan)** | 0.622 ms | **0.008 ms** | Linked List jauh lebih cepat (O(1)) karena Array wajib menggeser semua elemen (O(n)). |
| **Hapus Pesanan (ke-i)** | 1.200 ms | **0.950 ms** | Keduanya O(n) untuk penyesuaian posisi sisa elemen. |

## Struktur Folder
```text
2ez4u/
├── app.py
├── README.md
├── data/
│   ├── pesanan.csv
│   └── peta.csv
├── backend/
│   └── m1_pesanan.py
└── frontend/
    └── ui.py
```