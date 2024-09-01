from sample_app.models import Customer, Product, Sale
from django.contrib import admin


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone",
        "address",
        "city",
        "state",
        "country",
        "zip",
    ]
