from enum import Enum


class ProductCategory(str, Enum):
    SALT_BREAD = "salt_bread"
    DANISH = "danish"
    DONUT = "donut"
    VEGETABLE_BREAD = "vegetable_bread"
    SWEET_BREAD = "sweet_bread"
    BAG = "bag"
