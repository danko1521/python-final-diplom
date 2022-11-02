from django.contrib.auth.models import User, Contact
from django.db import models


# Create your models here.

# модель магазина
class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка на сайт', blank=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


# модель категорий
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'категории'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


# модель продукта
class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='название')
    category = models.ForeignKey(Category,
                                 verbose_name='название',
                                 related_name='products',
                                 blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


# модель информации о продукте
class ProductInfo(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name='Продукт',
                                related_name='product_infos',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='product_infos',
                             blank=True,
                             on_delete=models.CASCADE
                             )

    model = models.CharField(max_length=50, verbose_name='модель', blank=True)
    article = models.PositiveIntegerField(verbose_name='артикул')
    quantity = models.PositiveIntegerField(verbose_name='кол-во')
    price = models.PositiveIntegerField(verbose_name='цена')
    price_rrc = models.PositiveIntegerField(verbose_name='рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'информация о продукте'
        verbose_name_plural = 'информация о продуктах'
        # исключения в базе
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info')
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Параметры'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='информация о продукте',
                                     related_name='product_parameter',
                                     on_delete=models.CASCADE,
                                     blank=True
                                     )
    parameter = models.ForeignKey(Product,
                                  verbose_name='параметр',
                                  related_name='product_parameter',
                                  on_delete=models.CASCADE,
                                  blank=True)
    value = models.CharField(max_length=50, verbose_name='значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='orders',
                             blank=True, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, verbose_name='Контакт', related_name='orders', blank=True, null=True,
                                on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, verbose_name='Статус', choices=STATE_CHOICES)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-dt',)

    def __str__(self):
        return f'{self.user} - {self.dt}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items',
                                     blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    total_amount = models.PositiveIntegerField(default=0, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')
        ]

    def __str__(self):
        return f'№ {self.order} - {self.product_info.model}: {self.quantity} * {self.price} = {self.total_amount}'

    def save(self, *args, **kwargs):
        self.total_amount = self.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)
