# RECOMENDADO: Evita compilación C/Cython usando paquetes binarios de conda-forge
FROM mambaorg/micromamba:1.5.8

# Crear entorno con Python 3.11 y dependencias desde conda-forge
USER root
SHELL ["/bin/bash", "-lc"]

ENV MAMBA_DOCKERFILE_ACTIVATE=1 \
    CONDA_ENV=appenv

# Crear entorno y activar
RUN micromamba create -y -n "$CONDA_ENV" -c conda-forge \
    python=3.11 \
    numpy=1.26.4 \
    pandas=2.2.2 \
    scikit-learn=1.5.1 \
    fastapi=0.115.0 \
    uvicorn=0.30.0 \
    joblib=1.4.2 \
    pip \
    && micromamba clean -a -y

# Establecer entorno por defecto
ENV PATH=/opt/conda/envs/$CONDA_ENV/bin:$PATH

WORKDIR /app

# Copiar requirements y instalar dependencias adicionales
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade "pip>=25.2" "setuptools>=75.0.0" "wheel>=0.44.0" && \
    pip install --prefer-binary --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . /app

# Prueba de importación
RUN python -c "import pandas, numpy, fastapi, uvicorn; print('Imports OK - pandas:', pandas.__version__, 'numpy:', numpy.__version__)"

EXPOSE 8000

# Render provee $PORT en runtime
ENV PORT=8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]

