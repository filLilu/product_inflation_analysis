DIRECTORY = "transformed_data"
MODEL_DIRECTORY = "model"
MODEL_FILENAME = 'description.json'
HUB_DIRECTORY = "hub"
SAT_DIRECTORY = "satellit"
LINK_DIRECTORY = "link"
RAW_DATA_DIRECTORY = "raw_data"
SOURCE_FILE_NAME = "food_inflation.csv"

import pandas as pd
import json
import os
import sys
import shutil

from pathlib import Path

from Hub import Hub
from Satellit import Satellit
from Link import Link
from LinkSatellit import LinkSatellit

def transform_hubs_satellits(raw_data, model_description):
    """
    Функция для преобразования данных хабов и их сателлитов из сырых данных
    
    Args:
        raw_data (DataFrame): датафрейм с сырыми данными
        model_description: json с описанием структуры объектов

    Returns:
        hubs_sats_grouped: Список словарей, содержащих атрибуты:
            object_name: наименование объекта
            hub_values: записи хаба по объекту
            satellit_values: записи сателлита по объекту
    """
    hub_rows = [] # массив всех хабов, полученных из строки датафрейма
    satellit_rows = [] # массив всех сателлитов, полученных из строки датафрейма
    objects = set() # множество уникальных наименований объектов. Необходимо для группировки хабов по объекту

    # формируем список хабов и сателлитов по всем объектам из каждой строки исходного файла
    for row in raw_data.itertuples():
        for obj in model_description["objects"]:
            object_name = obj["name"]
            objects.add(object_name)

            business_key = {}
            for key in obj["business_key"]:
                business_key[key["target_name"]] = getattr(row, key["source_name"])

            hub = Hub(object_name, business_key, "worldbank")
            hub_rows.append(hub)

            if len(obj["descriptive_attributes"]) > 0:
                descriptive_attributes = {}
                for attr in obj["descriptive_attributes"]:
                    descriptive_attributes[attr["target_name"]] = getattr(row, attr["source_name"])
                
                satellit = Satellit(object_name, business_key, descriptive_attributes, "worldbank")
                satellit_rows.append(satellit)

    # инициализируем список хабов и сателлитов, сгруппированных по наименованию объекта
    hubs_sats_grouped = []
    for object in objects:
        hub = {}
        hub["object_name"] = object
        hub["hub_values"] = []
        hub["satellit_values"] = []
        hubs_sats_grouped.append(hub)

    for row in hub_rows:
        for obj in hubs_sats_grouped:
            if obj["object_name"] == row.object_name:
                obj["hub_values"].append(row.convert_to_dict())

    for row in satellit_rows:
        for obj in hubs_sats_grouped:
            if obj["object_name"] == row.object_name:
                obj["satellit_values"].append(row.convert_to_dict())
    
    return hubs_sats_grouped

def save_hubs(hubs_grouped, file_num, hub_data_path):
    """
    Функция для сохранения преобразованных данных хабов
    
    Args:
        hubs_grouped: Список хабов, сгруппированных по наименованию объекта. Каждый объект словаря содержит атрибуты:
            object_name: наименование объекта
            hub_values: записи хаба по объекту
            satellit_values: записи сателлита по объекту
    """

    for hub in hubs_grouped:
        output_file = os.path.join(hub_data_path, "h_" + hub["object_name"] + "_" + str(file_num) + ".csv")
        df = pd.DataFrame(hub["hub_values"])
        hash_key_name = hub["object_name"] + "_hk"
        df.drop_duplicates(subset=[hash_key_name], keep='first', inplace=True)
        df.to_csv(output_file, index=False, encoding='utf-8')

def save_satellits(satellits_grouped, file_num, sat_data_path):
    """
    Функция для сохранения преобразованных данных сателлитов, описывающих хабы
    
    Args:
        hubs_grouped: Список сателлитов, сгруппированных по наименованию объекта. Каждый объект словаря содержит атрибуты:
            object_name: наименование хаба
            hub_values: записи хаба по объекту
            satellit_values: записи сателлита по объекту
    """
    for sat in satellits_grouped:
        if len(sat["satellit_values"]) > 0:
            output_file = os.path.join(sat_data_path, "s_" + sat["object_name"] + "_" + str(file_num) + ".csv")
            df = pd.DataFrame(sat["satellit_values"])
            hash_key_name = sat["object_name"] + "_hk"
            df.drop_duplicates(subset=[hash_key_name], keep='first', inplace=True)
            df.to_csv(output_file, index=False, encoding='utf-8')

