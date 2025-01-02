"""Measurement."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin, Value

from ._base import GCPReference, GCPResource
from .participant import Participant
from .period import Period
from .position import Position
from .rule import Rule


class Measurement(GCPResource, Generic16Mixin):
    """Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/measurements'
    attr_seq: ClassVar[str] = 'measurement_seq'
    measurement_seq: str | None = None
    name: str
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    rule: GCPReference[Rule] | str | None = None
    value: Value
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    number_of_credits: Value
    is_private: bool | None = None
    processing_unit: str | None = None
    business_units: list[str] | None = None


class PrimaryMeasurement(Measurement):
    """Primary Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/primaryMeasurements'


class SecondaryMeasurement(Measurement):
    """Secondary Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/secondaryMeasurements'
