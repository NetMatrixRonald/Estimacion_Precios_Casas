# Usar imagen con numpy y scikit-learn ya instalados
FROM continuumio/miniconda3:latest

# Establecer directorio de trabajo
WORKDIR /app

# Crear entorno conda con versiones específicas
RUN conda create -n appenv python=3.11 numpy=1.24.3 scikit-learn=1.3.1 pandas=2.0.3 -y

# Activar entorno
ENV CONDA_DEFAULT_ENV=appenv
ENV PATH=/opt/conda/envs/$CONDA_DEFAULT_ENV/bin:$PATH

# Instalar dependencias adicionales con pip
RUN pip install fastapi==0.104.1 uvicorn==0.24.0 joblib==1.3.2 pydantic==2.4.2

# Copiar archivos esenciales
COPY main.py .
COPY artifacts/ artifacts/
COPY scripts/ scripts/

# Verificar instalación
RUN python -c "import numpy, sklearn, pandas; print('numpy:', numpy.__version__, 'sklearn:', sklearn.__version__, 'pandas:', pandas.__version__)"

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
