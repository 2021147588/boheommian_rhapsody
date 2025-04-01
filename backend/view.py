from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    birth_date: str
    gender: str
    license_acquired: str
    driving_experience_years: int
    accident_history: bool
    region: str
    job: str

class Vehicle(BaseModel):
    plate_number: str
    model: str
    year: int
    registered_date: str
    ownership: str
    usage: str
    accident_history: bool
    market_value: int

class InsuranceSettings(BaseModel):
    driver_scope: str
    coverages: dict
    discounts: dict

class UserInfo(BaseModel):
    user: User
    vehicle: Vehicle
    insurance_settings: InsuranceSettings