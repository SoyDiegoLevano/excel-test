import os
import pandas as pd
from datetime import datetime

# Datos de ejemplo
data = {
    "customer_type": ["Personal", "Empresa"],
    "name": ["Juan Perez", "ACME Corp"],
    "companyName": ["", "ACME Corporation"],
    "identityNumber": ["123456789", "987654321"],
    "email": ["juan@example.com", "contacto@acme.com"],
    "taxId": ["", "A1B2C3"],
    "phone": ["555-1234", "555-5678"],
    "address": ["Calle Falsa 123", "Avenida Siempre Viva 742"],
    "created_at": [datetime.now(), datetime.now()],
    "updated_at": [datetime.now(), datetime.now()],
}

# Crear DataFrame
df = pd.DataFrame(data)

# Nombres de archivos a generar
excel_file = "clientes_sample.xlsx"
csv_file = "clientes_sample.csv"

# Guardar en Excel (XLSX) y sobrescribir si existe
df.to_excel(excel_file, index=False)

# Guardar en CSV y sobrescribir si existe
df.to_csv(csv_file, index=False)

print(f"Archivos '{excel_file}' y '{csv_file}' creados con éxito.")
