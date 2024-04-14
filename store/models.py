from django.db import models
from django.urls import reverse
from django.db.models import Avg, Count

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
        
    def average_rating(self):
        # reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        reviews = ReviewRating.objects.aggregate(average=Avg('rating'))
        print(f'---> {reviews}')
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def count_reviews(self):
        reviews = ReviewRating.objects.aggregate(count=Count('review'))
        count = 0
        if reviews['count'] is not None:
            count = str(reviews['count'])
        return count

    def __str__(self):
        return self.product_name
    
 
class VariationManager(models.Manager):
    def all(self):
        return super(VariationManager, self).filter(is_active=True)

    def sizes(self):
        return self.all().filter(variation_category='size', is_active=True)

    def colors(self):
        return self.all().filter(variation_category='color', is_active=True)
    
       
VAR_CATEGORY_CHOICES = (
        ("color", "color"),
        ("size", "size"),
    )

   
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VAR_CATEGORY_CHOICES)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value
    
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject
    
    
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name
    
    class Meta:
        verbose_name = 'product gallery'
        verbose_name_plural = 'product gallery'