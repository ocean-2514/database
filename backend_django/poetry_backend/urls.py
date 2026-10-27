from django.urls import include, path

urlpatterns = [
    path("api/", include("api.urls")),
]

handler404 = "api.views.errors.not_found"
handler500 = "api.views.errors.server_error"
