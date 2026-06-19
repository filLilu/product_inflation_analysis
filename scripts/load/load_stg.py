import os
import sys
import json
import psycopg2

from .HubLoader import HubLoader
from .SatellitLoader import SatellitLoader
from .LinkLoader import LinkLoader
from .LinkSatellitLoader import LinkSatellitLoader

MODEL_DIRECTORY = "model"
MODEL_FILENAME = 'description.json'
INPUT_DATA_DIRECTORY = "transformed_data"
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'), 
    'port': os.getenv('DB_PORT', '5432')
}

base_path = '/opt/airflow'
model_path = os.path.join(base_path, MODEL_DIRECTORY)
sys.path.append(str(model_path))

def get_hubs_list(model_description): 
    hubs = model_description["objects"]
    objects = []
    for hub in hubs:
        object = {}
        object["name"] = hub["name"]
        business_key_attributes = []
        for business_key in hub["business_key"]:
            key = {}
            key["name"] = business_key["target_name"]
            key["type"] = business_key["type"]
            business_key_attributes.append(key)
        object["business_key"] = business_key_attributes
        objects.append(object)
    return objects

def get_sats_list(model_description):
    hubs = model_description["objects"]
    satellits = []
    for hub in hubs:
        if len(hub["descriptive_attributes"]) > 0:
            object = {}
            object["name"] = hub["name"]
            descriptive_attributes = []
            for attr in hub["descriptive_attributes"]:
                attribute = {}
                attribute["name"] = attr["target_name"]
                attribute["type"] = attr["type"]
                descriptive_attributes.append(attribute)
            object["descriptive_attributes"] = descriptive_attributes
            satellits.append(object)
    return satellits

def get_links_list(model_description):
    links_struct = model_description["links"]
    links = []
    for obj in links_struct:
        links.append(obj["linked_objects"])    
    return links

def get_link_sats_list(model_description):
    links = model_description["links"]
    link_satellits = []
    for link in links:
        if len(link["descriptive_attributes"]) > 0:
            link_sat = {}
            link_sat["objects"] = link["linked_objects"]
            descriptive_attributes = []
            for attr in link["descriptive_attributes"]:
                attribute = {}
                attribute["name"] = attr["target_name"]
                attribute["type"] = attr["type"]
                descriptive_attributes.append(attribute)

            link_sat["descriptive_attributes"] = descriptive_attributes
            link_satellits.append(link_sat)

    return link_satellits

def load_hubs_stg(hub_list, connection, data_directory):
    cursor = connection.cursor()

    for obj in hub_list:
        hub_loader = HubLoader(obj["name"], obj["business_key"])
        hub_loader.create_table("stg", connection)
        cursor.execute(f"TRUNCATE TABLE stg.h_{obj["name"]};")
        cursor.execute("SET search_path TO stg;")

        hub_directory = os.path.join(data_directory, "hub")

        n = 1
        while True:
            hub_file_name = os.path.join(hub_directory, "h_" + obj["name"] + "_" + str(n) + ".csv")
            if os.path.exists(hub_file_name):
                with open(hub_file_name, 'r', encoding='utf-8') as input_file:
                    next(input_file) 
                    cursor.copy_from(
                        input_file,
                        "h_" + obj["name"],
                        sep=','
                    )
                n += 1
            else:
                break
    
    connection.commit()

def load_satellits_stg(sats_list, connection, data_directory):
    cursor = connection.cursor()
    
    for sat in sats_list:
        sat_loader = SatellitLoader(sat["name"], sat["descriptive_attributes"])
        sat_loader.create_table("stg", connection)

        cursor.execute(f"TRUNCATE TABLE stg.s_{sat["name"]};")
        cursor.execute("SET search_path TO stg;")

        sat_directory = os.path.join(data_directory, "satellit")

        sql_command = f"""
        COPY s_{sat["name"]} FROM STDIN
        WITH (
            FORMAT csv,
            DELIMITER ',',
            QUOTE '"',
            HEADER true,
            NULL ''
        )
        """

        n = 1
        while True:
            sat_file_name = os.path.join(sat_directory, "s_" + sat["name"] + "_" + str(n) + ".csv")
            if os.path.exists(sat_file_name):
                with open(sat_file_name, 'r', encoding='utf-8') as input_file:
                    cursor.copy_expert(sql_command, input_file)
                n += 1
            else:
                break
    
    connection.commit()

def load_links_stg(links_list, connection, data_directory):
    cursor = connection.cursor()
    
    for link in links_list:
        name = ""
        for obj in link:
            name += "_" + obj
        name = name[1:]

        link_loader = LinkLoader(link)
        link_loader.create_table("stg", connection)
        cursor.execute(f"TRUNCATE TABLE stg.l_{name};")
        cursor.execute("SET search_path TO stg;")

        link_directory = os.path.join(data_directory, "link")

        n = 1
        while True:
            link_file_name = os.path.join(link_directory, "l_" + name + "_" + str(n) + ".csv")
            if os.path.exists(link_file_name):
                with open(link_file_name, 'r', encoding='utf-8') as input_file:
                    next(input_file) 
                    cursor.copy_from(
                        input_file,
                        "l_" + name,
                        sep=','
                    )
                n += 1
            else:
                break
    
    connection.commit()

def load_link_satellits_stg(link_sats_list, connection, data_directory):
    cursor = connection.cursor()

    for link_sat in link_sats_list:
        link_sat_loader = LinkSatellitLoader(link_sat["objects"], link_sat["descriptive_attributes"])
        link_sat_loader.create_table("stg", connection)

        name = ""
        for obj in link_sat["objects"]:
            name += "_" + obj
        name = name[1:]

        cursor.execute(f"TRUNCATE TABLE stg.ls_{name};")
        cursor.execute("SET search_path TO stg;")

        sat_directory = os.path.join(data_directory, "satellit")

        n = 1
        while True:
            link_sat_file_name = os.path.join(sat_directory, "ls_" + name + "_" + str(n) + ".csv")
            if os.path.exists(link_sat_file_name):
                with open(link_sat_file_name, 'r', encoding='utf-8') as input_file:
                    next(input_file) 
                    cursor.copy_from(
                        input_file,
                        "ls_" + name,
                        sep=','
                    )
                n += 1
            else:
                break
    
    connection.commit()

def load_stg():
    data_directory = os.path.join(base_path, INPUT_DATA_DIRECTORY)

    model_path = os.path.join(base_path, MODEL_DIRECTORY)
    with open(os.path.join(model_path, MODEL_FILENAME)) as f:
        model_description = json.load(f)
    
    hubs_list = get_hubs_list(model_description)
    sats_list = get_sats_list(model_description)
    links_list = get_links_list(model_description)
    link_sats_list = get_link_sats_list(model_description)

    connection = psycopg2.connect(**DB_CONFIG)

    cursor = connection.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS stg;")
    connection.commit()

    load_hubs_stg(hubs_list, connection, data_directory)
    load_satellits_stg(sats_list, connection, data_directory)
    load_links_stg(links_list, connection, data_directory)
    load_link_satellits_stg(link_sats_list, connection, data_directory)