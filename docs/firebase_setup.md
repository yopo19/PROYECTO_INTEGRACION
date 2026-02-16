# Configuración de Firebase Firestore

Para conectar el Agente a una base de datos real en Firebase, sigue estos pasos:

## 1. Crear Proyecto en Firebase Console
1. Ve a [console.firebase.google.com](https://console.firebase.google.com/).
2. Crea un nuevo proyecto.
3. Ve a **Firestore Database** en el menú lateral y dale a **Crear base de datos**.
4. Selecciona el modo **Nativo** y una ubicación cercana.

## 2. Generar Credenciales de Servicio (Service Account)
1. En tu proyecto, ve a la tuerca de **Configuración del proyecto** > **Cuentas de servicio**.
2. Haz clic en **Generar nueva clave privada**.
3. Se descargará un archivo JSON. **Guárdalo en un lugar seguro** (no lo subas al repositorio público).
4. Renombra el archivo a `firebase_credentials.json` y muévelo a la raíz del proyecto (o donde prefieras, pero asegúrate de añadirlo al `.gitignore`).

## 3. Configurar Entorno
En tu archivo `.env` o variables de entorno, añade la ruta al archivo JSON:

```bash
FIREBASE_CREDENTIALS_PATH=d:\Dev\PROYECTO_INTEGRACION\firebase_credentials.json
USE_FIRESTORE=true
```

## 4. Cargar Datos de Prueba (Seed)
Ejecuta el script para poblar la base de datos con los becarios de prueba:

```bash
python scripts/seed_firestore.py
```

## 5. Verificar
Si `USE_FIRESTORE=true`, el agente consultará Firestore en lugar de los datos en memoria.
