import hashlib
from datetime import datetime


class Link():
    def __init__(self, linked_objects, source):
        self.linked_objects = linked_objects
        self.source = source
        self.load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hash_key = self.get_hash_key()
    
    def get_hash_key(self):
        concat_main_business_key = ""

        for obj in self.linked_objects:
            concat_business_key = ""

            for value in obj["business_key"].values():
                concat_main_business_key += str(value)
                concat_business_key += str(value)

            obj["hash_key"] = hashlib.sha256(concat_business_key.encode('utf-8')).hexdigest() 

        return hashlib.sha256(concat_main_business_key.encode('utf-8')).hexdigest() 
    
    def convert_to_dict(self):
        row = {}

        hash_key_name = ""

        for obj in self.linked_objects:
            hash_key_name += obj["name"] + "_"

        hash_key_name += "hk"
        row[hash_key_name] = self.hash_key

        for obj in self.linked_objects:
            object_hash_key_name = obj["name"] + "_hk"
            row[object_hash_key_name] = obj["hash_key"]

        row["load_date"] = self.load_date
        row["record_source"] = self.source
        
        return row