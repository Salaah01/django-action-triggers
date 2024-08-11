"""Model contains the definitions for models that will be created and used for
testing.
"""

import typing as _t
import random
import string
from django.db import connection, models
from django.contrib.contenttypes.models import ContentType


def generate_random_string() -> str:
    """Generates a random string."""
    return "".join(
        random.choice(string.ascii_letters)
        for _ in range(random.randint(3, 10))
    )


def generate_random_email() -> str:
    """Generates a random email."""
    return f"{generate_random_string()}@{generate_random_string()}.com"


class BaseModel(models.Model):
    """A base model used for testing purposes. It contains helper methods to
    manage the schema and records.
    """

    ct_app_label = "action_triggers"
    ct_model: str

    class Meta:
        abstract = True

    @classmethod
    def create_table(cls) -> None:
        """Creates the table in the database."""
        if cls._meta.db_table not in connection.introspection.table_names():
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(cls)
            ContentType.objects.get_or_create(
                app_label=cls.ct_app_label,
                model=cls.ct_model,
            )

    @classmethod
    def drop_table(cls) -> None:
        """Drops the table from the database."""
        if cls._meta.db_table in connection.introspection.table_names():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DROP TABLE IF EXISTS {};".format(cls._meta.db_table)
                )
            ContentType.objects.filter(
                app_label=cls.ct_app_label,
                model=cls.ct_model,
            ).delete()


class CustomerModel(BaseModel):
    """A model used to testing purposes. It will imitate a customer model."""

    name = models.CharField(max_length=200, default=generate_random_string)
    email = models.EmailField(default=generate_random_email)

    @classmethod
    def create_record(cls) -> "CustomerModel":
        """Creates a record in the database."""
        rec = cls.objects.create()
        rec.save()
        return rec


class CustomerOrderModel(BaseModel):
    """A model used to testing purposes. It will imitate a customer order
    model.
    """

    customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    order_number = models.CharField(
        max_length=100, default=generate_random_string, null=True, blank=True
    )

    @classmethod
    def create_record(cls, customer: CustomerModel) -> "CustomerOrderModel":
        """Creates a record in the database."""
        rec = cls.objects.create(customer=customer)
        rec.save()
        return rec


class M2MModel(BaseModel):
    """A model used to testing purposes. It will imitate a many-to-many
    model.
    """

    ct_model = "m2mmodel"

    customers = models.ManyToManyField(
        CustomerModel,
        related_name="fav_colours",
    )
    fav_colour = models.CharField(
        max_length=50,
        default=generate_random_string,
    )

    @classmethod
    def create_record(cls, customers: _t.List[CustomerModel]) -> "M2MModel":
        """Creates a record in the database."""
        rec = cls.objects.create(fav_colour=generate_random_string())
        rec.customers.set(customers)
        rec.save()
        return rec


class One2OneModel(models.Model):
    """A model used to testing purposes. It will imitate a one-to-one
    relation.
    """

    ct_model = "one2onemodel"

    customer = models.OneToOneField(CustomerModel, on_delete=models.CASCADE)
    age = models.IntegerField(default=10)

    @classmethod
    def create_record(cls, customer: CustomerModel) -> "One2OneModel":
        """Creates a record in the database."""
        rec = cls.objects.create(customer=customer)
        rec.save()
        return rec
