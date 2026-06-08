from pydantic import BaseModel, ConfigDict

from app.enums.product_category import ProductCategory


class ProductBase(BaseModel):
    item_name: str
    price: int
    category: ProductCategory
    is_active: bool = True


class ProductCreateRequest(ProductBase):
    id: str


class ProductUpdateRequest(BaseModel):
    item_name: str | None = None
    price: int | None = None
    category: ProductCategory | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
