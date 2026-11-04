# Webhook NFC → luz de la habitación

Función en Python, desplegada gratis en Vercel, que alterna la roseta conectada a Smart Life.
La etiqueta NFC (con MacroDroid) llama a:

```
https://<tu-proyecto>.vercel.app/api/toggle?token=<WEBHOOK_TOKEN>
```

## 1. Credenciales de Tuya (iot.tuya.com)

1. Crea una cuenta en https://iot.tuya.com con el mismo correo o una cuenta nueva.
2. **Cloud → Development → Create Cloud Project**
   - Development method: *Smart Home*
   - Data center: el mismo de tu cuenta de Smart Life (en Colombia normalmente **Western America**).
3. Al crear el proyecto, autoriza las APIs que te sugiere (IoT Core, Authorization, Smart Home Basic Service).
4. En **Overview** copia el **Access ID** y el **Access Secret**.
5. Pestaña **Devices → Link App Account → Add App Account**: aparece un código QR.
   En Smart Life ve a **Yo → ícono de escaneo** y escanéalo. Tu roseta aparecerá en la lista.
6. Copia el **Device ID** de la roseta.

> La suscripción gratuita de IoT Core en Tuya se vence periódicamente; cuando ocurra, la renuevas gratis desde **Cloud → Cloud Services**.

## 2. Despliegue en Vercel

1. Sube esta carpeta a un repositorio de GitHub.
2. En https://vercel.com → **Add New → Project** → importa el repositorio (sin cambiar la configuración).
3. En **Settings → Environment Variables** agrega:

| Variable | Valor |
|---|---|
| `TUYA_ACCESS_ID` | Access ID |
| `TUYA_ACCESS_SECRET` | Access Secret |
| `TUYA_DEVICE_ID` | Device ID de la roseta |
| `TUYA_REGION` | `us` para Western America (`us-e`, `eu`, `in`, `cn` en otros casos) |
| `WEBHOOK_TOKEN` | Una clave larga inventada por ti |

4. Haz **Redeploy** para que tome las variables.

## 3. Prueba

Abre la URL en el navegador. Debes ver algo como:

```json
{"ok": true, "code": "switch_led", "encendido": true}
```

Si responde con error, el mensaje indica qué falló (región, credenciales o código del interruptor).
Si dice que no encuentra el código, define `TUYA_SWITCH_CODE` con uno de los códigos que lista.

## 4. MacroDroid

En la acción **Solicitud HTTP** de tu macro cambia la URL de IFTTT por la de Vercel. Listo.
