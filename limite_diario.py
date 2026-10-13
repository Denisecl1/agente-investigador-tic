
import os
import hashlib
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from flask import request
from upstash_redis import Redis


LIMITE_DIARIO = 2
ZONA_HORARIA = ZoneInfo("America/Mexico_City")

MENSAJE_LIMITE = (
    "Has alcanzado tu límite de peticiones del día de hoy. "
    "Vuelve mañana para volver a utilizarlo."
)


def comprobar_limite_diario():
    # Credenciales privadas de Upstash
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

    redis = Redis(url=url, token=token)

    # Obtener la IP desde el proxy de Vercel
    if os.getenv("VERCEL"):
        ip = request.headers.get("x-vercel-forwarded-for", "")
        ip = ip.split(",")[0].strip()
    else:
        ip = request.remote_addr

    if not ip:
        raise RuntimeError("No se pudo identificar la IP")

    # Obtener fecha y hora de México
    ahora = datetime.now(ZONA_HORARIA)
    fecha = ahora.strftime("%Y-%m-%d")

    # Evitar guardar la IP directamente
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    clave = f"radar_tic:limite:{fecha}:{ip_hash}"

    # Calcular los segundos hasta mañana
    manana = datetime.combine(
        ahora.date() + timedelta(days=1),
        time.min,
        tzinfo=ZONA_HORARIA
    )

    segundos = max(
        1,
        int((manana - ahora).total_seconds())
    )

    # Incrementar y configurar expiración de forma atómica
    transaccion = redis.multi()
    transaccion.incr(clave)
    transaccion.expire(clave, segundos)

    resultados = transaccion.exec()
    total = int(resultados[0])

    return total <= LIMITE_DIARIO, segundos
