# Python Microservices App

Esta aplicación es un microservicio desarrollado en Python (FASTAPI). Utiliza SQLAlchemy para la gestión de base de datos, pandas para la gestion depuracion de archivos y NATS para la comunicación asíncrona. A continuación, se explican los pasos para configurar y ejecutar el proyecto.

---

## Requisitos

Asegúrate de tener instalados los siguientes programas en tu sistema:

- Python 3.10 o superior
- Virtualenv (opcional pero recomendado)
- PostgreSQL (u otra base de datos configurada)
- NATS Server (si se utiliza NATS para comunicación)

---

## Instalación

Sigue estos pasos para configurar y ejecutar la aplicación:

### 1. Clona este repositorio
```bash
git clone <URL_DE_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### 2. Crea y activa un entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
source venv/bin/activate    # En Linux/Mac
venv\Scripts\activate      # En Windows
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno
Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DATABASE_URL=postgresql+psycopg2://usuario:contraseña@localhost:5432/nombre_basedatos
NATS_URL=nats://localhost:4222
```

Asegúrate de reemplazar `usuario`, `contraseña`, y `nombre_basedatos` por los valores correspondientes a tu base de datos o puedes mirar la configuracion en el .env.template.

### 5. Realiza las migraciones de la base de datos (si aplica)
```bash
alembic upgrade head
```

---

## Ejecución

1. Inicia el servidor NATS si es necesario:
```bash
nats-server -p 4222 -m 8222
```

2. Ejecuta la aplicación:
```bash
uvicorn app.api.main:app --reload --port 8003
```

---

## Estructura del Proyecto

```plaintext
├── app
│   ├── config        # Configuraciones generales
│   ├── domain        # Lógica de dominio y modelos
│   ├── services      # Servicios y casos de uso
│   ├── repositories  # Repositorios para interactuar con la base de datos
│   ├── tests         # Pruebas unitarias
├── main.py           # Punto de entrada de la aplicación
├── requirements.txt  # Dependencias del proyecto
├── .env              # Variables de entorno (no incluido en el repositorio)
```

---

## Autor
Desarrollado por Roman Rivas.

---

