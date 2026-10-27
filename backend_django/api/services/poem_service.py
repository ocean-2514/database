"""诗歌检索、详情与全文检索业务。"""
from ..common import normalize_page, page_result, parse_int
from ..exceptions import BadRequest
from ..repositories import poem_repo


def search(params) -> dict:
    keyword = params.get("keyword")
    poet_name = params.get("poetName")
    genre = params.get("genre")
    year_from = parse_int(params.get("yearFrom"), "yearFrom", None)
    year_to = parse_int(params.get("yearTo"), "yearTo", None)
    order_by = parse_int(params.get("orderBy"), "orderBy", None)

    page, page_size = normalize_page(
        parse_int(params.get("page"), "page", 1),
        parse_int(params.get("pageSize"), "pageSize", 10),
    )
    offset = (page - 1) * page_size

    total = poem_repo.count_poems(keyword, poet_name, genre, year_from, year_to)
    rows = (
        []
        if total == 0
        else poem_repo.search_poems(
            keyword, poet_name, genre, year_from, year_to, order_by, offset, page_size
        )
    )
    return page_result(total, page, page_size, rows)


def detail(poem_id: int) -> dict:
    poem = poem_repo.get_poem_detail(poem_id)
    if poem is None:
        # 原实现抛 IllegalArgumentException，最终 code=400
        raise BadRequest(f"诗歌不存在或已下架: id={poem_id}")
    return poem


def fulltext(keyword: str | None) -> list[dict]:
    if keyword is None:
        raise BadRequest("缺少参数: keyword")
    keyword = keyword.strip()
    if not keyword:
        raise BadRequest("检索关键词不能为空")
    return poem_repo.fulltext_search(keyword)
