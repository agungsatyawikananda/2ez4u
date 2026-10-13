# app.py
from backend.m2_antrean import (
    ke_postfix, hitung, 
    AntreanNaif, AntreanMelingkar, 
    ManajerUndoRedo
)

def run_m2_tests():
    print("==================================================")
    print("           2EZ4U ENGINE - MILESTONE 2             ")
    print("==================================================")

    # 1. Modul Kasir (Infix -> Postfix -> Evaluasi)
    print("\n[1] METODE KASIR & POSTFIX")
    contoh_struk = [
        "10000 + 5000 - 2000",
        "(3 * 12000) + (2 * 8500) - 5000",
        "((20000 - 5000) / 3) + 1000"
    ]
    for expr in contoh_struk:
        postfix = ke_postfix(expr)
        total = hitung(postfix)
        print(f"  Infix   : {expr}")
        print(f"  Postfix : {' '.join(postfix)}")
        print(f"  Total   : Rp {total:,}\n")

    # 2. Pengujian Antrean (Naif vs Circular)
    print("[2] ANTREAN (NAIF VS CIRCULAR)")
    q_kecil = AntreanMelingkar(capacity=4)
    q_kecil.enqueue("ORD-001")
    q_kecil.enqueue("ORD-002")
    q_kecil.enqueue("ORD-003")
    print(f"  Enqueue 3 data -> Size: {q_kecil.size()}")
    print(f"  Dequeue 2 data -> Out: {q_kecil.dequeue()}, {q_kecil.dequeue()}")
    
    # Putar pointer
    q_kecil.enqueue("ORD-004")
    q_kecil.enqueue("ORD-005")
    q_kecil.enqueue("ORD-006")
    print(f"  Enqueue 3 data lagi (Pointer Wrap-around) -> Front: {q_kecil.front}, Rear: {q_kecil.rear}")

    # 3. Manajer Undo / Redo & Stats
    print("\n[3] UNDO / REDO & STATISTIK")
    q_naif = AntreanNaif(1000)
    q_circ = AntreanMelingkar(1000)
    manager = ManajerUndoRedo(q_naif, q_circ)

    # Simulasi transaksi
    q_naif.enqueue("ORD-101")
    q_circ.enqueue("ORD-101")
    manager.catat_aksi("ENQUEUE", "ORD-101")

    q_naif.dequeue()
    q_circ.dequeue()
    manager.catat_aksi("DEQUEUE", "ORD-101")

    # Ambil statistik sistem
    stats = manager.stats()
    print("  System Stats:")
    for key, val in stats.items():
        print(f"    {key}: {val}")

    print("\n==================================================")
    print("Execution finished.")
    print("==================================================")


if __name__ == "__main__":
    run_m2_tests()