import simhash as sh
from datasketch import MinHash, MinHashLSH


s1 = '我爱韩燕芳'
s2 = '韩燕芳，我爱你'

set1 = {'minhash', 'is', 'a', 'probabilistic', 'data', 'structure', 'for',
        'estimating', 'the', 'similarity', 'between', 'datasets'}
set2 = {'minhash', 'is', 'a', 'probability', 'data', 'structure', 'for',
        'estimating', 'the', 'similarity', 'between', 'documents'}
set3 = {'minhash', 'is', 'probability', 'data', 'structure', 'for',
        'estimating', 'the', 'similarity', 'between', 'documents'}

m1 = MinHash(num_perm=128)
m2 = MinHash(num_perm=128)
m3 = MinHash(num_perm=128)
for d in set1:
    m1.update(d.encode('utf8'))
for d in set2:
    m2.update(d.encode('utf8'))
for d in set3:
    m3.update(d.encode('utf8'))

# Create LSH index
lsh = MinHashLSH(threshold=0.5, num_perm=128)
lsh.insert("m2", m2)
lsh.insert("m3", m3)
result = lsh.query(m1)
print("Approximate neighbours with Jaccard similarity > 0.5", result)


def djb_hash(s):
    import ctypes
    seed = 5381
    for i in s:
        seed = ((seed << 5) + seed) + ord(i)
    return ctypes.c_long(seed).value


def convert_n_bytes(n, b):
    bits = b * 8
    return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)


def convert_4_bytes(n):
    return convert_n_bytes(n, 4)


def get_hashcode(s):
    h = 0
    n = len(s)
    for i, c in enumerate(s):
        h = h + ord(c) * 31 ** (n - 1 - i)
    return convert_4_bytes(h)


print(sh.Simhash(s1).distance(sh.Simhash(s2)))
print(sh.Simhash(s1).value)
print(sh.Simhash(s2).value)
print(djb_hash(s1))
print(djb_hash(s2))
print(get_hashcode(s1))
print(get_hashcode(s2))
