import psutil
import platform
from fastapi.responses import JSONResponse


def getinfo():
    return JSONResponse(
        {
            "os": platform.system(),
            "os_version": platform.version(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "cpu_cores": psutil.cpu_count(logical=True),
        }
    )
