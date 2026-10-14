# backend/m3_laporan.py

def _clean_str(s):
    """Membersihkan spasi, tanda kutip, dan menyamakan ke huruf kecil."""
    if not s:
        return ""
    return str(s).strip().strip('"').strip("'").lower()


def _extract_id_num(s):
    """Mengekstrak angka ID dari string (misal: 'ORD-15000' -> 15000)."""
    if not s:
        return None
    digits = "".join([ch for ch in str(s) if ch.isdigit()])
    return int(digits) if digits else None


# =============================================================
# 1. ALGORITMA PENCARIAN (SEARCHING) MANUAL
# =============================================================

def linear_search(data_array, target, col_idx=0):
    """
    Pencarian Linier - O(n)
    Mencari target secara fleksibel (pencocokan angka ID, string kolom, atau baris).
    """
    target_clean = _clean_str(target)
    target_num = _extract_id_num(target)

    for i in range(data_array.size):
        row = data_array.get(i)
        if not row:
            continue

        cols = row.split(',')
        if len(cols) > col_idx:
            val_col = _clean_str(cols[col_idx])
            val_num = _extract_id_num(cols[col_idx])

            if target_num is not None and val_num is not None and target_num == val_num:
                return i

            if val_col == target_clean:
                return i

        row_clean = _clean_str(row)
        if target_clean in row_clean:
            return i

    return -1


def binary_search(data_array, target, col_idx=0):
    """
    Pencarian Biner - O(log n)
    Syarat: Data terurut berdasarkan Order ID.
    Pembandingan dilakukan berbasis angka ID agar presisi.
    """
    target_num = _extract_id_num(target)
    target_clean = _clean_str(target)

    low = 0
    high = data_array.size - 1

    while low <= high:
        mid = (low + high) // 2
        row = data_array.get(mid)
        if not row:
            break

        cols = row.split(',')
        if col_idx >= len(cols):
            break

        val_raw = cols[col_idx]
        val_clean = _clean_str(val_raw)
        val_num = _extract_id_num(val_raw)

        if (target_num is not None and val_num is not None and target_num == val_num) or (val_clean == target_clean):
            return mid

        if target_num is not None and val_num is not None:
            if val_num < target_num:
                low = mid + 1
            else:
                high = mid - 1
        else:
            if val_clean < target_clean:
                low = mid + 1
            else:
                high = mid - 1

    return -1


# =============================================================
# 2. ALGORITMA PENGURUTAN (SORTING) MANUAL
# =============================================================

def _get_sort_key(row, col_idx, is_numeric=False):
    if not row:
        return 0.0 if is_numeric else ""
    cols = row.split(',')
    if col_idx < len(cols):
        val = _clean_str(cols[col_idx])
        if is_numeric:
            try:
                return float(val)
            except ValueError:
                num = _extract_id_num(val)
                return float(num) if num is not None else 0.0
        return val
    return 0.0 if is_numeric else ""


def insertion_sort(data_array, col_idx=4, is_numeric=True):
    """
    Insertion Sort Manual - O(n^2)
    Menyisipkan elemen ke posisi terurut secara bertahap.
    """
    n = data_array.size
    for i in range(1, n):
        key_item = data_array.data[i]
        key_val = _get_sort_key(key_item, col_idx, is_numeric)
        j = i - 1
        while j >= 0 and _get_sort_key(data_array.data[j], col_idx, is_numeric) > key_val:
            data_array.data[j + 1] = data_array.data[j]
            j -= 1
        data_array.data[j + 1] = key_item


def merge_sort(data_array, col_idx=4, is_numeric=True):
    """
    Merge Sort Manual - O(n log n)
    Pengurutan berbasis Divide and Conquer (rekursif membagi dua dan menggabungkan sub-array).
    """
    def _merge_sort_rec(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left_half = [arr[i] for i in range(mid)]
        right_half = [arr[i] for i in range(mid, len(arr))]

        left_sorted = _merge_sort_rec(left_half)
        right_sorted = _merge_sort_rec(right_half)

        # Proses Penggabungan (Merge)
        merged = [None] * len(arr)
        i = j = k = 0

        while i < len(left_sorted) and j < len(right_sorted):
            key_a = _get_sort_key(left_sorted[i], col_idx, is_numeric)
            key_b = _get_sort_key(right_sorted[j], col_idx, is_numeric)
            if key_a <= key_b:
                merged[k] = left_sorted[i]
                i += 1
            else:
                merged[k] = right_sorted[j]
                j += 1
            k += 1

        while i < len(left_sorted):
            merged[k] = left_sorted[i]
            i += 1
            k += 1

        while j < len(right_sorted):
            merged[k] = right_sorted[j]
            j += 1
            k += 1

        return merged

    if data_array.size > 1:
        raw_items = [data_array.data[i] for i in range(data_array.size)]
        sorted_items = _merge_sort_rec(raw_items)
        for i in range(data_array.size):
            data_array.data[i] = sorted_items[i]