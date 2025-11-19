from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Filament Schemas
class FilamentBase(BaseModel):
    brand: str
    material: str
    color_name: str
    color_hex: str 
    is_multicolor: bool = False
    initial_weight: float
    remaining_weight: float
    price: float
    purchase_date: Optional[datetime] = None

class FilamentCreate(FilamentBase):
    pass

class FilamentUpdate(BaseModel):
    brand: Optional[str] = None
    material: Optional[str] = None
    color_name: Optional[str] = None
    color_hex: Optional[str] = None
    is_multicolor: Optional[bool] = None
    initial_weight: Optional[float] = None
    remaining_weight: Optional[float] = None
    price: Optional[float] = None

class FilamentResponse(FilamentBase):
    id: int
    
    class Config:
        from_attributes = True

# Print Job Schemas
class FilamentUsageBase(BaseModel):
    filament_id: int
    grams_used: float

class PrintJobCreate(BaseModel):
    name: str
    success: bool = True
    filaments_used: List[FilamentUsageBase]

class FilamentUsageResponse(FilamentUsageBase):
    id: int
    print_job_id: int
    
    class Config:
        from_attributes = True

class PrintJobResponse(BaseModel):
    id: int
    name: str
    date: datetime
    success: bool
    # usages: List[FilamentUsageResponse] = [] # We can add this if needed
    
    class Config:
        from_attributes = True

# Stats Schema
class StatsResponse(BaseModel):
    total_plastic_used_this_month: float
    most_used_color: str
