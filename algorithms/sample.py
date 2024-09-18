def proc_call(token, store_path, out_path):
    print(f"Successful proc call {token}")
    with open(out_path, "w+") as f:
        f.write(token)
    