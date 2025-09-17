from django.db import models
from django.db.models import Sum

class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_de_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_de_venta = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, related_name='productos')

    def __str__(self):
        return self.nombre

    def stock_total(self):
        return self.inventario.aggregate(total=Sum('cantidad'))['total'] or 0

    def esta_bajo_stock(self):
        stock_minimo = 10
        return self.stock_total() < stock_minimo

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre} en {self.almacen.nombre}"

    def agregar_stock(self, cantidad):
        self.cantidad += cantidad
        self.save()
        Transaccion.objects.create(
            producto=self.producto,
            tipo_de_transaccion='ENTRADA',
            cantidad=cantidad,
            almacen=self.almacen
        )

    def quitar_stock(self, cantidad):
        if self.cantidad >= cantidad:
            self.cantidad -= cantidad
            self.save()
            Transaccion.objects.create(
                producto=self.producto,
                tipo_de_transaccion='SALIDA',
                cantidad=cantidad,
                almacen=self.almacen
            )
            return True
        return False

class Transaccion(models.Model):
    TIPOS_DE_TRANSACCION = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    tipo_de_transaccion = models.CharField(max_length=10, choices=TIPOS_DE_TRANSACCION)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)