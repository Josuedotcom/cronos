from __future__ import annotations

import uuid
from datetime import date, time
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator


class WorkerRoleSchema(str, Enum):
    WORKER = "worker"
    MANAGER = "manager"
    HR_ADMIN = "hr_admin"


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    subdomain: str = Field(min_length=1, max_length=100)
    timezone: str = Field(default="America/Bogota")


class CompanyRead(BaseModel):
    id: uuid.UUID
    name: str
    subdomain: str
    timezone: str


class WorkerCreate(BaseModel):
    company_id: uuid.UUID
    suborganization_id: uuid.UUID
    area_id: uuid.UUID
    cedula: str = Field(min_length=3, max_length=20)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    contract_type: str = Field(default="standard")
    hourly_rate: Decimal = Field(gt=0)
    hire_date: date
    role: WorkerRoleSchema = WorkerRoleSchema.WORKER
    password: str = Field(min_length=12, max_length=128)

    @field_validator("contract_type")
    @classmethod
    def validate_contract_type(cls, value: str) -> str:
        allowed = {"standard", "shift_36h"}
        if value not in allowed:
            raise ValueError(f"contract_type must be one of {allowed}")
        return value


class WorkerRead(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    suborganization_id: uuid.UUID
    area_id: uuid.UUID
    cedula: str
    first_name: str
    last_name: str
    email: EmailStr | None = None
    role: WorkerRoleSchema


class ShiftTemplateCreate(BaseModel):
    company_id: uuid.UUID
    suborganization_id: uuid.UUID
    area_id: uuid.UUID
    code: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=100)
    start_time: time
    end_time: time


class ShiftTemplateRead(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    area_id: uuid.UUID
    code: str
    name: str
    start_time: time
    end_time: time


class ShiftAssignmentCreate(BaseModel):
    company_id: uuid.UUID
    worker_id: uuid.UUID
    template_id: uuid.UUID
    assignment_date: date


class TimesheetDayRead(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    worker_id: uuid.UUID
    timesheet_date: date
    ordinary_hours: Decimal
    night_hours: Decimal
    sunday_day_hours: Decimal
    sunday_night_hours: Decimal
    overtime_day: Decimal
    overtime_night: Decimal
    overtime_sunday_day: Decimal
    overtime_sunday_night: Decimal
    total_regular_amount: Decimal | None
    total_surcharge_amount: Decimal | None
    total_gross_amount: Decimal | None


class HolidayCreate(BaseModel):
    company_id: uuid.UUID
    holiday_date: date
    holiday_name: str = Field(min_length=1, max_length=100)
    is_public_holiday: bool = True


class SurchargeRuleCreate(BaseModel):
    company_id: uuid.UUID
    surcharge_type: str
    percentage: Decimal = Field(gt=0)
    effective_from: date
    effective_to: date | None = None
