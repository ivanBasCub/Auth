# Imagen base
FROM python:3.11-slim

# Variables de entorno para evitar .pyc y habilitar logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero para aprovechar la cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer puerto para Django
EXPOSE 8000

# Comando por defecto (se puede sobrescribir en docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
