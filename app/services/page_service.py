import pandas as pd
from app.domain.repositories.page_repository import PageRepository
from app.domain.repositories.page_log_repository import PageLogRepository
from app.domain.repositories.page_processed_repository import PageProcessedRepository
import requests
import json
import uuid
import csv
from datetime import datetime
import os

# Definir la carpeta base para guardar los archivos
BASE_DIR = "data_lake_files"
BASE_DIR_PROCESSED = "data_lake_processed"

# Crear la carpeta si no existe
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Crear la carpeta si no existe
if not os.path.exists(BASE_DIR_PROCESSED):
    os.makedirs(BASE_DIR_PROCESSED)    

class PageService:
    def __init__(self, staging : PageRepository, log : PageLogRepository, processed : PageProcessedRepository):
        self.staging = staging 
        self.log = log 
        self.processed = processed 

    def create(self, data):
        return self.staging.create(data)

    def get_one(self, id: int):
        return self.staging.get_one(id)
    
    def get_all(self):
        return self.staging.get_all()
    
    def save_to_data_lake(self, data):
        print(data)
        
        exists = self.staging.exists_in_date(data['page_id'], data['date'])

        if exists:
            raise ValueError("This record already exist")

        try:
            url = ""
            match data['page_id']:
                case 1:
                    url = "https://api.mockaroo.com/api/d8c941d0?count=1000&key=9d6d4740"
                case 2:
                    url = "https://api.mockaroo.com/api/d216f630?count=1000&key=9d6d4740"   
            
            if not url:
                raise ValueError("Page not found")

            response = self._consume_api(url)
            if response.status_code != 200:
                error = f"Error consuming API: {response.status_code} {response.reason}"
                self.save_log(error, data)
                raise Exception(f"{error}: {response.status_code} {response.reason}")

            file_path = self._save_response_file(response)
            if not file_path:
                error = "Unsupported Content-Type"
                self.save_log(error, data)
                raise Exception(error)

            data = {
                "date" : data['date'],
                "platform_id" : data['page_id'],
                "file_path" : file_path,
                "status" : "pending"
            }
                
            return self.create(data)
        except requests.exceptions.RequestException as e:
            error = "API request failed:"
            self.save_log(error, data)
            raise Exception(f"{error}: {str(e)}")    
            
    def _consume_api(self, url):
        return requests.get(url)
        
    def _save_response_file(self, response):
        content_type = response.headers.get("Content-Type", "")
        file_name = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        full_path = os.path.join(BASE_DIR, file_name)

        try:
            if "application/json" in content_type:
                data = response.json()
                file_path = f"{file_name}.json"
                with open(f"{full_path}.json", "w") as json_file:
                    json.dump(data, json_file)
                return file_path

            elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in content_type or "application/vnd.ms-excel" in content_type:
                file_path = f"{file_name}.xlsx"
                with open(f"{full_path}.xlsx", "wb") as f:
                    f.write(response.content)
                return file_path

            elif "text/csv" in content_type:
                file_path = f"{file_name}.csv"
                with open(f"{full_path}.csv", "w", newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for row in response.text.splitlines():
                        csv_writer.writerow(row.split(","))
                return file_path

            else:
                return None

        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
        
    def save_log(self, error, data):
        data = {
            "date" : data['date'],
            "platform_id" : data['page_id'],
            "file_path" : "",
            "status" : "request_error"
        }
        row = self.create(data)
        log_data = {
            "staging_data_id" : row.id,
            "error_description" : error,
        }
        self.log.create(log_data)

    def processing_data(self, date):
        pending = self.staging.get_all_pending(date)
        result = []
        for el in pending:
            self.staging.change_staging_status(el.id, 'processing')
            processed = self.processing_file(el)

            if not processed:
                el.status = "error"
                
            result.append(el)

        return result 
    
    def get_staging_from_date(self, date):
        return self.staging.get_staging_from_date(date)

    def processing_file(self, data):
        staging_path = os.path.join(BASE_DIR, data.file_path)
        if staging_path.endswith(".csv"):
            df = pd.read_csv(staging_path)
        elif staging_path.endswith(".json"):
            df = pd.read_json(staging_path)
        elif staging_path.endswith(".xls") or staging_path.endswith(".xlsx"):
            df = pd.read_excel(staging_path)
        else:
            self.staging.change_staging_status(data.id,'failed')
            raise ValueError("Formato de archivo no soportado")
        
        # Eliminar duplicados
        df = df.drop_duplicates()

        # Eliminar filas con valores nulos
        df = df.dropna()

        if 'amount' in df.columns:
            # Eliminar simbolos de pesos y comas para luego convertir 'amount' a float
            df['amount'] = df['amount'].replace({'\$': '', ',': ''}, regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

            # Eliminar filas con valores no convertibles (NaN)
            df = df.dropna(subset=['amount'])

            # Filtrar solo los valores mayores a cero
            df = df[df['amount'] > 0]

        # Filtrar solo las columnas necesarias
        selected_columns = ["model_name", "amount"]
        df = df[selected_columns]  

        df['staging_data_id'] = data.id  

        file_name = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path = os.path.join(BASE_DIR_PROCESSED, file_name)    
        df.to_csv(output_path, index=False)

        data_dict = df.to_dict(orient='records')
        self.staging.insert_bulk_data(data_dict)

        self.staging.change_staging_status(data.id,'completed', file_name)
        return True

    def total_amount_month(self):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        return self.staging.total_amount_month(year, month)





