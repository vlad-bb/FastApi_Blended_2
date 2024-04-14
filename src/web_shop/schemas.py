from pydantic import BaseModel
from typing import List, Dict


class WebShopRequest(BaseModel):
    products: List
    totalPrice: int
    queryId: str
    user: Dict



