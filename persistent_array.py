#!/usr/bin/env python3
"""Persistent Array — immutable versioned array using path copying."""
import math

class PNode:
    __slots__ = ('children', 'value')
    def __init__(self, value=None, children=None):
        self.value = value; self.children = children or [None, None]

class PersistentArray:
    BITS = 5; WIDTH = 1 << BITS; MASK = WIDTH - 1
    
    def __init__(self, root=None, size=0):
        self.root = root; self.size = size
    
    @classmethod
    def from_list(cls, items):
        arr = cls()
        for item in items: arr = arr.append(item)
        return arr
    
    def get(self, index):
        if index < 0 or index >= self.size: raise IndexError(index)
        node = self.root; depth = self._depth()
        for level in range(depth * self.BITS, -1, -self.BITS):
            idx = (index >> level) & self.MASK
            if node is None: return None
            if level == 0: return node.children[idx] if idx < len(node.children) else None
            node = node.children[idx] if idx < len(node.children) else None
        return node.value if node else None
    
    def set(self, index, value):
        if index < 0 or index >= self.size: raise IndexError(index)
        new_root = self._set(self.root, self._depth() * self.BITS, index, value)
        return PersistentArray(new_root, self.size)
    
    def _set(self, node, level, index, value):
        node = PNode(children=list(node.children) if node else [None]*self.WIDTH)
        idx = (index >> level) & self.MASK
        if level == 0: 
            while len(node.children) <= idx: node.children.append(None)
            node.children[idx] = value
        else:
            while len(node.children) <= idx: node.children.append(None)
            node.children[idx] = self._set(node.children[idx], level - self.BITS, index, value)
        return node
    
    def append(self, value):
        new_size = self.size + 1
        depth = self._depth_for(new_size)
        root = self.root
        if self._depth() < depth:
            root = PNode(children=[root] + [None]*(self.WIDTH-1))
        new_root = self._set(root or PNode(), depth * self.BITS, self.size, value)
        return PersistentArray(new_root, new_size)
    
    def _depth(self): return self._depth_for(self.size)
    def _depth_for(self, n):
        if n <= self.WIDTH: return 0
        return int(math.ceil(math.log(n, self.WIDTH)))
    
    def to_list(self): return [self.get(i) for i in range(self.size)]

if __name__ == "__main__":
    v0 = PersistentArray.from_list([10, 20, 30, 40, 50])
    v1 = v0.set(2, 99)
    v2 = v1.append(60)
    print(f"v0: {v0.to_list()}")
    print(f"v1 (set [2]=99): {v1.to_list()}")
    print(f"v2 (append 60): {v2.to_list()}")
    print(f"v0 unchanged: {v0.to_list()}")
