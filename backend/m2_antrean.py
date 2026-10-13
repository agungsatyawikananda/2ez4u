# backend/m2_antrean.py

class Stack:
    """Struktur Data Stack (LIFO) buatan sendiri"""
    def __init__(self, initial_capacity=10):
        self.capacity = initial_capacity
        self.data = [None] * self.capacity
        self.top = -1

    def is_empty(self):
        return self.top == -1

    def is_full(self):
        return self.top == self.capacity - 1

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.top + 1):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def push(self, item):
        if self.is_full():
            self._resize(self.capacity * 2)
        self.top += 1
        self.data[self.top] = item

    def pop(self):
        if self.is_empty():
            return None
        item = self.data[self.top]
        self.data[self.top] = None
        self.top -= 1
        return item

    def peek(self):
        if self.is_empty():
            return None
        return self.data[self.top]

    def size(self):
        return self.top + 1


# =============================================================
# 1. MESIN KASIR: STRUK INFIX KE POSTFIX & EVALUASI
# =============================================================

def tokenisasi(ekspresi):
    tokens = []
    i = 0
    n = len(ekspresi)
    while i < n:
        ch = ekspresi[i]
        if ch == ' ':
            i += 1
            continue
        if ch in "0123456789":
            num = ""
            while i < n and ekspresi[i] in "0123456789":
                num += ekspresi[i]
                i += 1
            tokens.append(num)
        else:
            tokens.append(ch)
            i += 1
    return tokens


def prioritas_op(op):
    if op in ('*', '/'):
        return 2
    if op in ('+', '-'):
        return 1
    return 0


def ke_postfix(ekspresi):
    tokens = tokenisasi(ekspresi)
    stack_op = Stack()
    postfix = []

    for token in tokens:
        if token.isdigit():
            postfix.append(token)
        elif token == '(':
            stack_op.push(token)
        elif token == ')':
            while not stack_op.is_empty() and stack_op.peek() != '(':
                postfix.append(stack_op.pop())
            if not stack_op.is_empty() and stack_op.peek() == '(':
                stack_op.pop()
        elif token in ('+', '-', '*', '/'):
            while (not stack_op.is_empty() and 
                   stack_op.peek() != '(' and 
                   prioritas_op(stack_op.peek()) >= prioritas_op(token)):
                postfix.append(stack_op.pop())
            stack_op.push(token)

    while not stack_op.is_empty():
        postfix.append(stack_op.pop())

    return postfix


def hitung(postfix):
    stack_val = Stack()
    for token in postfix:
        if token.isdigit():
            stack_val.push(int(token))
        elif token in ('+', '-', '*', '/'):
            b = stack_val.pop()  # Operand kanan (urutan pop penting!)
            a = stack_val.pop()  # Operand kiri
            if a is None or b is None:
                continue
            if token == '+':
                res = a + b
            elif token == '-':
                res = a - b
            elif token == '*':
                res = a * b
            elif token == '/':
                res = a // b if b != 0 else 0
            stack_val.push(res)

    return stack_val.pop()


# =============================================================
# 2. FITUR QUEUE: NAIF VS MELINGKAR
# =============================================================

class AntreanNaif:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.count = 0
        self.total_geseran = 0

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.count):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def enqueue(self, item):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.count] = item
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        item = self.data[0]
        for i in range(1, self.count):
            self.data[i - 1] = self.data[i]
            self.total_geseran += 1
        self.data[self.count - 1] = None
        self.count -= 1
        return item

    def size(self):
        return self.count


class AntreanMelingkar:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.data = [None] * self.capacity
        self.front = 0
        self.rear = -1
        self.count = 0

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.capacity]
        self.data = new_data
        self.front = 0
        self.rear = self.count - 1
        self.capacity = new_capacity

    def enqueue(self, item):
        if self.count == self.capacity:
            self._resize(self.capacity * 2)
        self.rear = (self.rear + 1) % self.capacity
        self.data[self.rear] = item
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        item = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item

    def size(self):
        return self.count


# =============================================================
# 3. MANAJER UNDO / REDO & STATISTIK (POIN 8 & 9)
# =============================================================

class ManajerUndoRedo:
    def __init__(self, q_naif: AntreanNaif, q_circular: AntreanMelingkar):
        self.q_naif = q_naif
        self.q_circular = q_circular
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def catat_aksi(self, jenis_aksi, data):
        self.redo_stack = Stack()  # Mengosongkan redo
        self.undo_stack.push((jenis_aksi, data))

    def undo_last(self):
        if self.undo_stack.is_empty():
            return None
        aksi = self.undo_stack.pop()
        self.redo_stack.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo_stack.is_empty():
            return None
        aksi = self.redo_stack.pop()
        self.undo_stack.push(aksi)
        return aksi

    def stats(self):
        """Memenuhi Rekomendasi Poin 9"""
        return {
            "queue_len_naif": self.q_naif.size(),
            "queue_len_circular": self.q_circular.size(),
            "queue_capacity_naif": self.q_naif.capacity,
            "queue_capacity_circular": self.q_circular.capacity,
            "total_geseran": self.q_naif.total_geseran,
            "undo_depth": self.undo_stack.size(),
            "redo_depth": self.redo_stack.size()
        }