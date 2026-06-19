import requests
import pandas as pd
import time
import os
from datetime import datetime
from pathlib import Path

DATASET_URL = 'https://microdata.worldbank.org/api/tables/data/fcv/wld_2021_rtfp_v02_m'
BATCH_SIZE = 5000
OUTPUT_FILE = 'worldbank_data_food_inflation.csv'
LOG_FILE = 'extract_food_inflation.log'
DIRECTORY = "raw_data"
extracted_fields = ["ISO3", "country", "adm1_name", "adm2_name", "mkt_name", "lat", "lon", "geo_id", "year", "month", "currency", "o_apples", "h_apples", "l_apples", "o_bananas", "h_bananas", "l_bananas", "o_beans", "h_beans", "l_beans", "o_beans_egyptian", "h_beans_egyptian", "l_beans_egyptian", "o_beans_fao", "h_beans_fao", "l_beans_fao", "o_bread", "h_bread", "l_bread", "o_bread_fao", "h_bread_fao", "l_bread_fao", "o_bulgur", "h_bulgur", "l_bulgur", "o_cabbage", "h_cabbage", "l_cabbage", "o_carrots", "h_carrots", "l_carrots", "o_cassava", "h_cassava", "l_cassava", "o_cassava_fao", "h_cassava_fao", "l_cassava_fao", "o_cassava_flour", "h_cassava_flour", "l_cassava_flour", "o_cassava_flour_fao", "h_cassava_flour_fao", "l_cassava_flour_fao", "o_cassava_meal", "h_cassava_meal", "l_cassava_meal", "o_cheese", "h_cheese", "l_cheese", "o_chickpeas", "h_chickpeas", "l_chickpeas", "o_chili", "h_chili", "l_chili", "o_cocoyam_fao", "h_cocoyam_fao", "l_cocoyam_fao", "o_coffee_instant", "h_coffee_instant", "l_coffee_instant", "o_couscous", "h_couscous", "l_couscous", "o_couscous_fao", "h_couscous_fao", "l_couscous_fao", "o_cowpeas", "h_cowpeas", "l_cowpeas", "o_cowpeas_fao", "h_cowpeas_fao", "l_cowpeas_fao", "o_cowpeased_fao", "h_cowpeased_fao", "l_cowpeased_fao", "o_cucumbers", "h_cucumbers", "l_cucumbers", "o_dates", "h_dates", "l_dates", "o_eggplants", "h_eggplants", "l_eggplants", "o_eggs", "h_eggs", "l_eggs", "o_fish", "h_fish", "l_fish", "o_fish_barbel_sole", "h_fish_barbel_sole", "l_fish_barbel_sole", "o_fish_catfish", "h_fish_catfish", "l_fish_catfish", "o_fish_goldstripe_sardinella", "h_fish_goldstripe_sardinella", "l_fish_goldstripe_sardinella", "o_fish_mackerel", "h_fish_mackerel", "l_fish_mackerel", "o_fish_milkfish", "h_fish_milkfish", "l_fish_milkfish", "o_fish_mullet_catfish", "h_fish_mullet_catfish", "l_fish_mullet_catfish", "o_fish_roundscad", "h_fish_roundscad", "l_fish_roundscad", "o_fish_salted", "h_fish_salted", "l_fish_salted", "o_fish_smoked", "h_fish_smoked", "l_fish_smoked", "o_fish_tilapia", "h_fish_tilapia", "l_fish_tilapia", "o_fish_tuna_canned", "h_fish_tuna_canned", "l_fish_tuna_canned", "o_fonio", "h_fonio", "l_fonio", "o_gari_fao", "h_gari_fao", "l_gari_fao", "o_garlic", "h_garlic", "l_garlic", "o_groundnuts", "h_groundnuts", "l_groundnuts", "o_groundnuts_paste", "h_groundnuts_paste", "l_groundnuts_paste", "o_lemons", "h_lemons", "l_lemons", "o_lentils", "h_lentils", "l_lentils", "o_livestock_camel_fao", "h_livestock_camel_fao", "l_livestock_camel_fao", "o_livestock_goat", "h_livestock_goat", "l_livestock_goat", "o_livestock_goat_fao", "h_livestock_goat_fao", "l_livestock_goat_fao", "o_livestock_goat_s_fao", "h_livestock_goat_s_fao", "l_livestock_goat_s_fao", "o_livestock_sheep_two_year_old_male", "h_livestock_sheep_two_year_old_male", "l_livestock_sheep_two_year_old_male", "o_livestockgoat_castrated_male", "h_livestockgoat_castrated_male", "l_livestockgoat_castrated_male", "o_livestockgoat_male", "h_livestockgoat_male", "l_livestockgoat_male", "o_livestocksheep_castrated_male", "h_livestocksheep_castrated_male", "l_livestocksheep_castrated_male", "o_maize", "h_maize", "l_maize", "o_maize_fao", "h_maize_fao", "l_maize_fao", "o_maize_flour", "h_maize_flour", "l_maize_flour", "o_maize_flour_fao", "h_maize_flour_fao", "l_maize_flour_fao", "o_maize_meal", "h_maize_meal", "l_maize_meal", "o_meat_beef", "h_meat_beef", "l_meat_beef", "o_meat_beef_chops", "h_meat_beef_chops", "l_meat_beef_chops", "o_meat_beef_fao", "h_meat_beef_fao", "l_meat_beef_fao", "o_meat_beef_minced", "h_meat_beef_minced", "l_meat_beef_minced", "o_meat_buffalo", "h_meat_buffalo", "l_meat_buffalo", "o_meat_camel_fao", "h_meat_camel_fao", "l_meat_camel_fao", "o_meat_chicken", "h_meat_chicken", "l_meat_chicken", "o_meat_chicken_broiler", "h_meat_chicken_broiler", "l_meat_chicken_broiler", "o_meat_chicken_fao", "h_meat_chicken_fao", "l_meat_chicken_fao", "o_meat_chicken_plucked", "h_meat_chicken_plucked", "l_meat_chicken_plucked", "o_meat_chicken_whole", "h_meat_chicken_whole", "l_meat_chicken_whole", "o_meat_goat", "h_meat_goat", "l_meat_goat", "o_meat_lamb", "h_meat_lamb", "l_meat_lamb", "o_meat_mutton_fao", "h_meat_mutton_fao", "l_meat_mutton_fao", "o_meat_pork", "h_meat_pork", "l_meat_pork", "o_melons", "h_melons", "l_melons", "o_milk", "h_milk", "l_milk", "o_milk_fao", "h_milk_fao", "l_milk_fao", "o_millet", "h_millet", "l_millet", "o_millet_fao", "h_millet_fao", "l_millet_fao", "o_oil", "h_oil", "l_oil", "o_oil_fao", "h_oil_fao", "l_oil_fao", "o_okra", "h_okra", "l_okra", "o_onions", "h_onions", "l_onions", "o_onions_fao", "h_onions_fao", "l_onions_fao", "o_oranges", "h_oranges", "l_oranges", "o_parsley", "h_parsley", "l_parsley", "o_pasta", "h_pasta", "l_pasta", "o_peas", "h_peas", "l_peas", "o_plantains", "h_plantains", "l_plantains", "o_plantains_fao", "h_plantains_fao", "l_plantains_fao", "o_potatoes", "h_potatoes", "l_potatoes", "o_potatoes_fao", "h_potatoes_fao", "l_potatoes_fao", "o_pulses", "h_pulses", "l_pulses", "o_rice", "h_rice", "l_rice", "o_rice_fao", "h_rice_fao", "l_rice_fao", "o_rice_various", "h_rice_various", "l_rice_various", "o_salt", "h_salt", "l_salt", "o_sesame", "h_sesame", "l_sesame", "o_sorghum", "h_sorghum", "l_sorghum", "o_sorghum_fao", "h_sorghum_fao", "l_sorghum_fao", "o_sorghum_food_aid", "h_sorghum_food_aid", "l_sorghum_food_aid", "o_sugar", "h_sugar", "l_sugar", "o_tea", "h_tea", "l_tea", "o_teff_fao", "h_teff_fao", "l_teff_fao", "o_tomatoes", "h_tomatoes", "l_tomatoes", "o_tomatoes_paste", "h_tomatoes_paste", "l_tomatoes_paste", "o_watermelons", "h_watermelons", "l_watermelons", "o_wheat", "h_wheat", "l_wheat", "o_wheat_fao", "h_wheat_fao", "l_wheat_fao", "o_wheat_flour", "h_wheat_flour", "l_wheat_flour", "o_wheat_flour_fao", "h_wheat_flour_fao", "l_wheat_flour_fao", "o_yam", "h_yam", "l_yam", "o_yogurt", "h_yogurt", "l_yogurt", "o_beans_egyptian", "h_beans_egyptian", "l_beans_egyptian", "o_cowpeas_fao", "h_cowpeas_fao", "l_cowpeas_fao", "o_watermelons", "h_watermelons", "l_watermelons"]


