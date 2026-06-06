from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest, ProductResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def list_active_products(db: Session = Depends(get_db)):
    return product_service.fetch_all_active_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = product_service.fetch_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreateRequest, db: Session = Depends(get_db)):
    existing_product = product_service.fetch_product_by_id(db, payload.id)
    if existing_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product ID already exists")
    return product_service.create_product(db, payload)      


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str, payload: ProductUpdateRequest, db: Session = Depends(get_db)
):
    product = product_service.update_product(db, product_id, payload)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(product_id: str, db: Session = Depends(get_db)):
    success = product_service.deactivate_product(db, product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
