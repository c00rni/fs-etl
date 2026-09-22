from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Filling:
    title: str
    cik: str
    form_type: str
    company_name: str
    link: str
    filling_date: date
