from django.contrib import admin
from sample_app.models import Customer


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