def transform_links_satellits(raw_data, model_description):
    """
    Функция для преобразования данных линков и их сателлитов из сырых данных
    
    Args:
        raw_data (DataFrame): датафрейм с сырыми данными
        model_description: json с описанием структуры объектов

    Returns:
        links_sats_grouped: Список объектов, содержащих атрибуты:
            link_name:
            objects_struct: список структур объектов, входящих в линк
            link_objects: объекты линка
            link_sat_objects: объекты сателлита, относящегося к линку

    """
    objects = [] # массив всех линков и их сателлитов, полученных из строки датафрейма
    # link_names = set() # множество уникальных наименований линков. Необходимо для группировки объектов

    all_objects_struct = model_description["objects"]

    link_types = []    

    # Формируем массив линков с наименованием линка (конкатенация наименований объектов), структурой бизнес-ключа и списком описательных атрибутов
    for link_type in model_description["links"]:
        link_obj = {}
        link_obj["objects_struct"] = []
        # link_obj["link_name"] = ""
        link_obj["descriptive_attributes"] = link_type["descriptive_attributes"]
        link_obj["link_objects"] = []
        link_obj["link_sat_objects"] = []
        for object_name in link_type["linked_objects"]:
            # link_obj["link_name"] += object_name
            # формируем массив наименований объектов с их бизнес-ключами
            for obj in all_objects_struct:
                if object_name == obj["name"]:
                    struct = {}
                    struct["name"] = obj["name"]
                    struct["business_key"] = obj["business_key"]
                    link_obj["objects_struct"].append(struct)
            
        # link_names.add(link_obj["link_name"])
        link_types.append(link_obj)

    for row in raw_data.itertuples():
        for link_type in link_types:
            objects = []
            for linked_object in link_type["objects_struct"]:
                object = {}
                object["name"] = linked_object["name"]
                business_key = {}

                for key in linked_object["business_key"]:
                    business_key[key["target_name"]] = getattr(row, key["source_name"])
                
                object["business_key"] = business_key
                objects.append(object)

            link = Link(objects, "worldbank")
            link_type["link_objects"].append(link.convert_to_dict())

            if len(link_type["descriptive_attributes"]) > 0:
                descriptive_attributes = {}
                for attr in link_type["descriptive_attributes"]:
                    descriptive_attributes[attr["target_name"]] = getattr(row, attr["source_name"])

                link_sat_object = LinkSatellit(objects, descriptive_attributes, "worldbank")
                link_type["link_sat_objects"].append(link_sat_object.convert_to_dict())

    return link_types

def save_links_sats(linkes_grouped, file_num, link_data_path, sat_data_path):
    """
    Функция для сохранения данных линков и сателлитов, отоносящихсся к линкам

    Args:
        linkes_grouped: список линков, сгруппированных по типу объекта
    """
    for link in linkes_grouped:
        output_file_name = ""

        for obj in link["objects_struct"]:
            output_file_name += "_" + obj["name"]

        hash_key_name = output_file_name[1:] + "_hk"

        output_link_file = os.path.join(link_data_path, "l" + output_file_name + "_" + str(file_num) + ".csv")
        link_df = pd.DataFrame(link["link_objects"])
        link_df.drop_duplicates(subset=[hash_key_name], keep='first', inplace=True)
        link_df.to_csv(output_link_file, index=False)

        if len(link["link_sat_objects"]) > 0:
            output_sat_file = os.path.join(sat_data_path, "ls" + output_file_name + "_" + str(file_num) + ".csv")
            sat_df = pd.DataFrame(link["link_sat_objects"])
            sat_df.drop_duplicates(subset=[hash_key_name], keep='first', inplace=True)
            sat_df.to_csv(output_sat_file, index=False, encoding='utf-8')

def transform_objects():
    base_path = '/opt/airflow'
    transformed_data_path = os.path.join(base_path, DIRECTORY)

    hub_data_path = os.path.join(transformed_data_path, HUB_DIRECTORY)
    if os.path.exists(hub_data_path):
        shutil.rmtree(hub_data_path)
    os.makedirs(hub_data_path, exist_ok=False)

    sat_data_path = os.path.join(transformed_data_path, SAT_DIRECTORY)
    if os.path.exists(sat_data_path):
        shutil.rmtree(sat_data_path)
    os.makedirs(sat_data_path, exist_ok=True)

    link_data_path = os.path.join(transformed_data_path, LINK_DIRECTORY)
    if os.path.exists(link_data_path):
        shutil.rmtree(link_data_path)
    os.makedirs(link_data_path, exist_ok=True)

    # выгружаем модель в объект
    model_path = os.path.join(base_path, MODEL_DIRECTORY)
    with open(os.path.join(model_path, MODEL_FILENAME)) as f:
        model_description = json.load(f)
        
    source_file = os.path.join(transformed_data_path, SOURCE_FILE_NAME)

    chunk_size = 1000000
    chunks = pd.read_csv(source_file, chunksize=chunk_size)

    for chunk_num, chunk in enumerate(chunks, start=1):
        hubs_sats_data = transform_hubs_satellits(chunk, model_description)
        save_hubs(hubs_sats_data, chunk_num, hub_data_path)
        save_satellits(hubs_sats_data, chunk_num, sat_data_path)
        links_sats_data = transform_links_satellits(chunk, model_description)
        save_links_sats(links_sats_data, chunk_num, link_data_path, sat_data_path)