from pydantic import BaseModel
from typing import List, Dict

"""
{'invoiceId': '2404145J666ZrNRophsn', 'status': 'created', 'amount': 100, 'ccy': 980, 
'createdDate': '2024-04-14T09:36:37Z', 'modifiedDate': '2024-04-14T09:36:37Z', 
'reference': '123', 'destination': 'Order from Telegram Bot'}

"""


class InvoiceRequest(BaseModel):
    invoiceId: str
    status: str
    amount: int
    ccy: int
    createdDate: str
    modifiedDate: str
    reference: str
    destination: str
