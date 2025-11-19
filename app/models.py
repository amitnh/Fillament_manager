from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Filament(Base):
    __tablename__ = "filaments"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    material = Column(String, index=True)  # PLA, PETG, etc.
    color_name = Column(String)
    color_hex = Column(String)  # Stores single hex or JSON list of hexes
    is_multicolor = Column(Boolean, default=False)
    initial_weight = Column(Float)  # grams
    remaining_weight = Column(Float)  # grams
    purchase_date = Column(DateTime, default=datetime.now)
    price = Column(Float)

    usages = relationship("FilamentUsage", back_populates="filament")


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(DateTime, default=datetime.now)
    success = Column(Boolean, default=True)

    filament_usages = relationship("FilamentUsage", back_populates="job")


class FilamentUsage(Base):
    __tablename__ = "filament_usages"

    id = Column(Integer, primary_key=True, index=True)
    print_job_id = Column(Integer, ForeignKey("print_jobs.id"))
    filament_id = Column(Integer, ForeignKey("filaments.id"))
    grams_used = Column(Float)

    job = relationship("PrintJob", back_populates="filament_usages")
    filament = relationship("Filament", back_populates="usages")


