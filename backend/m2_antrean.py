# backend/m2_antrean.py

class Stack:
    def __init__(self, cap=10):
        self.cap = cap
        self.data = [None] * self.cap
        self.top = -1

    def is_empty(self): return self.top == -1
    def size(self): return self.top + 1

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.top + 1):
            new_data[i] = self.data[i]
        self.data = new_data
        self.cap = new_cap

    def push(self, val):
        if self.top == self.cap - 1:
            self._resize(self.cap * 2)
        self.top += 1
        self.data[self.top] = val

    def pop(self):
        if self.is_empty(): return None
        val = self.data[self.top]
        self.data[self.top] = None
        self.top -= 1
        return val

    def peek(self):
        return None if self.is_empty() else self.data[self.top]


# --- STRUK KASIR (POSTFIX) ---

def tokenisasi(expr):
    tokens, i, n = [], 0, len(expr)
    while i < n:
        if expr[i] == ' ':
            i += 1
        elif expr[i].isdigit():
            num = ""
            while i < n and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(num)
        else:
            tokens.append(expr[i])
            i += 1
    return tokens

def prioritas(op):
    return 2 if op in ('*', '/') else (1 if op in ('+', '-') else 0)

def ke_postfix(expr):
    tokens = tokenisasi(expr)
    st, pf = Stack(), []
    for t in tokens:
        if t.isdigit():
            pf.append(t)
        elif t == '(':
            st.push(t)
        elif t == ')':
            while not st.is_empty() and st.peek() != '(':
                pf.append(st.pop())
            st.pop()  # Pop '('
        else:
            while not st.is_empty() and st.peek() != '(' and prioritas(st.peek()) >= prioritas(t):
                pf.append(st.pop())
            st.push(t)
    while not st.is_empty():
        pf.append(st.pop())
    return pf

def hitung(postfix):
    st = Stack()
    for t in postfix:
        if t.isdigit():
            st.push(int(t))
        else:
            b, a = st.pop(), st.pop()
            if a is None or b is None: continue
            if t == '+': st.push(a + b)
            elif t == '-': st.push(a - b)
            elif t == '*': st.push(a * b)
            elif t == '/': st.push(a // b if b != 0 else 0)
    return st.pop()


# --- QUEUE NAIF VS CIRCULAR ---

class AntreanNaif:
    def __init__(self, cap=1000):
        self.cap = cap
        self.data = [None] * self.cap
        self.count = 0
        self.total_geseran = 0

    def size(self): return self.count

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.count):
            new_data[i] = self.data[i]
        self.data, self.cap = new_data, new_cap

    def enqueue(self, val):
        if self.count == self.cap: self._resize(self.cap * 2)
        self.data[self.count] = val
        self.count += 1

    def enqueue_front(self, val):
        if self.count == self.cap: self._resize(self.cap * 2)
        for i in range(self.count, 0, -1):
            self.data[i] = self.data[i - 1]
            self.total_geseran += 1
        self.data[0] = val
        self.count += 1

    def dequeue(self):
        if self.count == 0: return None
        val = self.data[0]
        for i in range(1, self.count):
            self.data[i - 1] = self.data[i]
            self.total_geseran += 1
        self.data[self.count - 1] = None
        self.count -= 1
        return val

    def pop_back(self):
        if self.count == 0: return None
        val = self.data[self.count - 1]
        self.data[self.count - 1] = None
        self.count -= 1
        return val


class AntreanMelingkar:
    def __init__(self, cap=1000):
        self.cap = cap
        self.data = [None] * self.cap
        self.front, self.rear, self.count = 0, -1, 0

    def size(self): return self.count

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.count):
            new_data[i] = self.data[(self.front + i) % self.cap]
        self.data = new_data
        self.front, self.rear, self.cap = 0, self.count - 1, new_cap

    def enqueue(self, val):
        if self.count == self.cap: self._resize(self.cap * 2)
        self.rear = (self.rear + 1) % self.cap
        self.data[self.rear] = val
        self.count += 1

    def enqueue_front(self, val):
        if self.count == self.cap: self._resize(self.cap * 2)
        self.front = (self.front - 1 + self.cap) % self.cap
        self.data[self.front] = val
        self.count += 1

    def dequeue(self):
        if self.count == 0: return None
        val = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.cap
        self.count -= 1
        return val

    def pop_back(self):
        if self.count == 0: return None
        val = self.data[self.rear]
        self.data[self.rear] = None
        self.rear = (self.rear - 1 + self.cap) % self.cap
        self.count -= 1
        return val


# --- MANAJER UNDO / REDO ---

class ManajerUndoRedo:
    def __init__(self, q_naif, q_circular):
        self.q_naif, self.q_circular = q_naif, q_circular
        self.undo_st, self.redo_st = Stack(), Stack()

    def catat_aksi(self, jenis, data):
        self.redo_st = Stack()
        self.undo_st.push((jenis, data))

    def undo_last(self):
        if self.undo_st.is_empty(): return None
        aksi = self.undo_st.pop()
        jenis, data = aksi

        if jenis == "ENQUEUE":
            self.q_naif.pop_back()
            self.q_circular.pop_back()
        elif jenis == "DEQUEUE":
            self.q_naif.enqueue_front(data)
            self.q_circular.enqueue_front(data)

        self.redo_st.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo_st.is_empty(): return None
        aksi = self.redo_st.pop()
        jenis, data = aksi

        if jenis == "ENQUEUE":
            self.q_naif.enqueue(data)
            self.q_circular.enqueue(data)
        elif jenis == "DEQUEUE":
            self.q_naif.dequeue()
            self.q_circular.dequeue()

        self.undo_st.push(aksi)
        return aksi