from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
import model
from database import Base, engine, Session, get_db
from oauth2 import get_current_user
from schema import LoginSchema

Base.metadata.create_all(bind=engine)
router = APIRouter(tags=["delete"])

system_admin_role = 1
tenant_admin_role = 2
user_role = 3


@router.delete("/delete_tenant/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    verify_tenant = db.execute(select(model.Tenant).filter(model.Tenant.tenant_id == tenant_id)).scalar()
    if not verify_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_tenant)
        db.commit()
        return 'Tenant deleted successfully.'
    return f'{current_user.user_name} is not authorized to perform this action.'


@router.delete("/tenant_application_delete/{tenant_id}")
def delete_tenant_application(tenant_id: int, db: Session = Depends(get_db),
                              current_user: LoginSchema = Depends(get_current_user)):
    verify_application = db.query(model.Tenants_Applications).filter(
        model.Tenants_Applications.tenant_id == tenant_id).first()
    if not verify_application:
        raise HTTPException(status_code=404, detail="Tenant application not found")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_application)
        db.commit()
        return 'Tenant application deleted !!!'
    return f'{current_user.user_name} is not authorized to perform this action.'


@router.delete("/delete_user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    )
    print(current_user_role)

    current_user_tenant = db.scalar(
        select(model.Users.tenant_foreign_id)
        .filter(model.Users.user_id == current_user.user_id)
    )
    print(current_user_tenant)

    if current_user_role != tenant_admin_role and current_user_role != system_admin_role:
        raise HTTPException(status_code=403, detail="Only tenant admin or system admin is authorized to delete users.")

    # Verify if the user to be deleted belongs to the same tenant as the current user
    user_to_delete = db.execute(
        select(model.Users).filter(model.Users.user_id == user_id)
    ).scalar()
    print(user_to_delete)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")
    if user_to_delete.tenant_foreign_id != current_user_tenant:
        raise HTTPException(status_code=403, detail="You can only delete users from your own tenant.")

    # Delete the user
    db.delete(user_to_delete)
    db.commit()
    return {'detail': 'User deleted successfully.'}


@router.delete("/user_application_delete/{user_app_id}")
def delete_user_application(user_app_id: int, db: Session = Depends(get_db),
                            current_user: LoginSchema = Depends(get_current_user)):
    current_user_role = db.scalar(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    )

    if not current_user_role:
        raise HTTPException(status_code=403, detail="Role is not assigned to you... ")

    if current_user_role not in [system_admin_role, tenant_admin_role]:
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action.")

    if current_user_role == tenant_admin_role:
        # Check if the user application belongs to the current tenant
        tenant_id = db.scalar(
            select(model.Users.tenant_foreign_id)
            .filter(model.Users.user_id == current_user.user_id)
        )
        user_application = db.execute(
            select(model.Users_Applications)
            .join(model.Users)
            .filter(
                model.Users_Applications.user_id == user_app_id,
                model.Users.tenant_foreign_id == tenant_id
            )
        ).scalar()
        if not user_application:
            raise HTTPException(status_code=403,
                                detail="You can only delete user applications from your own tenant.")

    # Verify if the user application exists
    verify_application = db.query(model.Users_Applications).filter(
        model.Users_Applications.user_id == user_app_id).first()
    if not verify_application:
        raise HTTPException(status_code=404, detail="User application not found")

    db.delete(verify_application)
    db.commit()
    return 'User application deleted !!!'


@router.delete("/role_update/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    verify_role = db.query(model.Role).filter(model.Role.role_id == role_id).first()
    if not verify_role:
        raise HTTPException(status_code=404, detail=f"Role not found with this id: {role_id}")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_role)
        db.commit()
        return f'Role id {role_id} deleted !!!'
    return f'{current_user.user_name} is not authorized to perform this action.'


@router.delete("/permission_update/{permission_id}")
def delete_permission(permission_id: int, db: Session = Depends(get_db),
                      current_user: LoginSchema = Depends(get_current_user)):
    verify_permission = db.query(model.Permission).filter(model.Permission.permission_id == permission_id).first()
    if not verify_permission:
        raise HTTPException(status_code=404, detail=f"Permission not found with this id: {permission_id}")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_permission)
        db.commit()

        return f'Permission of this id {permission_id} deleted !!!'
    return f'{current_user.user_name} is not authorized to perform this action.'


@router.delete("/application_update/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db),
                       current_user: LoginSchema = Depends(get_current_user)):
    verify_application = db.query(model.Application).filter(model.Application.application_id == application_id).first()
    if not verify_application:
        raise HTTPException(status_code=404, detail=f"Application not found with this id {application_id}")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_application)
        db.commit()
        return f'Application of this id {application_id} deleted!!!'
    return f'{current_user.user_name} is not authorized to perform this action.'


@router.delete("/login_info_update/{user_id}")
def delete_login_info(user_id: int, db: Session = Depends(get_db),
                      current_user: LoginSchema = Depends(get_current_user)):
    verify_login = db.query(model.LoginModel).filter(model.LoginModel.user_id == user_id).first()
    if not verify_login:
        raise HTTPException(status_code=404, detail=f"Login not found with this id: {user_id}")
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        db.delete(verify_login)
        db.commit()

        return f'user id {user_id} deleted !!!'
    return f'{current_user.user_name} is not authorized to perform this action.'
