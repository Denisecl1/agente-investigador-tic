
import os
import hashlib
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from flask import request
from upstash_redis import Redis


# Configuración del límite diario
LIMITE_DIARIO = 2
ZONA_HORARIA = ZoneInfo("America/Mexico_City")

MENSAJE_LIMITE = (
    "Has alcanzado tu límite de peticiones del día de hoy. "
    "Vuelve mañana para volver a utilizarlo."
)


def comprobar_limite_diario():
    # Obtener credenciales privadas de Upstash
    url = (
        os.getenv("KV_REST_API_URL")
        or os.getenv("STORAGE_KV_REST_API_URL")
        or os.getenv("UPSTASH_REDIS_REST_URL")
    )

    token = (
        os.getenv("KV_REST_API_TOKEN")
        or os.getenv("STORAGE_KV_REST_API_TOKEN")
        or os.getenv("UPSTASH_REDIS_REST_TOKEN")
    )

    if not url or not token:
        raise RuntimeError("Falta configurar Upstash Redis")

    # Identificar la IP del visitante
    if os.getenv("VERCEL"):
        ip = (
            request.headers.get("x-vercel-forwarded-for")
            or request.headers.get("x-forwarded-for")
            or ""
        ).split(",")[0].strip()
    else:
        ip = request.remote_addr

    if not ip:
        raise RuntimeError("No se pudo identificar la IP")

    # Fecha actual en México
    ahora = datetime.now(ZONA_HORARIA)
    fecha = ahora.strftime("%Y-%m-%d")

    # Crear un identificador sin guardar la IP directamente
    ip_hash = hashlib.sha256(
        ip.encode("utf-8")
    ).hexdigest()

    clave = f"radar_tic:limite:{fecha}:{ip_hash}"

    # Calcular cuánto falta para medianoche
    manana = datetime.combine(
        ahora.date() + timedelta(days=1),
        time.min,
        tzinfo=ZONA_HORARIA
    )

    segundos = max(
        1,
        int((manana - ahora).total_seconds())
    )

    # Conectar con Redis
    redis = Redis(url=url, token=token)

    # Incrementar contador y establecer expiración
    transaccion = redis.multi()
    transaccion.incr(clave)
    transaccion.expire(clave, segundos)

    resultados = transaccion.exec()
    total = int(resultados[0])

    # Permitir únicamente los primeros dos intentos
    permitido = total <= LIMITE_DIARIO

    return permitido, segundos
