from typing import Optional

from pydantic import BaseModel


class Tenant(BaseModel):
    name: str
    email: str
    contact: str

    class Config:
        orm_mode = True


class CurrentUser(BaseModel):
    login_id: int
    user_name: str
    user_id: int

    class Config:
        orm_mode = True


class TenantOut(BaseModel):
    tenant_id: int
    tenant_name: str
    tenant_email: str
    tenant_contact: str

    class Config:
        orm_mode = True




class ShowUser_response(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_contact: str
    tenant_foreign_id: Optional[int] = None

    class Config:
        orm_mode = True


class Product(BaseModel):
    name: str
    description: str
    price: float
    quantity: int

    class Config:
        orm_mode = True


class Order(BaseModel):
    product_id: int
    quantity: int

    class Config:
        orm_mode = True


class Users_model(BaseModel):
    name: str
    email: str
    contact: str


    class Config:
        orm_mode = True


class Role(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Permission(BaseModel):
    description: str
    role_foreign_id: int

    class Config:
        orm_mode = True


class Application(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class Tenants_Application(BaseModel):
    tenant_id: int
    application_id: int

    class Config:
        orm_mode = True


class Users_Application(BaseModel):
    application_id: int

    class Config:
        orm_mode = True


class LoginSchema(BaseModel):
    username: str
    user_password: str
    user_id: int

    class Config:
        orm_mode = True

class login_response(BaseModel):
    login_id: int
    user_id: int
    user_name: str

    class Config:
        orm_mode = True

class UserRoleResponse(BaseModel):
    role: str

    class Config:
        orm_mode = True


class CombinedResponse(BaseModel):

    current_user: login_response
    assigned_role: Optional[UserRoleResponse]

    class Config:
        orm_mode = True