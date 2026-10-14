# backend/m1_pesanan.py

class DynamicArray:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * self.capacity

    def _resize(self, new_cap):
        new_data = [None] * new_cap
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_cap

    def append(self, val):  # REGULER - O(1)
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = val
        self.size += 1

    def prepend(self, val):  # VIP - O(n)
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i - 1]
        self.data[0] = val
        self.size += 1

    def insert(self, idx, val):  # PRIORITAS - O(n)
        if idx < 0 or idx > self.size:
            return
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, idx, -1):
            self.data[i] = self.data[i - 1]
        self.data[idx] = val
        self.size += 1

    def get(self, idx):  # O(1)
        if 0 <= idx < self.size:
            return self.data[idx]
        return None

    def delete(self, idx):  # O(n)
        if idx < 0 or idx >= self.size:
            return None
        val = self.data[idx]
        for i in range(idx, self.size - 1):
            self.data[i] = self.data[i + 1]
        self.data[self.size - 1] = None
        self.size -= 1
        return val


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def prepend(self, val):  # VIP - O(1)
        node = Node(val)
        node.next = self.head
        self.head = node
        if not self.tail:
            self.tail = node
        self.size += 1

    def append(self, val):  # REGULER - O(1)
        node = Node(val)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def insert(self, idx, val):  # PRIORITAS - O(n)
        if idx <= 0:
            return self.prepend(val)
        if idx >= self.size:
            return self.append(val)
        
        node = Node(val)
        curr = self.head
        for _ in range(idx - 1):
            curr = curr.next
        node.next = curr.next
        curr.next = node
        self.size += 1

    def get(self, idx):  # O(n)
        if idx < 0 or idx >= self.size:
            return None
        curr = self.head
        for _ in range(idx):
            curr = curr.next
        return curr.data

    def delete(self, idx):  # O(n)
        if idx < 0 or idx >= self.size or not self.head:
            return None
        
        if idx == 0:
            val = self.head.data
            self.head = self.head.next
            if not self.head:
                self.tail = None
            self.size -= 1
            return val

        curr = self.head
        for _ in range(idx - 1):
            curr = curr.next
        val = curr.next.data
        if curr.next == self.tail:
            self.tail = curr
        curr.next = curr.next.next
        self.size -= 1
        return val