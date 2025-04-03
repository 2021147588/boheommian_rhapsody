from pydantic import BaseModel
from typing import Optional, Dict

class User(BaseModel):
    name: str
    birth_date: str
    gender: str
    license_acquired: str
    driving_experience_years: int
    accident_history: bool
    region: str
    job: str
    hobby: str
    driving_style: str
    accident_history_info: str
    insurance_tendency: str
    basic_option_expectation: str
    expected_insurance_grade: str
    additional_notes: str

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
    coverages: Dict[str, str]
    discounts: Dict[str, bool | str]

class UserInfo(BaseModel):
    user: User
    vehicle: Vehicle
    insurance_settings: InsuranceSettings