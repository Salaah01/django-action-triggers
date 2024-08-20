.. code-block:: python

  from django.db import models

  class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

  class Product(models.Model):
      name = models.CharField(max_length=255)
      description = models.TextField()


  class Sale(models.Model):
      customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
      product = models.ForeignKey(Product, on_delete=models.CASCADE)
      quantity = models.IntegerField()
