# 🔧 Solución para Error de Python 3.13 en Render

## ❌ Problema
Render estaba usando Python 3.13 por defecto, pero nuestras dependencias (pandas 2.0.3, numpy 1.24.3) no tienen wheels precompilados para Python 3.13, causando el error:
```
BackendUnavailable: Cannot import 'setuptools.build_meta'
```

## ✅ Solución implementada

### 1. **Archivos de configuración añadidos:**
- `render.yaml` - Fuerza Python 3.11 en Render
- `.python-version` - Versión específica para pyenv
- `runtime.txt` actualizado a Python 3.11.9

### 2. **Dependencias actualizadas:**
- Añadido `setuptools>=65.0.0` y `wheel>=0.37.0` al requirements.txt
- Versiones estables que tienen wheels para Python 3.11

### 3. **Configuración en Render:**
- **Environment**: Python 3
- **Python Version**: 3.11.9 (específico)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🚀 Pasos para desplegar

1. **Subir cambios:**
   ```bash
   git add .
   git commit -m "Fix Python 3.13 compatibility - force Python 3.11"
   git push origin main
   ```

2. **En Render:**
   - Crear nuevo Web Service
   - Conectar repositorio
   - **IMPORTANTE**: Seleccionar Python Version 3.11.9
   - Render detectará automáticamente `render.yaml`
   - Deploy

## ⚡ Por qué funcionará ahora

- **Python 3.11.9**: Versión estable con wheels precompilados para pandas/numpy
- **setuptools/wheel**: Herramientas de build actualizadas
- **Versiones estables**: pandas 2.0.3 y numpy 1.24.3 tienen wheels para Python 3.11
- **Sin compilación**: Todas las dependencias se instalan desde wheels precompilados

El build debería completarse sin errores en ~2-3 minutos.
