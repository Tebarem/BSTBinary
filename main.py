import struct
import os
import timeit

class FileBSTNode:
    def __init__(self, index, email, left=None, right=None):
        self.index = index
        self.email = email
        self.left = left
        self.right = right

    def serialize(self):
        email_bytes = self.email.encode('utf-8')
        email_size = len(email_bytes)
        # Ensure email is fixed length, e.g., 256 bytes
        email_bytes = email_bytes.ljust(256, b'\0')

        return struct.pack('Q256sQQ', self.index, email_bytes, self.left or 0, self.right or 0)

    @staticmethod
    def deserialize(data):
        index, email_bytes, left, right = struct.unpack('Q256sQQ', data)
        email = email_bytes.rstrip(b'\0').decode('utf-8')
        left = left if left != 0 else None
        right = right if right != 0 else None
        return FileBSTNode(index, email, left, right)


class FileBST:
    NODE_SIZE = 280  # 8 (index) + 256 (email) + 8 (left) + 8 (right)

    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self.root_index = None
        self.next_index = 0

        if os.path.exists(data_file_path):
            self._load_metadata()
        else:
            # Create the file
            with open(data_file_path, 'w') as f:
                pass
            self._save_metadata()

    def _load_metadata(self):
        with open(self.data_file_path, 'rb') as f:
            f.seek(0)
            meta_data = f.read(16)
            self.root_index, self.next_index = struct.unpack('QQ', meta_data)

    def _save_metadata(self):
        with open(self.data_file_path, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('QQ', self.root_index or 0, self.next_index))

    def _write_node(self, node):
        with open(self.data_file_path, 'r+b') as f:
            f.seek(16 + node.index * self.NODE_SIZE)
            f.write(node.serialize())

    def _read_node(self, index):
        with open(self.data_file_path, 'rb') as f:
            f.seek(16 + index * self.NODE_SIZE)
            data = f.read(self.NODE_SIZE)
        return FileBSTNode.deserialize(data)

    def insert(self, email):
        if self.root_index is None:
            self.root_index = self.next_index
            self._write_node(FileBSTNode(self.next_index, email))
            self.next_index += 1
            self._save_metadata()
        else:
            self._insert(self.root_index, email)

    def _insert(self, current_index, email):
        current_node = self._read_node(current_index)
        if email < current_node.email:
            if current_node.left is None:
                current_node.left = self.next_index
                self._write_node(FileBSTNode(self.next_index, email))
                self.next_index += 1
            else:
                self._insert(current_node.left, email)
        else:
            if current_node.right is None:
                current_node.right = self.next_index
                self._write_node(FileBSTNode(self.next_index, email))
                self.next_index += 1
            else:
                self._insert(current_node.right, email)
        self._write_node(current_node)

    def search(self, email):
        return self._search(self.root_index, email)

    def _search(self, current_index, email):
        if current_index is None:
            return None
        current_node = self._read_node(current_index)
        if email == current_node.email:
            return current_node.index
        elif email < current_node.email:
            return self._search(current_node.left, email)
        else:
            return self._search(current_node.right, email)

    def traverse(self):
        self._traverse(self.root_index)

    def _traverse(self, current_index):
        if current_index is not None:
            current_node = self._read_node(current_index)
            self._traverse(current_node.left)
            print(f"Email: {current_node.email}, Index: {current_node.index}")
            self._traverse(current_node.right)


def read_mapping_index(data_file_path, index):
    with open(data_file_path, 'rb') as f:
        f.seek(16 + index * FileBST.NODE_SIZE)
        data = f.read(FileBST.NODE_SIZE)
    return FileBSTNode.deserialize(data).email


bst = FileBST('bst_data.bin')

""" with open('email_list.txt', 'r') as f:
    for email in f:
        bst.insert(email.strip()) """


""" index = bst.search('test@123.com')
print(f"The index for 'test@123.com' is {index}")

index = bst.search('example@456.com')
print(f"The index for 'example@456.com' is {index}")

index = bst.search('hello@world.com')
print(f"The index for 'hello@world.com' is {index}") """

#print(timeit.timeit('print(bst.search("Phillipcharming@gmx.de"))', globals=globals(), number=1) * 1000, 'ms')
print(timeit.timeit('print(read_mapping_index("bst_data.bin", 99992))', globals=globals(), number=1) * 1000, 'ms')
