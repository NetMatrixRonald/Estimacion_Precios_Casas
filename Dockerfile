# Usar Python 3.11 oficial
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Actualizar pip y instalar herramientas
RUN pip install --upgrade pip setuptools wheel

# Instalar numpy y scikit-learn específicamente desde wheels
RUN pip install --only-binary=:all: numpy==1.24.3 scikit-learn==1.3.1

# Copiar requirements y instalar el resto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos esenciales
COPY main.py .
COPY artifacts/ artifacts/
COPY scripts/ scripts/

# Verificar instalación
RUN python -c "import numpy, sklearn; print('numpy:', numpy.__version__, 'sklearn:', sklearn.__version__)"

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
