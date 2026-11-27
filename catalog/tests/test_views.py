from decimal import Decimal

from django.test import RequestFactory, TestCase

from catalog.models import Book, Category
from catalog.views import _filter_books


class CatalogFilterTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.ficcion = Category.objects.create(name="Ficción", slug="ficcion")
        self.academicos = Category.objects.create(name="Académicos", slug="academicos")
        self.garcia = Book.objects.create(
            title="Cien años de soledad",
            author="Gabriel García Márquez",
            price=Decimal("45000"),
            condition=Book.Condition.COMO_NUEVO,
            category=self.ficcion,
            slug="cien-anos",
        )
        Book.objects.create(
            title="Manual de Django",
            author="Equipo Dev",
            price=Decimal("60000"),
            condition=Book.Condition.NUEVO,
            category=self.academicos,
            slug="manual-django",
        )
        Book.objects.create(
            title="Novela barata",
            author="Autor X",
            price=Decimal("15000"),
            condition=Book.Condition.ACEPTABLE,
            category=self.ficcion,
            slug="novela-barata",
        )

    def _filtered_ids(self, query_string):
        request = self.factory.get("/catalog/", query_string)
        qs, _ = _filter_books(request)
        return set(qs.values_list("pk", flat=True))

    def test_search_by_title(self):
        ids = self._filtered_ids({"q": "soledad"})
        self.assertEqual(ids, {self.garcia.pk})

    def test_search_by_author(self):
        ids = self._filtered_ids({"q": "García"})
        self.assertEqual(ids, {self.garcia.pk})

    def test_filter_by_category(self):
        ids = self._filtered_ids({"category": "academicos"})
        self.assertEqual(len(ids), 1)
        self.assertNotIn(self.garcia.pk, ids)

    def test_filter_by_price_range(self):
        ids = self._filtered_ids({"price_min": "20000", "price_max": "50000"})
        self.assertEqual(ids, {self.garcia.pk})

    def test_invalid_prices_are_ignored(self):
        all_ids = self._filtered_ids({})
        for value in ("abc", "NaN", "Infinity", "-Infinity", "-5000"):
            with self.subTest(value=value):
                self.assertEqual(self._filtered_ids({"price_min": value}), all_ids)
                self.assertEqual(self._filtered_ids({"price_max": value}), all_ids)

    def test_price_range_is_swapped_when_min_greater_than_max(self):
        ids = self._filtered_ids({"price_min": "50000", "price_max": "20000"})
        self.assertEqual(ids, {self.garcia.pk})

    def test_index_with_invalid_price_does_not_fail(self):
        response = self.client.get("/catalog/", {"price_min": "NaN", "price_max": "Infinity"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cien años de soledad")

    def test_filter_by_condition(self):
        ids = self._filtered_ids({"condition": "aceptable"})
        self.assertEqual(len(ids), 1)
        self.assertNotIn(self.garcia.pk, ids)

    def test_index_lists_books(self):
        response = self.client.get("/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cien años de soledad")

    def test_index_search_via_query_param(self):
        response = self.client.get("/catalog/", {"q": "García"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cien años de soledad")
        self.assertNotContains(response, "Manual de Django")
