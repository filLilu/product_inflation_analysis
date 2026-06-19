class LinkSatellitLoader:
    def __init__(self, objects, descriptive_attributes):
        self.objects = objects
        self.descriptive_attributes = descriptive_attributes
        
    def create_table(self, schema_name, connection):
        object_name = ""
        for obj in self.objects:
            object_name += "_" + obj

        table_name = "ls" + object_name
        hash_key_name = object_name[1:] + "_hk"

        descriptive_columns = ""
        for attr in self.descriptive_attributes:
            descriptive_columns += f"{attr["name"]} {attr["type"]},\n"

        ddl = f'''
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
            {hash_key_name} VARCHAR(64),
            {descriptive_columns}
            load_date TIMESTAMP,
            source VARCHAR(100)
        );
        '''
        
        cursor = connection.cursor()
        cursor.execute(ddl)
        connection.commit()

    def load_core(self, stg_schema_name, core_schema_name, connection):
        object_name = ""
        for obj in self.objects:
            object_name += "_" + obj

        table_name = "ls" + object_name
        hash_key_name = object_name[1:] + "_hk"

        descriptive_attributes_differ = "NOT (1=1\n"
        stg_descriptive_attributes = ""
        descriptive_attributes_names = ""
        for attr in self.descriptive_attributes:
            descriptive_attributes_differ += "AND stg." + attr["name"] + " = core." + attr["name"] + "\n"
            stg_descriptive_attributes += "stg." + attr["name"] + ",\n"
            descriptive_attributes_names += attr["name"] + ",\n"
        descriptive_attributes_differ += ")"

        create_new_sql = f'''
        CREATE TABLE {core_schema_name}.{table_name}_new AS
        SELECT 
            {hash_key_name},
            {descriptive_attributes_names}
            load_date,
            source
        FROM (
            SELECT *, row_number() over (partition by {hash_key_name} order by load_date desc) as rn
            FROM (
                SELECT
                    stg.{hash_key_name},
                    {stg_descriptive_attributes}
                    stg.load_date,
                    stg.source
                FROM (
                    SELECT *,
                        row_number() over (partition by {hash_key_name} order by load_date desc) as rn
                    FROM {stg_schema_name}.{table_name}
                ) stg
                LEFT JOIN {core_schema_name}.{table_name} core ON
                    core.{hash_key_name} = stg.{hash_key_name}
                WHERE stg.rn = 1
                    AND (
                        core.{hash_key_name} IS NULL 
                        OR 
                        {descriptive_attributes_differ}
                    )
                UNION ALL 
                SELECT * 
                FROM {core_schema_name}.{table_name}
            ) t
        ) t1
        WHERE rn = 1;
        '''

        drop_table_sql = f"DROP TABLE {core_schema_name}.{table_name};"

        rename_table_sql = f"ALTER TABLE {core_schema_name}.{table_name}_new RENAME TO {table_name};"
        
        cursor = connection.cursor()
        cursor.execute(create_new_sql)
        cursor.execute(drop_table_sql)
        cursor.execute(rename_table_sql)
        connection.commit()