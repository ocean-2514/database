"""CORS：只放行原项目允许的两个本地前端地址，并支持携带 Cookie。"""
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class CorsMiddleware:
    ALLOWED_ORIGINS = frozenset({
        "http://localhost:5173",
        "http://localhost:3000",
    })

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        is_preflight = request.method == "OPTIONS" and request.path.startswith("/api/")

        if is_preflight:
            status = 200 if origin in self.ALLOWED_ORIGINS else 403
            response = HttpResponse(status=status)
        else:
            response = self.get_response(request)

        if origin in self.ALLOWED_ORIGINS:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = (
                request.headers.get("Access-Control-Request-Headers") or "Content-Type"
            )
            response["Access-Control-Max-Age"] = "3600"
            # 保留 SessionMiddleware 添加的 Vary: Cookie，不要整体覆盖
            patch_vary_headers(response, ("Origin",))

        return response
