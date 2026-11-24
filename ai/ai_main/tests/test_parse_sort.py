"""app.search.parse_sort 단위 테스트. OpenSearch·모델 없이 돈다(pydantic, pytest 만 필요).

실행: ai/ai_main 에서 `python -m pytest tests`
"""

import pytest

from app.search import LIST_SORTS, SEARCH_SORTS, InvalidSortError, parse_sort

TIE = {"image_id": {"order": "desc"}}


@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("createdAt,desc", [{"created_at": {"order": "desc"}}, TIE]),
        ("createdAt,asc", [{"created_at": {"order": "asc"}}, TIE]),
        ("uploadedAt,desc", [{"uploaded_at": {"order": "desc", "missing": "_last"}}, TIE]),
        ("lastViewedAt,desc", [{"last_viewed_at": {"order": "desc", "missing": "_last"}}, TIE]),
        # imageId 정렬은 그 자체가 동률 해소 기준이라 뒤에 덧붙이지 않는다.
        ("imageId,asc", [{"image_id": {"order": "asc"}}]),
        ("imageId,desc", [{"image_id": {"order": "desc"}}]),
        ("  createdAt,asc  ", [{"created_at": {"order": "asc"}}, TIE]),
    ],
)
def test_list_sorts(sort, expected):
    assert parse_sort(sort, LIST_SORTS, "createdAt,desc") == expected


@pytest.mark.parametrize("sort", [None, ""])
def test_missing_sort_uses_default(sort):
    assert parse_sort(sort, LIST_SORTS, "createdAt,desc") == [{"created_at": {"order": "desc"}}, TIE]


def test_relevance():
    expected = [{"_score": {"order": "desc"}}, TIE]
    assert parse_sort("relevance", SEARCH_SORTS, "relevance") == expected
    assert parse_sort(None, SEARCH_SORTS, "relevance") == expected


def test_direction_defaults_to_desc():
    assert parse_sort("createdAt", {"createdAt"}, "createdAt") == [{"created_at": {"order": "desc"}}, TIE]


@pytest.mark.parametrize(
    ("sort", "allowed"),
    [
        ("relevance", LIST_SORTS),          # 목록 API 는 relevance 를 받지 않는다
        ("createdAt,asc", SEARCH_SORTS),    # 허용 목록 밖
        ("createdAt,DESC", LIST_SORTS),     # 대소문자 구분
        ("title,desc", LIST_SORTS),
        ("createdAt,up", {"createdAt,up"}),  # 허용 목록에 있어도 방향이 틀리면 거부
        ("title,desc", {"title,desc"}),      # 허용 목록에 있어도 필드가 없으면 거부
    ],
)
def test_invalid_sort_raises(sort, allowed):
    with pytest.raises(InvalidSortError):
        parse_sort(sort, allowed, "createdAt,desc")
