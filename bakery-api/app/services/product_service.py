from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest


def fetch_all_active_products(db: Session) -> list[Product]:
    return db.query(Product).filter(Product.is_active == True).all()


def fetch_product_by_id(db: Session, product_id: str) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, payload: ProductCreateRequest) -> Product:
    new_product = Product(**payload.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def update_product(
    db: Session, product_id: str, payload: ProductUpdateRequest
) -> Product | None:
    product = fetch_product_by_id(db, product_id)
    if not product:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def deactivate_product(db: Session, product_id: str) -> bool:
    product = fetch_product_by_id(db, product_id)
    if not product:
        return False
    product.is_active = False
    db.commit()
    return True
