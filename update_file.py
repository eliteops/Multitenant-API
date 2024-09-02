from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

import model
import schema
from database import Base, engine, Session, get_db
from oauth2 import get_current_user

Base.metadata.create_all(bind=engine)
router = APIRouter(tags=["update"])

system_admin_role = 1
tenant_admin_role = 2
user_role = 3


@router.put("/tenant_update/{tenant_id}")
async def update_tenant(tenant_id: int, request: schema.Tenant, db: Session = Depends(get_db),
                        current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_tenant = db.query(model.Tenant).filter(model.Tenant.tenant_id == tenant_id).first()
    print(vars(verify_tenant))
    print('this is the current user id ..............', current_user.user_id)

    if not verify_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))
    if current_user_role == system_admin_role:
        verify_tenant.tenant_name = request.name
        verify_tenant.tenant_email = request.email
        verify_tenant.tenant_password = request.password
        verify_tenant.tenant_contact = request.contact
        db.commit()
        return 'Tenant updated !!!'
    return 'You are not authorized to update tenant, only system admin can update tenant'


'write function for updating tenant application'


@router.put("/tenant_application_update/{tenant_id}")
def update_tenant_application(tenant_id: int, request: schema.Tenants_Application, db: Session = Depends(get_db),
                              current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_application = db.query(model.Tenants_Applications).filter(
        model.Tenants_Applications.tenant_id == tenant_id).first()
    if not verify_application:
        raise HTTPException(status_code=404, detail="Tenant application not found")

    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))

    if current_user_role == system_admin_role:
        verify_application.tenant_id = request.tenant_id
        verify_application.application_id = request.application_id
        db.commit()
        return 'Tenant application updated !!!'
    return 'You are not authorized to update tenant application, only system admin can update tenant application'


@router.put("/user_update/{user_id}")
def update_user(user_id: int, request: schema.Users_model, db: Session = Depends(get_db),
                current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_user = db.query(model.Users).filter(model.Users.user_id == user_id).first()
    if not verify_user:
        raise HTTPException(status_code=404, detail="user not found")

    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()

    tenant_id = db.execute(
        select(model.Users.tenant_foreign_id)
        .filter(model.Users.user_id == current_user.user_id)
    ).scalar()

    if current_user_role == system_admin_role:
        verify_user.user_name = request.name
        verify_user.user_email = request.email
        verify_user.user_password = request.password
        verify_user.user_contact = request.contact
        db.commit()
        return 'User updated !!!'

    if current_user_role == tenant_admin_role:
        print('Notice: Tenant admin can only update users for their tenants..')
        if tenant_id == verify_user.tenant_foreign_id:
            verify_user.user_name = request.name
            verify_user.user_email = request.email
            verify_user.user_password = request.password
            verify_user.user_contact = request.contact
            db.commit()
            return f'User updated by {current_user.user_name} !!!'

    raise HTTPException(status_code=404, detail="You are not authorized to update this user")


@router.put("/user_application_update/{user_id}")
def update_user_application(user_id: int, request: schema.Users_Application, db: Session = Depends(get_db),
                            current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_application = db.execute(
        select(model.Users_Applications).filter(model.Users_Applications.user_id == user_id)).scalar()
    if not verify_application:
        raise HTTPException(status_code=404, detail="User application not found")

    current_user_role = db.execute(
        select(model.UsersRole.role_id).filter(model.UsersRole.user_id == current_user.user_id)).scalar()

    current_user_tenant = db.execute(
        select(model.Users.tenant_foreign_id).filter(model.Users.user_id == current_user.user_id)).scalar()

    if current_user_role == system_admin_role:
        verify_application.user_id = user_id
        verify_application.application_id = request.application_id
        db.commit()
        return 'User application updated !!!'

    if current_user_role == tenant_admin_role:
        print("Notice: Tenant admin can only update their user's app details for their tenants..")
        check_tenant = db.execute(select(model.Users.tenant_foreign_id)
                                  .join(model.Users_Applications)
                                  .filter(model.Users_Applications.user_id == user_id)).scalar()

        if current_user_tenant == check_tenant:
            verify_application.user_id = user_id
            verify_application.application_id = request.application_id
            db.commit()
            return f'User application updated by {current_user.user_name} !!!'

    raise HTTPException(status_code=404, detail="You are not authorized to update this user application")


@router.put("/role_update/{role_id}")
def update_role(role_id: int, request: schema.Role, db: Session = Depends(get_db),
                current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_role = db.query(model.Role).filter(model.Role.role_id == role_id).first()
    if not verify_role:
        raise HTTPException(status_code=404, detail=f"Role not found with this id: {role_id}")
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))

    if current_user_role == system_admin_role:
        verify_role.role_name = request.name
        db.commit()
        return f'Role id {role_id} updated !!!'
    return 'You are not authorized to update role'


@router.put("/permission_update/{permission_id}")
def update_permission(permission_id: int, request: schema.Permission, db: Session = Depends(get_db),
                      current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_permission = db.query(model.Permission).filter(model.Permission.permission_id == permission_id).first()
    if not verify_permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))

    if current_user_role == system_admin_role:
        verify_permission.permission_description = request.description
        verify_permission.role_foreign_id = request.role_foreign_id

        db.commit()
        return 'Permission updated !!!'
    return 'You are not authorized to update permission'


@router.put("/application_update/{application_id}")
def update_application(application_id: int, request: schema.Application, db: Session = Depends(get_db),
                       current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_application = db.query(model.Application).filter(model.Application.application_id == application_id).first()
    if not verify_application:
        raise HTTPException(status_code=404, detail="Application not found")

    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))

    if current_user_role == system_admin_role:
        verify_application.application_name = request.name
        verify_application.application_description = request.description
        db.commit()
        return 'Application updated !!!'
    return 'You are not authorized to update application'


@router.put("/login_update/{user_id}")
def update_login_info(user_id: int, request: schema.LoginSchema, db: Session = Depends(get_db),
                      current_user: schema.LoginSchema = Depends(get_current_user)):
    verify_login_info = db.query(model.LoginModel).filter(model.LoginModel.user_id == user_id).first()
    if not verify_login_info:
        raise HTTPException(status_code=404, detail="Login Info not found.")
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id))

    if current_user_role == system_admin_role:
        verify_login_info.user_name = request.username
        verify_login_info.user_password = request.user_password

        db.commit()
        return 'Login Info updated !!!'
    return 'You are not authorized to update Login Info.'
