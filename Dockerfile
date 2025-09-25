# Usar Python 3.11 oficial
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos esenciales primero
COPY main.py .
COPY artifacts/ artifacts/
COPY scripts/ scripts/

# Verificar que el modelo existe
RUN ls -la artifacts/

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
