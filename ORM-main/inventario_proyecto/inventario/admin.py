from django.contrib import admin
from .models import Almacen, Proveedor, Producto, Inventario, Transaccion

admin.site.register(Almacen)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Inventario)
admin.site.register(Transaccion)