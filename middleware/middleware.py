from time import perf_counter
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class HiByeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f'hi - {request.url}')
        start_time = perf_counter()
        response = await call_next(request)
        process_time = perf_counter() - start_time

        print(f"bye (took {process_time:.4f} seconds)")
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response
    