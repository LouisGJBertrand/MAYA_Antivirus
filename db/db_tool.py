
import hashlib
import os

def CalculateMD5(filepath):
    f = open(filepath,'rb')
    m = hashlib.md5()
    while True:
        ## Don't read the entire file at once...
        data = f.read(10240)
        if len(data) == 0:
            break
        m.update(data)
    return m.hexdigest()

dir_path = os.path.dirname(os.path.realpath(__file__))

db_file_path = dir_path + "\\malware_db.json"
hash_file_path = dir_path + "\\malware_db.json.md5"

hash_file = open(hash_file_path, 'wb')

hash_file.write(CalculateMD5(db_file_path).encode())