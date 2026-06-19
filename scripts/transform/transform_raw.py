from pathlib import Path
import os
import pandas as pd
import math
import logging

DIRECTORY = "transformed_data"
RAW_DATA_DIRECTORY = "raw_data"
OUTPUT_FILE = "food_inflation.csv"
PRODUCT_FILE = 'products.csv'
RAW_DATA_FILE = "worldbank_data_food_inflation.csv"

extracted_fields = ["ISO3", "country", "adm1_name", "adm2_name", "mkt_name", "lat", "lon", "geo_id", "year", "month", "currency"]

def transform_raw():
    logger = logging.getLogger(__name__)
    base_path = '/opt/airflow'
    transformed_data_path = os.path.join(base_path, DIRECTORY)
    os.makedirs(transformed_data_path, exist_ok=True)
    logger.info(f"Найден каталог {transformed_data_path}")

    raw_data_path = os.path.join(base_path, RAW_DATA_DIRECTORY)
    raw_data_file_name = os.path.join(raw_data_path, RAW_DATA_FILE)
    logger.info(f"Файл с сырыми данными {raw_data_file_name}")

    raw_data = pd.read_csv(raw_data_file_name)
    logger.info(f"Прочитан файл с сырыми данными")
    
    output_file_name = os.path.join(transformed_data_path, OUTPUT_FILE)

    products_file_name = os.path.join(raw_data_path, PRODUCT_FILE)
    products = pd.read_csv(products_file_name)
    logger.info(f"Прочитан файл с наименованиями продуктов {products_file_name}")
    products_list = products.iloc[:, 0].tolist()

    output_rows = []
    for record in raw_data.itertuples():
        row = {}
        for field in extracted_fields:
            row[field] = getattr(record, field)
        
        for product in products_list:
            if not math.isnan(getattr(record, "o_" + product)):
                product_info = {}
                product_info["product"] = product
                product_info["average_price"] = getattr(record, "o_" + product)
                product_info["max_price"] = getattr(record, "h_" + product)
                product_info["min_price"] = getattr(record, "l_" + product)
                result_row = row | product_info
                output_rows.append(result_row)
        
    result = pd.DataFrame(output_rows)
    result.to_csv(output_file_name, index=False, encoding='utf-8')
    logger.info(f"Записаны данные в файл {output_file_name}") 