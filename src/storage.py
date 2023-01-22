import shutil

def storage_used():
    total, used, free = shutil.disk_usage("./")
    return total, used, free
