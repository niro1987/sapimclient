"""Tests for SAP Incentive Management model.base module."""

from enum import StrEnum
from typing import ClassVar

import pytest
from pydantic import AliasChoices, Field
from pydantic_core import ValidationError

from sapimclient.model import BusinessUnit, base as model_base


def test_basemodel() -> None:
    """Test _BaseModel class."""

    class DummyModel(model_base._BaseModel):
        """Dummy model for testing."""

        dummy_str: str | None = None

    # Test strip whitespace
    dummy_model = DummyModel(dummy_str='  spam  ')
    assert dummy_model.dummy_str == 'spam'

    # Test min length
    with pytest.raises(ValidationError) as err:
        dummy_model = DummyModel(dummy_str='')
    assert 'dummy_str' in str(err.value)

    # Test extra
    dummy_model = DummyModel(dummy_str='spam', dummy_int=42)
    assert dummy_model.dummy_str == 'spam'
    assert 'dummy_int' in dummy_model.model_extra
    assert dummy_model.model_extra['dummy_int'] == 42
    assert dummy_model.dummy_int == 42

    # Test alias generator
    field_info = DummyModel.model_fields['dummy_str']
    assert field_info.alias == 'dummyStr'

    # Test populate by alias
    dummy_model = DummyModel(dummyStr='spam')
    assert dummy_model.dummy_str == 'spam'

    # Test populate by name
    dummy_model = DummyModel(dummy_str='spam')
    assert dummy_model.dummy_str == 'spam'

    class DummyEnum(StrEnum):
        """Dummy enum for testing."""

        SPAM = 'spam'
        EGGS = 'eggs'

    class DummyEnumModel(model_base._BaseModel):
        """Test use of enum values."""

        dummy_str: DummyEnum

    # Test use enum values
    dummy_model = DummyEnumModel(dummy_str=DummyEnum.SPAM)
    assert dummy_model.dummy_str == 'spam'

    with pytest.raises(ValidationError) as err:
        dummy_model = DummyEnumModel(dummy_str='bacon')

    # Test validate assignment
    dummy_model = DummyModel(dummy_str='spam')
    assert dummy_model.dummy_str == 'spam'
    with pytest.raises(ValidationError) as err:
        dummy_model.dummy_str = 42


def test_basemodel_typed_fields() -> None:
    """Test _BaseModel.typed_fields function."""

    class DummyModel(model_base._BaseModel):
        """Dummy model for testing."""

        dummy_str: str
        dummy_int: int
        dummy_str_int: str | int
        dummy_list_str: list[str]
        dummy_list_str_int: list[str | int]

    str_fields = DummyModel.typed_fields(str)
    assert 'dummy_str' in str_fields
    assert 'dummy_int' not in str_fields
    assert 'dummy_str_int' in str_fields
    assert 'dummy_list_str' in str_fields
    assert 'dummy_list_str_int' in str_fields

    int_fields = DummyModel.typed_fields(int)
    assert 'dummy_str' not in int_fields
    assert 'dummy_int' in int_fields
    assert 'dummy_str_int' in int_fields
    assert 'dummy_list_str' not in int_fields
    assert 'dummy_list_str_int' in int_fields


def test_endpoint() -> None:
    """Test Endpoint class."""

    class DummyEndpoint(model_base.Endpoint):
        """Dummy endpoint for testing."""

        attr_endpoint: ClassVar[str] = 'dummyEndpoint'
        expandable: model_base.Expandable

    assert 'attr_endpoint' in model_base.Endpoint.__annotations__
    assert DummyEndpoint.attr_endpoint == 'dummyEndpoint'

    # Test expands
    dummy_endpoint = DummyEndpoint(expandable=model_base.Expandable())
    assert 'expandable' in dummy_endpoint.expands()


def test_resource() -> None:
    """Test Resource class."""

    class DummyResource(model_base.Resource):
        """Dummy resource for testing."""

        attr_seq: ClassVar[str] = 'dummy_seq'
        dummy_seq: str | None = None

    assert issubclass(model_base.Resource, model_base.Endpoint)
    assert 'attr_seq' in model_base.Resource.__annotations__
    assert DummyResource.attr_seq == 'dummy_seq'

    dummy_resource = DummyResource(dummy_seq='spam')
    assert dummy_resource.dummy_seq == 'spam'

    # Test seq
    assert dummy_resource.seq == 'spam'


