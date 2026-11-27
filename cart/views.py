from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Book

from .cart import MAX_QTY_PER_BOOK, Cart


def _get_cart(request):
    return Cart(request.session)


def _is_ajax(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    accept = request.headers.get("Accept", "")
    return "application/json" in accept


INVALID_QTY_MESSAGE = "Cantidad no válida."
LIMIT_QTY_MESSAGE = f"Puedes llevar máximo {MAX_QTY_PER_BOOK} unidades de cada libro."


def _parse_quantity(value, default=None):
    """Convierte la cantidad enviada a entero; retorna `default` si no es un entero."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _format_cop(amount):
    """Formatea Decimal como pesos colombianos sin decimales."""
    if amount is None:
        return "$0"
    quantized = Decimal(amount).quantize(Decimal("1"))
    return f"${quantized:,.0f}"


def _json_payload(cart, *, message="", line_subtotal=None, in_cart=None, quantity=None, limited=False):
    payload = {
        "count": len(cart),
        "total": str(cart.total_price),
        "total_formatted": _format_cop(cart.total_price),
        "message": message,
        "limited": limited,
        "max_quantity": MAX_QTY_PER_BOOK,
    }
    if quantity is not None:
        payload["quantity"] = quantity
    if line_subtotal is not None:
        payload["line_subtotal"] = str(line_subtotal)
        payload["line_subtotal_formatted"] = _format_cop(line_subtotal)
    if in_cart is not None:
        payload["in_cart"] = in_cart
    return payload


def _redirect_back(request, fallback="cart:detail"):
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect(fallback)


@require_POST
def add(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart = _get_cart(request)
    qty = max(1, _parse_quantity(request.POST.get("quantity"), default=1))
    limited = False

    if cart.contains(book):
        message = "Ya en el carrito"
        added = False
    else:
        cart.add(book, qty=qty)
        added = True
        limited = qty > MAX_QTY_PER_BOOK
        message = f"«{book.title}» se añadió al carrito."
        if limited:
            message = f"{message} {LIMIT_QTY_MESSAGE}"

    if _is_ajax(request):
        return JsonResponse(
            _json_payload(
                cart,
                message=message,
                line_subtotal=cart.line_subtotal(book),
                in_cart=True,
                quantity=cart.get_quantity(book),
                limited=limited,
            )
        )

    if added and not limited:
        messages.success(request, message)
    else:
        messages.warning(request, message)
    return _redirect_back(request, fallback=book.get_absolute_url())


@require_POST
def update(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart = _get_cart(request)
    qty = _parse_quantity(request.POST.get("quantity"))

    if qty is None:
        if _is_ajax(request):
            return JsonResponse(
                _json_payload(
                    cart,
                    message=INVALID_QTY_MESSAGE,
                    line_subtotal=cart.line_subtotal(book),
                    in_cart=cart.contains(book),
                ),
                status=400,
            )
        messages.error(request, INVALID_QTY_MESSAGE)
        return redirect("cart:detail")

    cart.update(book, qty)
    limited = qty > MAX_QTY_PER_BOOK and cart.contains(book)

    if _is_ajax(request):
        if cart.contains(book):
            line_subtotal = cart.line_subtotal(book)
            message = LIMIT_QTY_MESSAGE if limited else "Cantidad actualizada."
        else:
            line_subtotal = Decimal("0")
            message = "Ítem eliminado del carrito."
        return JsonResponse(
            _json_payload(
                cart,
                message=message,
                line_subtotal=line_subtotal,
                in_cart=cart.contains(book),
                quantity=cart.get_quantity(book),
                limited=limited,
            )
        )

    if limited:
        messages.warning(request, LIMIT_QTY_MESSAGE)
    elif cart.contains(book):
        messages.success(request, "Cantidad actualizada.")
    else:
        messages.success(request, f"«{book.title}» se eliminó del carrito.")
    return redirect("cart:detail")


@require_POST
def remove(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart = _get_cart(request)
    cart.remove(book)
    message = f"«{book.title}» se eliminó del carrito."

    if _is_ajax(request):
        return JsonResponse(
            _json_payload(
                cart,
                message=message,
                line_subtotal=Decimal("0"),
                in_cart=False,
            )
        )

    messages.success(request, message)
    return redirect("cart:detail")


def detail(request):
    cart = _get_cart(request)
    cart_items = list(cart)
    context = {
        "cart_items": cart_items,
        "cart_total": cart.total_price,
        "cart_is_empty": len(cart_items) == 0,
        "max_qty_per_book": MAX_QTY_PER_BOOK,
    }
    return render(request, "cart/detail.html", context)
