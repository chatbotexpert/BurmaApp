try:
    with open('log_final.txt', 'rb') as f:
        data = f.read(2000)
        print(f"Read {len(data)} bytes")
        print(repr(data))
except Exception as e:
    print(f"Error: {e}")
