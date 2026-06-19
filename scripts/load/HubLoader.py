class HubLoader:
    def __init__(self, object_name, business_key):
        self.object_name = object_name
        self.business_key = business_key
        
    def create_table(self, schema_name, connection):
        table_name = "h_" + self.object_name
        hash_key_name = self.object_name + "_hk"

        business_key_columns = ""
        for key in self.business_key:
            business_key_columns += f"{key["name"]} {key["type"]},\n"

        ddl = f'''
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
            {hash_key_name} VARCHAR(64),
            {business_key_columns}
            load_date TIMESTAMP,
            source VARCHAR(100)
        );
        '''
        
        cursor = connection.cursor()
        cursor.execute(ddl)
        connection.commit()

    def load_core(self, stg_schema_name, core_schema_name, connection):
        table_name = "h_" + self.object_name
        hash_key_name = self.object_name + "_hk"

        business_key_attrs = ""
        for key in self.business_key:
            business_key_attrs += f"stg.{key["name"]},\n"

        sql = f'''
        INSERT INTO {core_schema_name}.{table_name}
        SELECT
            stg.{hash_key_name},
            {business_key_attrs}
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
