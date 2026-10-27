"""管理端接口（全部需要管理员角色）。"""
from ..common import parse_path_int, read_json_body, require_method
from ..decorators import api_view, require_admin
from ..services import admin_service


@api_view
@require_admin
def poets(request):
    if request.method == "GET":
        return admin_service.list_poets()
    if request.method == "POST":
        return admin_service.add_poet(read_json_body(request))
    require_method(request, "GET", "POST")
    return None


@api_view
@require_admin
def poet_detail(request, poet_id):
    poet_id = parse_path_int(poet_id, "poetId")
    if request.method == "PUT":
        admin_service.update_poet(poet_id, read_json_body(request))
        return None
    if request.method == "DELETE":
        admin_service.delete_poet(poet_id)
        return None
    require_method(request, "PUT", "DELETE")
    return None


@api_view
@require_admin
def poems(request):
    require_method(request, "POST")
    return admin_service.add_poem(read_json_body(request))


@api_view
@require_admin
def poem_detail(request, poem_id):
    poem_id = parse_path_int(poem_id, "poemId")
    if request.method == "PUT":
        admin_service.update_poem(poem_id, read_json_body(request))
        return None
    if request.method == "DELETE":
        admin_service.delete_poem(poem_id)
        return None
    require_method(request, "PUT", "DELETE")
    return None


@api_view
@require_admin
def poem_status(request, poem_id):
    require_method(request, "PUT")
    poem_id = parse_path_int(poem_id, "poemId")
    admin_service.change_publication_status(poem_id, request.GET.get("value"))
    return None


@api_view
@require_admin
def collections(request):
    if request.method == "GET":
        return admin_service.list_collections()
    if request.method == "POST":
        admin_service.add_collection(read_json_body(request))
        return None
    require_method(request, "GET", "POST")
    return None


@api_view
@require_admin
def collection_detail(request, collection_id):
    collection_id = parse_path_int(collection_id, "collectionId")
    if request.method == "PUT":
        admin_service.update_collection(collection_id, read_json_body(request))
        return None
    if request.method == "DELETE":
        admin_service.delete_collection(collection_id)
        return None
    require_method(request, "PUT", "DELETE")
    return None


@api_view
@require_admin
def genres(request):
    require_method(request, "POST")
    return admin_service.add_genre(read_json_body(request))


@api_view
@require_admin
def genre_detail(request, genre_id):
    genre_id = parse_path_int(genre_id, "genreId")
    if request.method == "PUT":
        admin_service.update_genre(genre_id, read_json_body(request))
        return None
    if request.method == "DELETE":
        admin_service.delete_genre(genre_id)
        return None
    require_method(request, "PUT", "DELETE")
    return None
