from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

app = FastAPI()

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DATABASE_URL = "dbname=bd-test user=postgres password=postgres host=localhost"

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
except Exception as e:
    raise Exception(f"Error conectando a la base de datos: {e}")

def create_customer_table():
    """
    Crea la tabla customer si no existe, con id autogenerado
    y columnas created_at y updated_at con valores por defecto.
    """
    create_table_query = """
        CREATE TABLE IF NOT EXISTS customer (
            id SERIAL PRIMARY KEY,
            customer_type TEXT,
            name TEXT,
            "companyName" TEXT,
            "identityNumber" TEXT,
            email TEXT,
            "taxId" TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()

create_customer_table()

@app.post("/upload", summary="Subir archivo de clientes (Excel o CSV)")
async def upload_customers(file: UploadFile = File(...)):
    # Tipos de contenido admitidos para Excel y CSV
    excel_types = [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]
    csv_types = [
        "text/csv",
        "application/csv",
        "text/plain"
    ]
    
    # Verifica que el archivo sea Excel o CSV
    if file.content_type in excel_types:
        try:
            contents = await file.read()
            df = pd.read_excel(BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al leer el archivo Excel: {e}"
            )
    elif file.content_type in csv_types:
        try:
            contents = await file.read()
            # pd.read_csv puede aceptar BytesIO; si hay problemas de codificación, se puede especificar encoding.
            df = pd.read_csv(BytesIO(contents))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al leer el archivo CSV: {e}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo inválido. Se permiten solo archivos Excel o CSV."
        )
    
    # Definir las columnas esperadas según el esquema de la tabla.
    expected_columns = [
        "customer_type", "name", "companyName", "identityNumber",
        "email", "taxId", "phone", "address", "created_at", "updated_at"
    ]
    # Columnas obligatorias
    required_columns = [
        "customer_type", "name", "companyName", "identityNumber",
        "email", "taxId", "phone", "address"
    ]
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Faltan las siguientes columnas obligatorias en el archivo: {missing_required}"
        )
    
    # Manejar columnas de fechas: Si no existen, se asigna None para que la BD use el default
    for date_col in ["created_at", "updated_at"]:
        if date_col not in df.columns:
            df[date_col] = None
        else:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    
    # Preparar los datos para la inserción respetando el orden de las columnas definidas
    rows = df[expected_columns].values.tolist()
    
    insert_query = """
        INSERT INTO customer (
            customer_type, name, "companyName", "identityNumber", email, "taxId", phone, address, created_at, updated_at
        )
        VALUES %s;
    """
    
    try:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, rows)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al insertar datos en la base de datos: {e}"
        )
    
    return {"detail": f"Se han insertado {len(rows)} registros de clientes correctamente."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
