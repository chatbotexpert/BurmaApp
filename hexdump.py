import sys
import binascii

try:
    filename = sys.argv[1]
    with open(filename, 'rb') as f:
        content = f.read(500)
    print(binascii.hexlify(content).decode('ascii'))
except Exception as e:
    print(f"Error: {e}")
