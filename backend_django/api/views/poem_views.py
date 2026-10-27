"""公开的诗歌检索、详情、全文检索与流派接口。"""
from ..common import parse_path_int, require_method
from ..decorators import api_view
from ..repositories import genre_repo
from ..services import poem_service


@api_view
def search(request):
    require_method(request, "GET")
    return poem_service.search(request.GET)


@api_view
def fulltext(request):
    require_method(request, "GET")
    return poem_service.fulltext(request.GET.get("keyword"))


@api_view
def detail(request, poem_id):
    require_method(request, "GET")
    return poem_service.detail(parse_path_int(poem_id, "poemId"))


@api_view
def genres(request):
    require_method(request, "GET")
    return genre_repo.list_all()
