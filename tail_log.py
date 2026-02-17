try:
    with open('log_reuters_2.txt', 'rb') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 4000))
        data = f.read()
        # Try utf-16 first (default regarding previous logs), then utf-8
        try:
            print(data.decode('utf-16'))
        except:
             print(data.decode('utf-8', errors='ignore'))
except Exception as e:
    print(f"Error reading log: {e}")
