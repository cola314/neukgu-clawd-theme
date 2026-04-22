import sys
with open(sys.argv[1], 'rb') as f:
    raw = f.read(30)
print('first bytes:', raw.hex())
print('has BOM?', raw[:3] == b'\xef\xbb\xbf')
print('ASCII preview:', raw[:30])
