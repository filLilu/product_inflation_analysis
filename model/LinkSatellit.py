import hashlib
from datetime import datetime


class LinkSatellit():
    def __init__(self, linked_objects, descriptive_attributes, source):
        self.linked_objects = linked_objects
        self.descriptive_attributes = descriptive_attributes
        self.source = source
        self.load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hash_key = self.get_hash_key()
    
    def get_hash_key(self):
        concat_main_business_key = ""

        for obj in self.linked_objects:
            for value in obj["business_key"].values():
                concat_main_business_key += str(value)

        return hashlib.sha256(concat_main_business_key.encode('utf-8')).hexdigest() 
    
    def convert_to_dict(self):
        row = {}

        hash_key_name = ""

        for obj in self.linked_objects:
            hash_key_name += obj["name"] + "_"

        hash_key_name += "hk"
        row[hash_key_name] = self.hash_key

        for key, value in self.descriptive_attributes.items():
            row[key] = value

        row["load_date"] = self.load_date
        row["record_source"] = self.source
        
        return row