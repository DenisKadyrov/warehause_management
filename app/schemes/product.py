from pydantic import BaseModel


class BaseProduct(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

class CreateProductRequest(BaseProduct):
    pass

class CreateProductResponse(BaseProduct):
    id: int


class ReadProductResponse(BaseProduct):
    id: int


class ReadAllProductsResponse(BaseModel):
    products: list[ReadProductResponse]


class UpdateProductRequest(BaseProduct):
    pass


class UpdateProductResponse(BaseProduct):
    id: int