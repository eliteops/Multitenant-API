from sqlalchemy import select
from database import Base, engine, Session, get_db
from model import Users, Tenant, Application, UsersRole, Role, Users_Applications, LoginModel, Tenants_Applications, \
    Permission
from fastapi import APIRouter, Depends, HTTPException
from oauth2 import oauth2_scheme, get_current_user
from sqlalchemy import select, join, and_
from schema import LoginSchema

# r = redis.Redis(host='localhost', port=6379, db=0)

Base.metadata.create_all(bind=engine)
router = APIRouter(tags=["View"])
system_admin_role = 1                                                                                        
tenant_admin_role = 2
user_role = 3

@router.get("/users/{user_id}")
async def get_user_details(user_id: int , db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    # Query the Users table to fetch user details
    print(current_user)
    print(current_user.user_id)
    current_user_role = db.execute(
        select(UsersRole.role_id)
        .filter(UsersRole.user_id == current_user.user_id)
    ).scalar()
    if current_user_role == system_admin_role:
        user_query = select(Users).where(Users.user_id == user_id)
        user_result = db.execute(user_query)
        user = user_result.scalars().first()
        if not user:
            return 'User not found with that user id.'  # User not found

        # Query related tables to fetch additional details
        user_role_query = select(UsersRole).where(UsersRole.user_id == user_id)
        user_role_result = db.execute(user_role_query)
        user_role = user_role_result.scalars().first()

        role_query = select(Role).where(Role.role_id == user_role.role_id)
        role_result = db.execute(role_query)
        role = role_result.scalars().first()

        permission_query = select(Permission).where(Permission.role_foreign_id == role.role_id)
        permission_result = db.execute(permission_query)
        permissions = permission_result.scalars().all()

        user_application_query = select(Users_Applications).where(Users_Applications.user_id == user_id)
        user_application_result = db.execute(user_application_query)
        user_applications = user_application_result.scalars().all()

        applications = []
        for ua in user_applications:
            application_query = select(Application).where(Application.application_id == ua.application_id)
            application_result = db.execute(application_query)
            applications.append(application_result.scalars().first())

        tenant_query = select(Tenant).where(Tenant.tenant_id == user.tenant_foreign_id)
        tenant_result = db.execute(tenant_query)
        tenant = tenant_result.scalars().first()

        # Construct a dictionary with user details
        user_details = {
            "user": {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "user_email": user.user_email,
                "user_contact": user.user_contact
            },
            "role": {
                "role_id": role.role_id,
                "role_name": role.role_name
            },
            "permissions": [p.permission_description for p in permissions],
            "applications": [app.application_name for app in applications],
            "tenant": {
                "tenant_id": tenant.tenant_id,
                "tenant_name": tenant.tenant_name,
                "tenant_email": tenant.tenant_email,
                "tenant_contact": tenant.tenant_contact
            }
        }

        return user_details
    return f'{current_user.user_name} is not authorized to access this page.'

@router.get("/show_users")
async def view_user(db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    current_user_tenant_id = db.execute(
        select(Users.tenant_foreign_id)
        .filter(Users.user_id == current_user.user_id)
    ).scalar()                                                             #  Get the tenant id of the logged in user

    if not current_user_tenant_id:
        raise HTTPException(status_code=404, detail="Tenant not found for the current user...")

    # Fetch the role of the current user
    current_user_role = db.execute(
        select(UsersRole.role_id)
        .filter(UsersRole.user_id == current_user.user_id)
    ).scalar()

    # If the user's role is 1 (system admin), return all users
    if current_user_role == system_admin_role:
        all_users = db.execute(select(Users)).scalars().all()
        return all_users

    req_permission = 'view users'

    # Fetching users belonging to the same tenant as the current user
    users = db.execute(
        select(Users)
        .join(UsersRole)
        .join(Role)
        .join(Permission)
        .where(                       # filtering permission and tenant_id given to that user
            and_(
                Users.tenant_foreign_id == current_user_tenant_id,
                Permission.permission_description == req_permission
            )

        )

    )

    users = users.scalars().all()
    if users:
        return users

    return 'No users found for the current tenant with the required permission'

@router.get("/show_loggedin_users")
async def view_loggedin_user(db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    loggedin_user = db.query(LoginModel).all()
    return loggedin_user


@router.get("/show_tenants")
async def show_tenants(db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    permission = 'view tenant'
    tenants = db.query(Tenant).all()
    users = db.query(Users).filter(Users.user_id == current_user.user_id).first()
    user_tenant = db.query(Tenant).filter(Tenant.tenant_id == users.tenant_foreign_id).first()

    current_user_role = db.execute(
        select(UsersRole.role_id)
        .filter(UsersRole.user_id == current_user.user_id)
    ).scalar()
    if not current_user_role:
        return 'Role not found for the current user...'

    if current_user_role == system_admin_role:
        return {
            'tenants': tenants,

            'user_id': current_user.user_id,
            'login_id': current_user.login_id,
            'user_name': current_user.user_name,

            "User's Tenant": user_tenant
        }
    return 'You are not authorized to view tenants'


@router.get("/show_tenant_applications")
async def view_tenant_application(db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    view_application = db.query(Tenants_Applications).all()

    if not view_application:
        return 'Application not found for the current tenant...'

    current_user_role = db.execute(
        select(UsersRole.role_id)
        .filter(UsersRole.user_id == current_user.user_id)
    ).scalar()

    if not current_user_role:
        return 'Role not found for the current user...'

    if current_user_role == system_admin_role:
        return view_application
    return 'You are not authorized to view applications'

@router.get("/show_user_applications")
async def view_user_application(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    view_application = db.query(Users_Applications).all()
    return view_application


@router.get("/roles")
async def view_roles(db: Session = Depends(get_db), current_user: LoginSchema = Depends(get_current_user)):
    roles = db.query(Role).all()
    if not roles:
        return 'Role not found...'

    current_user_role = db.execute(
        select(UsersRole.role_id)
        .filter(UsersRole.user_id == current_user.user_id)
    ).scalar()

    if not current_user_role:
        return 'Role not found for the current user...'

    if current_user_role == system_admin_role:
        return roles
    return 'You are not authorized to view roles'

@router.get("/read_permissions")
async def view_permissions(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    permissions = db.query(Permission).all()
    user_role = db.query(UsersRole).all()
    grant_permission = [(i.permission_id, i.permission_description, i.role_foreign_id) for i in permissions if
                        i.role_foreign_id == 2]
    return permissions


@router.get("/application")
async def view_applications(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    applications = db.query(Application).all()
    return applications

# def view_function_permissions(db: Session = Depends(get_db)):
#     permission = db.query(Permission).all()
#     req_permission = 'add user'
#     permissions = [(i.permission_id, i.permission_description, i.role_foreign_id) for i in permission if
#                    i.permission_description == req_permission]
#     print(permissions)
#
#
# view_function_permissions(Session)
