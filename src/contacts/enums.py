from enum import Enum


class SearchParams(str, Enum):
    id = "id"
    name = "name"
    second_name = "second_name"
    email = "email"
    phone = "phone"
