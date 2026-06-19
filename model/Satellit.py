import hashlib
from datetime import datetime


class Satellit():
    def __init__(self, object_name, business_key, descriptive_attributes, source):
        self.object_name = object_name
        self.business_key = business_key
        self.descriptive_attributes = descriptive_attributes
        self.source = source
        self.load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hash_key = self.get_hash_key()
    
    def get_hash_key(self):
        concat_business_key = ""

        for value in self.business_key.values():
            concat_business_key += str(value)

        return hashlib.sha256(concat_business_key.encode('utf-8')).hexdigest() 
    
    def convert_to_dict(self):
        row = {}

        hash_key_name = self.object_name + "_hk"
        row[hash_key_name] = self.hash_key

        for key, value in self.descriptive_attributes.items():
            row[key] = value

        row["load_date"] = self.load_date
        row["record_source"] = self.source
        
        return row