def fetch_data_batch(url, offset, batch_size, log_file):
    """
    Функция для получения батча данных из API. Выделяет из ответа только необходимые атрибуты

    Args:
        url (string): URL API
        offset (int): Смещение для пагинации
        batch_size (int): Размер батча
        log_file (file): Файл для логирования
    
    Returns:
        list: Список записей или пустой список в случае ошибки.

    """

    params = {
        'limit': batch_size,
        'offset': offset,
        'type': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=180)
        response.raise_for_status()
        data = response.json()

        if 'data' in data:
            records = data.get('data', [])
            result = []

            for record in records:
                row = {}
                for field in extracted_fields:
                    row[field] = record.get(field)
                result.append(row)
            return result

        else:
            log_file.write(f"{datetime.now()} Ошибка! Структура ответа не соответствует ожидаемой.\n")
            return []

    except requests.exceptions.RequestException as e:
        log_file.write(f"{datetime.now()} Ошибка при запросе данных: {e}\n")
        return []
    except ValueError as e:
        log_file.write(f"{datetime.now()} Ошибка парсинга JSON: {e}\n")
        return []

def extract():
    all_data = []
    offset = 0
    total_records = 0
    
    base_path = '/opt/airflow'
    raw_data_path = os.path.join(base_path, DIRECTORY)
    os.makedirs(raw_data_path, exist_ok=True)

    log_file_path = os.path.join(raw_data_path, LOG_FILE)

    # Создаем файл с логами загрузки
    with open(log_file_path, 'w', encoding='utf-8') as log_file:

        log_file.write("Старт загрузки данных\n")
        
        output_file_path = os.path.join(raw_data_path, OUTPUT_FILE)

        # Создаем файл с сырыми данными, записываем в него структуру записей
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            fields_cnt = len(extracted_fields)
            for i in range(fields_cnt):
                output_file.write(extracted_fields[i])
                if i < fields_cnt - 1:
                    output_file.write(",")

            output_file.write("\n")
    
        while True:
            log_file.write(f"{datetime.now()} Загрузка батча со смещением {offset}\n")
            batch = fetch_data_batch(DATASET_URL, offset, BATCH_SIZE, log_file)

            if not batch:
                break

            df = pd.DataFrame(batch)

            batch_size = len(batch)
            total_records += batch_size

            try:
                df.to_csv(output_file_path, mode='a', header=False, index=False, encoding='utf-8')
                log_file.write(f"{datetime.now()} Загружено {batch_size} записей в файл: {OUTPUT_FILE}. Всего: {total_records}\n")
            except Exception as e:
                log_file.write(f"{datetime.now()} Ошибка при сохранении записей в файл: {e.message}\n")


            if batch_size < BATCH_SIZE:
                break

            offset += BATCH_SIZE

            time.sleep(5)        

        log_file.write(f"{datetime.now()} Всего загружено записей: {total_records}\n")