class LinkLoader:
    def __init__(self, objects):
        self.objects = objects
        
    def create_table(self, schema_name, connection):
        object_name = ""
        for obj in self.objects:
            object_name += "_" + obj

        table_name = "l" + object_name

        hash_key_name = object_name[1:] + "_hk"

        linked_object_keys = ""
        for obj in self.objects:
            linked_object_keys += f"{obj + "_hk"} VARCHAR(64),\n"

        ddl = f'''
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
            {hash_key_name} VARCHAR(64),
            {linked_object_keys}
            load_date TIMESTAMP,
            source VARCHAR(100)
        );
        '''
        
        cursor = connection.cursor()
        cursor.execute(ddl)
        connection.commit()

    def load_core(self, stg_schema_name, core_schema_name, connection):    
        object_name = ""
        objecst_hk_list = ""

        for obj in self.objects:
            object_name += "_" + obj
            objecst_hk_list += obj + "_hk,\n"
        
        table_name = "l" + object_name
        hash_key_name = object_name[1:] + "_hk"

        sql = f'''
        INSERT INTO {core_schema_name}.{table_name}
        SELECT
            stg.{hash_key_name},
            {objecst_hk_list}
            stg.load_date,
            stg.source
        FROM (
            select *, 
                row_number() over (partition by {hash_key_name} order by load_date desc) as rn
            FROM {stg_schema_name}.{table_name} 
        ) stg        
        WHERE stg.rn = 1 AND NOT EXISTS (
            SELECT 1
            FROM {core_schema_name}.{table_name} core
            WHERE stg.{hash_key_name} = core.{hash_key_name}
        );
        '''
        
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()