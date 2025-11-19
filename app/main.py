from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud, database, utils

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Filament Manager for Bambu Lab")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/filament", response_model=schemas.FilamentResponse)
def create_filament(filament: schemas.FilamentCreate, db: Session = Depends(get_db)):
    return crud.create_filament(db=db, filament=filament)

@app.get("/filaments", response_model=List[schemas.FilamentResponse])
def read_filaments(
    material: Optional[str] = None, 
    low_stock: bool = False, 
    db: Session = Depends(get_db)
):
    return crud.get_filaments(db, material=material, low_stock=low_stock)

@app.put("/filament/{filament_id}", response_model=schemas.FilamentResponse)
def update_filament(filament_id: int, filament: schemas.FilamentUpdate, db: Session = Depends(get_db)):
    db_filament = crud.update_filament(db, filament_id, filament)
    if db_filament is None:
        raise HTTPException(status_code=404, detail="Filament not found")
    return db_filament

@app.post("/print", response_model=schemas.PrintJobResponse)
def log_print_job(print_job: schemas.PrintJobCreate, db: Session = Depends(get_db)):
    return crud.create_print_job(db=db, print_job=print_job)

@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)

@app.post("/parse-file")
async def parse_file(file: UploadFile = File(...)):
    """
    Upload a .gcode or .3mf file to extract estimated filament usage.
    Returns a list of weights (in grams) found in the file metadata.
    """
    contents = await file.read()
    weights = utils.parse_material_usage(contents, file.filename)
    return {"filename": file.filename, "estimated_weights_g": weights}
