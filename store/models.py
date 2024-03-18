from django.db import models
from django.urls import reverse

from category.models import Category
from accounts.models import Account


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        # return reverse('product_detail', args=[self.category__slug, self.slug])
        return reverse('product_detail', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug,
        })

    def __str__(self):
        return self.product_name
    
    
class Variation(models.Model):
    
    variation_category_choices = (
        ("color", "color"),
        ("size", "size"),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.product)
