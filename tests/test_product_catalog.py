"""제품 셀링 포인트 매핑 테이블 테스트 - TDD 선행 작성"""
import pytest

from src.data_preprocessing.product_catalog import ProductCatalog


@pytest.fixture
def catalog():
    return ProductCatalog()


class TestProductCatalog:
    def test_catalog_has_three_main_products(self, catalog):
        """주력 3개 제품이 모두 등록되어 있어야 한다."""
        names = catalog.list_product_names()
        assert "하늘천" in names
        assert "따지" in names
        assert "해유기1호" in names

    def test_product_has_npk(self, catalog):
        """각 제품에 N-P-K 성분 정보가 있어야 한다."""
        for name in ["하늘천", "따지", "해유기1호"]:
            product = catalog.get_product(name)
            assert "N" in product["npk"]
            assert "P" in product["npk"]
            assert "K" in product["npk"]

    def test_product_has_selling_points(self, catalog):
        """각 제품에 핵심 셀링 포인트가 1개 이상 있어야 한다."""
        for name in ["하늘천", "따지", "해유기1호"]:
            product = catalog.get_product(name)
            assert len(product["selling_points"]) >= 1

    def test_product_has_four_mu(self, catalog):
        """4無 공법 항목이 제품에 포함되어야 한다."""
        product = catalog.get_product("하늘천")
        assert "four_mu" in product
        assert set(product["four_mu"]) == {"무항생제", "무염분", "무가스", "무취"}

    def test_product_has_category(self, catalog):
        """제품별 카테고리(유기질비료/미생물제제 등)가 있어야 한다."""
        for name in ["하늘천", "따지", "해유기1호"]:
            product = catalog.get_product(name)
            assert "category" in product
            assert len(product["category"]) > 0

    def test_product_has_shop_links(self, catalog):
        """쿠팡/네이버 쇼핑 링크 필드가 있어야 한다."""
        product = catalog.get_product("하늘천")
        assert "shop_links" in product
        assert "coupang" in product["shop_links"]
        assert "naver" in product["shop_links"]

    def test_get_comparison_table(self, catalog):
        """제품 간 N-P-K 비교 테이블을 생성할 수 있어야 한다."""
        table = catalog.get_comparison_table()
        assert len(table) >= 3
        assert all("name" in row and "npk" in row for row in table)

    def test_get_product_not_found(self, catalog):
        """존재하지 않는 제품 조회 시 None을 반환해야 한다."""
        assert catalog.get_product("없는제품") is None

    def test_search_by_keyword(self, catalog):
        """키워드로 관련 제품을 검색할 수 있어야 한다."""
        results = catalog.search("유기질")
        assert len(results) >= 1
        assert all("name" in r for r in results)
