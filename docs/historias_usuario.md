# Historias de usuario — Mantenimiento de ComuniApp

Proyecto: ComuniApp, librería virtual comunitaria hecha en Django en el módulo de Análisis y Diseño de Sistemas.
Curso: Mantenimiento de software, Corporación Universitaria Iberoamericana.
Autor: Ángel Udalber Rodríguez Moya.

Cada historia se trabaja en su propia rama `feature/HU-0X-...` que sale de `develop`. Después pasa a `test` para correr las pruebas y, si todo sale bien, se integra en `main`.

| ID | Historia | Tipo de mantenimiento (SWEBOK) | Rama |
| --- | --- | --- | --- |
| HU-01 | Cantidad inválida en el carrito | Correctivo | `feature/HU-01-cantidad-invalida-carrito` |
| HU-02 | Filtros de precio con valores inválidos | Correctivo | `feature/HU-02-filtros-precio` |
| HU-03 | Ordenar por precio de mayor a menor | Perfectivo | `feature/HU-03-orden-precio-desc` |
| HU-04 | Límite de unidades por libro | Preventivo | `feature/HU-04-limite-unidades` |
| HU-05 | Costo de envío configurable y Python 3.13 | Adaptativo | `feature/HU-05-envio-configurable` |

---

## HU-01 — Cantidad inválida en el carrito

**Como** comprador, **quiero** que el libro siga en mi carrito si escribo por error una cantidad que no es un número, **para** no tener que buscarlo y agregarlo otra vez.

Situación actual: si en el campo de cantidad se envía un texto (por ejemplo `abc`), la vista toma el valor 0 y borra el libro del carrito.

Criterios de aceptación:

1. Si la cantidad no es un número entero, el carrito no cambia y se muestra el mensaje "Cantidad no válida".
2. Si la cantidad es 0, el libro se elimina, como ya pasaba.
3. Hay una prueba automática para cada caso.

## HU-02 — Filtros de precio con valores inválidos

**Como** lector, **quiero** que el catálogo ignore los precios mínimo o máximo que no tengan sentido, **para** que la búsqueda no falle ni muestre resultados vacíos sin razón.

Situación actual: el filtro acepta valores como `NaN`, `Infinity` o números negativos, y si el mínimo es mayor que el máximo no aparece ningún libro.

Criterios de aceptación:

1. Los valores no numéricos, `NaN`, `Infinity` y negativos se ignoran.
2. Si el mínimo es mayor que el máximo, se intercambian.
3. Hay pruebas automáticas para estos casos.

## HU-03 — Ordenar por precio de mayor a menor

**Como** lector, **quiero** ordenar el catálogo del precio más alto al más bajo, **para** encontrar rápido las ediciones especiales o de colección.

Criterios de aceptación:

1. El selector "Ordenar por" tiene la opción "Precio (mayor a menor)".
2. Al elegirla, los libros aparecen de mayor a menor precio y se conservan los demás filtros.
3. Hay una prueba automática del orden.

## HU-04 — Límite de unidades por libro

**Como** administrador de la tienda, **quiero** que nadie pueda pedir más de 10 unidades del mismo libro, **para** evitar pedidos con cantidades digitadas por error que luego toca anular.

Criterios de aceptación:

1. El límite se define en una sola constante `MAX_QTY_PER_BOOK = 10`.
2. Si se pide más del límite al agregar o al actualizar, la cantidad queda en 10 y se avisa al usuario.
3. Hay pruebas automáticas del límite.

## HU-05 — Costo de envío configurable y Python 3.13

**Como** responsable del despliegue, **quiero** cambiar el costo de envío con una variable de entorno y correr la aplicación en Python 3.13, **para** adaptarla a una nueva tarifa de la transportadora y a la versión de Python del servidor sin tocar el código.

Criterios de aceptación:

1. `SHIPPING_COST` se lee de la variable de entorno del mismo nombre; si no existe, vale 8000.
2. `.env.example` documenta la variable.
3. `runtime.txt` queda en Python 3.13 y las pruebas pasan en esa versión.
