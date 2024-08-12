"""Test for the `payload` module."""

from functools import partial
import json
from copy import deepcopy

import pytest
from model_bakery import baker

from action_triggers.payload import (
    parse_payload,
    payload_from_instance,
    payload_generator,
)
from tests.models import (
    CustomerModel,
    CustomerOrderModel,
    M2MModel,
    One2OneModel,
)
from action_triggers.models import Config


class TestParsePayload:
    """Tests for the `parse_payload` function."""

    def test_original_payload_is_not_mutated(self):
        """Test that the original payload is not mutated."""

        payload = json.dumps({"name": "{{ instance.name }}"})
        original_payload = deepcopy(payload)
        instance = baker.make(CustomerModel)
        result = parse_payload(instance, payload)

        assert payload == original_payload
        assert result != original_payload

    @pytest.mark.parametrize(
        "model_class",
        (CustomerModel, CustomerOrderModel, M2MModel, One2OneModel),
    )
    def test_parse_payload_with_plain_dict(self, model_class):
        """Test parsing a plain dictionary."""
        payload = {
            "name": "John Doe",
            "email": "john.doe@exmaple.com",
            "phone": 123,
        }
        parsed_payload = parse_payload(
            baker.make(model_class), json.dumps(payload)
        )
        assert parsed_payload == payload

    @pytest.mark.parametrize(
        "model_class,field_name",
        (
            (CustomerModel, "name"),
            (CustomerOrderModel, "order_number"),
            (M2MModel, "fav_colour"),
            (One2OneModel, "age"),
        ),
    )
    def test_parse_payload_with_reference(self, model_class, field_name):
        """Test parsing a payload with a 0-level deep reference."""
        payload = {
            "plain_text": "a plain text",
            "reference": f"{{{{ instance.{field_name} }}}}",
        }

        instance = baker.make(model_class)
        result = parse_payload(instance, json.dumps(payload))

        assert result["plain_text"] == payload["plain_text"]
        assert result["reference"] == str(getattr(instance, field_name))

    @pytest.mark.parametrize(
        "model_class,field_name",
        (
            (CustomerModel, "name"),
            (CustomerOrderModel, "order_number"),
            (M2MModel, "fav_colour"),
            (One2OneModel, "age"),
        ),
    )
    def test_parse_support_non_json_serializable_objects(
        self, model_class, field_name
    ):
        instance = baker.make(model_class)
        payload = f"{{{{ instance.{field_name} }}}}"
        result = parse_payload(instance, payload)

        assert result == getattr(instance, field_name)

    def test_parse_payload_with_nested_reference_12m_field(self):
        instance = baker.make(CustomerOrderModel)
        payload = json.dumps(
            {
                "customer": {
                    "id": "{{ instance.customer.id }}",
                    "name": "{{ instance.customer.name }}",
                },
                "order_number": "{{ instance.order_number }}",
            }
        )
        result = parse_payload(instance, payload)

        assert result == {
            "customer": {
                "id": str(instance.customer.id),
                "name": instance.customer.name,
            },
            "order_number": instance.order_number,
        }

    def test_parse_payload_with_nested_reference_121_field(self):
        instance = baker.make(One2OneModel)
        payload = json.dumps(
            {
                "customer": {
                    "id": "{{ instance.customer.id }}",
                    "name": "{{ instance.customer.name }}",
                },
                "age": "{{ instance.age }}",
            }
        )
        result = parse_payload(instance, payload)

        assert result == {
            "customer": {
                "id": str(instance.customer.id),
                "name": instance.customer.name,
            },
            "age": str(instance.age),
        }

    def test_parse_payload_with_nested_reference_m2m_field(self):
        customer_1, customer_2 = baker.make(CustomerModel, _quantity=2)
        instance = baker.make(M2MModel, customers=[customer_1, customer_2])
        payload = """
            {
                "fav_colour": "{{ instance.fav_colour }}",
                "customers": [
                    {% for customer in instance.customers.all %}
                        {
                            "id": "{{ customer.id }}",
                            "name": "{{ customer.name }}"
                        }{% if not forloop.last %},{% endif %}
                    {% endfor %}
                ]
            }
        """

        result = parse_payload(instance, payload)

        assert result == {
            "fav_colour": instance.fav_colour,
            "customers": [
                {"id": str(customer_1.id), "name": customer_1.name},
                {"id": str(customer_2.id), "name": customer_2.name},
            ],
        }


class TestPayloadFromInstance:
    """Tests for the `payload_from_instance` function."""

    def test_from_12m_instance_creates_json_serializable_obj(self):
        instance = baker.make(CustomerOrderModel)
        payload = payload_from_instance(instance)

        json.dumps(payload)
        assert payload == {
            "customer": instance.customer_id,
            "order_number": instance.order_number,
        }

    def test_from_121_creates_json_serializable_obj(self):
        instance = baker.make(One2OneModel)
        payload = payload_from_instance(instance)

        json.dumps(payload)
        assert payload == {
            "customer": instance.customer.id,
            "age": instance.age,
        }

    def test_from_m2m_creates_json_serializable_obj(self):
        customer_1, customer_2 = baker.make(CustomerModel, _quantity=2)
        instance = baker.make(M2MModel, customers=[customer_1, customer_2])
        payload = payload_from_instance(instance)

        json.dumps(payload)
        assert payload == {
            "fav_colour": instance.fav_colour,
            "customers": [customer_1.id, customer_2.id],
        }


class TestPayloadGenerator:
    """Tests for the `payload_generator` function."""

    def test_returns_parse_payload_function_when_config_has_payload(self):
        config = baker.make(Config, payload={"key": "value"})
        result = payload_generator(config)

        isinstance(result, partial)
        assert result.func == parse_payload

    def test_returns_payload_from_instance_function_when_config_has_no_payload(
        self,
    ):
        config = baker.make(Config)
        result = payload_generator(config)

        assert result is payload_from_instance