def test_resource_alias_override() -> None:
    """Test resource alias override."""

    class DummyResource(model_base.Resource):
        """Dummy model."""

        dummy_code_id: str = Field(
            validation_alias=AliasChoices('dummyCodeId', 'ID'),
        )

    dummy: DummyResource = DummyResource(dummyCodeId='spam')
    assert dummy.dummy_code_id == 'spam'
    dump: dict[str, str] = dummy.model_dump(by_alias=True, exclude_none=True)
    assert dump == {'dummyCodeId': 'spam'}

    dummy2: DummyResource = DummyResource(ID='eggs')
    assert dummy2.dummy_code_id == 'eggs'
    dump2: dict[str, str] = dummy2.model_dump(by_alias=True, exclude_none=True)
    assert 'ID' not in dump2
    assert dump == {'dummyCodeId': 'spam'}


def test_reference() -> None:
    """Test Reference class."""
    assert issubclass(model_base.Reference, model_base.Expandable)
    assert 'key' in model_base.Reference.model_fields
    assert 'display_name' in model_base.Reference.model_fields
    assert 'object_type' in model_base.Reference.model_fields
    assert 'logical_keys' in model_base.Reference.model_fields

    # Test field validator
    class DummyModel(model_base.Resource):
        """Dummy model for testing."""

        business_unit: model_base.Reference
        business_units: list[model_base.Reference]

    model_data = {
        'business_unit': {
            'key': '123',
            'display_name': 'spam',
            'object_type': 'BusinessUnit',
            'logical_keys': {'name': 'spam'},
        },
        'business_units': [
            {
                'key': '456',
                'display_name': 'eggs',
                'object_type': 'BusinessUnit',
                'logical_keys': {'name': 'eggs'},
            },
        ],
    }
    dummy_model = DummyModel(**model_data)
    assert dummy_model.business_unit.key == '123'
    assert str(dummy_model.business_unit) == '123'
    assert dummy_model.business_unit.object_type is BusinessUnit
    assert dummy_model.business_unit.logical_keys['name'] == 'spam'

    assert dummy_model.business_units[0].key == '456'
    assert str(dummy_model.business_units[0]) == '456'
    assert dummy_model.business_units[0].object_type is BusinessUnit
    assert dummy_model.business_units[0].logical_keys['name'] == 'eggs'


def test_reference_string() -> None:
    """Test reference field as string."""

    class DummyResource(model_base.Resource):
        """Dummy model."""

        id: str
        reference: str | model_base.Reference

    dummy: DummyResource = DummyResource(id='spamm', reference='eggs')
    assert dummy.id == 'spamm'
    assert isinstance(dummy.reference, str)
    assert dummy.reference == 'eggs'


def test_reference_unknown_resource() -> None:
    """Test Reference class with unkown resource class."""

    class DummyModel(model_base.Resource):
        """Dummy model for testing."""

        business_unit: model_base.Reference

    # Test reference must be a subclass of Resource
    model_data = {
        'business_unit': {
            'key': '123',
            'display_name': 'spam',
            'object_type': 'UnknownResource',
            'logical_keys': {'name': 'spam'},
        },
    }

    with pytest.raises(ValidationError) as err:
        _ = DummyModel(**model_data)
    assert 'Could not find object type: UnknownResource' in str(err.value)

    # Test reference must not be class Resource
    model_data = {
        'business_unit': {
            'key': '123',
            'display_name': 'spam',
            'object_type': 'Resource',
            'logical_keys': {'name': 'spam'},
        },
    }

    with pytest.raises(ValidationError) as err:
        _ = DummyModel(**model_data)
    assert 'Object type is not a subclass of Resource: Resource' in str(err.value)

    # Test reference must be a subclass of Resource even if imported from module
    model_data = {
        'business_unit': {
            'key': '123',
            'display_name': 'spam',
            'object_type': 'Value',
            'logical_keys': {'name': 'spam'},
        },
    }

    with pytest.raises(ValidationError) as err:
        _ = DummyModel(**model_data)
    assert 'Object type is not a subclass of Resource: Value' in str(err.value)
