from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from . import models, schemas

def create_filament(db: Session, filament: schemas.FilamentCreate):
    db_filament = models.Filament(**filament.dict())
    db.add(db_filament)
    db.commit()
    db.refresh(db_filament)
    return db_filament

def get_filaments(db: Session, material: str = None, low_stock: bool = False):
    query = db.query(models.Filament)
    if material:
        query = query.filter(models.Filament.material == material)
    if low_stock:
        # Assuming low stock is < 100g or 10% of initial? Let's say < 100g for now
        query = query.filter(models.Filament.remaining_weight < 100)
    return query.all()

def get_filament(db: Session, filament_id: int):
    return db.query(models.Filament).filter(models.Filament.id == filament_id).first()

def update_filament(db: Session, filament_id: int, filament_update: schemas.FilamentUpdate):
    db_filament = get_filament(db, filament_id)
    if not db_filament:
        return None
    
    update_data = filament_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_filament, key, value)

    db.add(db_filament)
    db.commit()
    db.refresh(db_filament)
    return db_filament

def create_print_job(db: Session, print_job: schemas.PrintJobCreate):
    # 1. Create Print Job
    db_print_job = models.PrintJob(name=print_job.name, success=print_job.success)
    db.add(db_print_job)
    db.commit()
    db.refresh(db_print_job)

    # 2. Process usages
    for usage in print_job.filaments_used:
        # Create Usage Record
        db_usage = models.FilamentUsage(
            print_job_id=db_print_job.id,
            filament_id=usage.filament_id,
            grams_used=usage.grams_used
        )
        db.add(db_usage)

        # Deduct weight from inventory
        db_filament = get_filament(db, usage.filament_id)
        if db_filament:
            db_filament.remaining_weight -= usage.grams_used
            # Ensure we don't go below zero? Optional, but good for data integrity
            # db_filament.remaining_weight = max(0, db_filament.remaining_weight)
            db.add(db_filament)
    
    db.commit()
    return db_print_job

def get_stats(db: Session):
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    # Total plastic used this month
    total_used = db.query(func.sum(models.FilamentUsage.grams_used))\
        .join(models.PrintJob)\
        .filter(models.PrintJob.date >= start_of_month)\
        .scalar() or 0.0

    # Most used color
    # Group usages by filament color and sum grams
    # We need to join FilamentUsage -> Filament
    most_used_color_result = db.query(
        models.Filament.color_name,
        func.sum(models.FilamentUsage.grams_used).label('total_grams')
    ).join(models.FilamentUsage, models.Filament.id == models.FilamentUsage.filament_id)\
     .group_by(models.Filament.color_name)\
     .order_by(desc('total_grams'))\
     .first()

    most_used_color = most_used_color_result[0] if most_used_color_result else "N/A"

    return {
        "total_plastic_used_this_month": total_used,
        "most_used_color": most_used_color
    }
