from database import Base, engine, Session, get_db
import model
from schema import Users_model, Role, Permission, Application, Tenant, Tenants_Application, Users_Application, \
    LoginSchema
from fastapi import APIRouter, Depends, HTTPException
from oauth2 import get_current_user, oauth2_scheme
from sqlalchemy import select, join, and_
from hash import hash_password

Base.metadata.create_all(bind=engine)
router = APIRouter(tags=["Add"])

system_admin_role = 1
tenant_admin_role = 2
user_role = 3


@router.post("/add_login_details")
def login_details(schema: LoginSchema, db: Session = Depends(get_db),
                  current_user: LoginSchema = Depends(get_current_user)):
    # Get the current user's role
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if not current_user_role:
        raise HTTPException(status_code=404, detail="User not found or the role not assigned.")

    if current_user_role == system_admin_role:

        # Hash the provided password
        hashed_password = hash_password(schema.user_password)
        print(hashed_password)

        # add the login details to the database
        db.add(model.LoginModel(user_name=schema.username, user_password=hashed_password, user_id=schema.user_id))
        db.commit()
        db.close()
        return 'Login details added successfully.'
    return HTTPException(status_code=403, detail="You are not authorized to perform this action")


@router.post("/add_tenant")
def add_tenant(schema: Tenant, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db.add(model.Tenant(tenant_name=schema.name, tenant_email=schema.email,
                        tenant_contact=schema.contact))
    db.commit()
    db.close()
    return 'tenant added successfully....'


@router.post("/add_tenant_application")
def tenant_application(schema: Tenants_Application, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    # Get the current user's role
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()
    if not current_user_role:
        raise HTTPException(status_code=404, detail="User not found or the role not assigned.")

    if current_user_role == system_admin_role:
        db.add(model.Tenants_Applications(tenant_id=schema.tenant_id, application_id=schema.application_id))
        db.commit()
        db.close()
        return 'application added successfully to the tenant..'
    return f'{current_user.user_name} is not authorized to access this. Please contact the system admin.'


@router.post("/add_user")
def add_user(schema: Users_model, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    # Get the current user's role
    current_user_role = db.execute(
        select(model.UsersRole.role_id)
        .filter(model.UsersRole.user_id == current_user.user_id)
    ).scalar()

    if not current_user_role:
        raise HTTPException(status_code=404, detail="User not found or role not assigned..")

    tenant_id = db.execute(
        select(model.Users.tenant_foreign_id)
        .filter(model.Users.user_id == current_user.user_id)
    ).scalar()
    print(tenant_id)

    # If the user's role is 1 (system admin), return all users
    if current_user_role == system_admin_role or current_user_role == tenant_admin_role:
        if current_user_role == tenant_admin_role:
            print('Notice: Tenant admin can only add users for their tenants...')
        db.add(model.Users(user_name=schema.name, user_email=schema.email,
                           user_contact=schema.contact, tenant_foreign_id=tenant_id))

        db.commit()
        db.close()
        return 'Login details added successfully.'
    return f"{current_user.user_name} is not authorized to perform this action"


@router.post("/add_user_application")
def user_application(schema: Users_Application, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    db.add(model.Users_Applications(user_id=schema.user_id, application_id=schema.application_id))
    db.commit()
    db.close()
    return 'application added successfully to the user...'


@router.post("/add_role")
def add_role(schema: Role, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    db.add(model.Role(role_name=schema.name))
    db.commit()
    db.close()
    return 'Role added successfully..'


@router.post("/add_permission")
def add_permission(schema: Permission, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    db.add(model.Permission(permission_description=schema.description, role_foreign_id=schema.role_foreign_id))
    db.commit()
    db.close()
    return 'permission added successfully.'


@router.post("/add_application")
def add_application(schema: Application, db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    db.add(model.Application(application_name=schema.name, application_description=schema.description))
    db.commit()
    db.close()
    return 'application added successfully.'
