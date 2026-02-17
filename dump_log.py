try:
    with open('log_final.txt', 'rb') as f:
        data = f.read()
        try:
            print(data.decode('utf-16'))
        except:
             print(data.decode('utf-8', errors='ignore'))
except Exception as e:
    print(f"Error reading log: {e}")
