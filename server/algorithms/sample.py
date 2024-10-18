# Each algorithm should be in a file like this, any number of subdiretories or other files can be added, 
# but this root file with a proc_call function must be present.
# This function with these parameters is required from all algorithms for them to be called consistently within the worker.
def proc_call(token, store_path, out_path):
    print(f"Successful proc call {token}")
    with open(out_path, "w+") as f:
        f.write(token)
    