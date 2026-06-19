import os
import sys
import json
import psycopg2


from .HubLoader import HubLoader
from .SatellitLoader import SatellitLoader
from .LinkLoader import LinkLoader
from .LinkSatellitLoader import LinkSatellitLoader
from .load_stg import get_hubs_list, get_sats_list, get_links_list, get_link_sats_list

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


def load_hubs_core(hubs_list, connection):
    for obj in hubs_list:
        hub_loader = HubLoader(obj["name"], obj["business_key"])
        hub_loader.create_table("core", connection)
        hub_loader.load_core("stg", "core", connection)

def load_sats_core(sats_list, connection):
    for obj in sats_list:
        sat_loader = SatellitLoader(obj["name"], obj["descriptive_attributes"])
        sat_loader.create_table("core", connection)
        sat_loader.load_core("stg", "core", connection)

def load_links_core(links_list, connection):
    for obj in links_list:
        link_loader = LinkLoader(obj)
        link_loader.create_table("core", connection)
        link_loader.load_core("stg", "core", connection)

def load_link_sats_core(link_sats_list,  connection):
    for obj in link_sats_list:
        link_loader = LinkSatellitLoader(obj["objects"], obj["descriptive_attributes"])
        link_loader.create_table("core", connection)
        link_loader.load_core("stg", "core", connection)

def load_core():
    model_path = os.path.join(base_path, MODEL_DIRECTORY)
    with open(os.path.join(model_path, MODEL_FILENAME)) as f:
        model_description = json.load(f)
    
    hubs_list = get_hubs_list(model_description)
    sats_list = get_sats_list(model_description)
    links_list = get_links_list(model_description)
    link_sats_list = get_link_sats_list(model_description)

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS core;")
    connection.commit()

    load_hubs_core(hubs_list, connection)
    load_sats_core(sats_list, connection)
    load_links_core(links_list, connection)
    load_link_sats_core(link_sats_list, connection)