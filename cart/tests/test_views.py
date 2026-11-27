from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from cart.cart import CART_SESSION_KEY
from catalog.models import Book, Category


class CartUpdateViewTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Ficción", slug="ficcion")
        self.book = Book.objects.create(
            title="Libro de prueba",
            author="Autor Test",
            price=Decimal("25000"),
            condition=Book.Condition.BUENO,
            category=category,
            slug="libro-prueba",
        )
        self.client.post(reverse("cart:add", args=[self.book.slug]), {"quantity": 2})

    def _cart_quantity(self):
        return self.client.session[CART_SESSION_KEY].get(str(self.book.pk), 0)

    def _update(self, quantity, **extra):
        return self.client.post(
            reverse("cart:update", args=[self.book.slug]), {"quantity": quantity}, **extra
        )

    def test_invalid_quantity_keeps_item(self):
        response = self._update("abc", follow=True)
        self.assertEqual(self._cart_quantity(), 2)
        self.assertContains(response, "Cantidad no válida.")

    def test_invalid_quantity_ajax_returns_400(self):
        response = self._update("abc", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.json()["in_cart"])
        self.assertEqual(self._cart_quantity(), 2)

    def test_zero_quantity_removes_item(self):
        self._update("0")
        self.assertNotIn(str(self.book.pk), self.client.session[CART_SESSION_KEY])

    def test_valid_quantity_updates_item(self):
        self._update("3")
        self.assertEqual(self._cart_quantity(), 3)
