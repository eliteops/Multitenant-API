from sqlalchemy import String, Integer, ForeignKey, Column
from database import Base
from sqlalchemy.orm import relationship, mapped_column


class Role(Base):
    __tablename__ = 'Roles'
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = mapped_column(String, nullable=False)
    tenants = relationship("TenantRole", back_populates="role")
    permission = relationship("Permission", back_populates="role")
    users_role = relationship("UsersRole", back_populates="role")


class Permission(Base):
    __tablename__ = 'permissions'
    permission_id = mapped_column(Integer, primary_key=True, index=True)
    permission_description = mapped_column(String, nullable=False)
    role_foreign_id = mapped_column(ForeignKey('Roles.role_id'), nullable=True)
    role = relationship("Role", back_populates="permission")
    # tenant = relationship("Tenant", back_populates="permissions")


class Application(Base):
    __tablename__ = 'applications'
    application_id = mapped_column(Integer, primary_key=True, index=True)
    application_name = mapped_column(String, nullable=False)
    application_description = mapped_column(String, nullable=False)
    user_application = relationship("Users_Applications", back_populates="application")
    tenant_application = relationship("Tenants_Applications", back_populates="application")


class Tenant(Base):
    __tablename__ = 'tenants'
    tenant_id = mapped_column(Integer, primary_key=True, index=True)
    tenant_name = mapped_column(String, nullable=False)
    tenant_email = mapped_column(String, unique=True, nullable=False)
    tenant_contact = mapped_column(String, unique=True, nullable=False)
    user = relationship("Users", back_populates="tenant")
    tenant_role_id = relationship("TenantRole", back_populates="tenant")
    application = relationship("Tenants_Applications", back_populates="tenant")


class Tenants_Applications(Base):
    __tablename__ = 'tenants_applications'
    serial_no = mapped_column(Integer, primary_key=True, index=True)
    tenant_id = mapped_column(Integer, ForeignKey('tenants.tenant_id'))
    tenant = relationship("Tenant", back_populates="application")
    application_id = Column(Integer, ForeignKey('applications.application_id'))
    application = relationship("Application", back_populates="tenant_application")


class TenantRole(Base):
    __tablename__ = 'tenant_roles'
    serial_no = mapped_column(Integer, primary_key=True, index=True)
    tenant_id = mapped_column(Integer, ForeignKey('tenants.tenant_id'))
    tenant = relationship("Tenant", back_populates="tenant_role_id")
    role_id = mapped_column(Integer, ForeignKey('Roles.role_id'))
    role = relationship("Role", back_populates="tenants")


class Users(Base):
    __tablename__ = 'users'
    user_id = mapped_column(Integer, primary_key=True, index=True)
    user_name = mapped_column(String, nullable=False)
    user_email = mapped_column(String, unique=True, nullable=False)
    user_contact = mapped_column(String, unique=True, nullable=False)
    tenant_foreign_id = mapped_column(ForeignKey('tenants.tenant_id'), nullable=False)
    tenant = relationship("Tenant", back_populates="user")
    user_application = relationship("Users_Applications", back_populates="user")
    login_info = relationship("LoginModel", back_populates="user")
    user_id_role = relationship("UsersRole", back_populates="user")


class UsersRole(Base):
    __tablename__ = 'user_role'
    serial_no = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(ForeignKey('users.user_id'))
    user = relationship("Users", back_populates="user_id_role")
    role_id = mapped_column(ForeignKey('Roles.role_id'))
    role = relationship("Role", back_populates="users_role")


class Users_Applications(Base):
    __tablename__ = 'user_application'
    serial_no = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(ForeignKey('users.user_id'))
    user = relationship("Users", back_populates="user_application")
    application_id = mapped_column(ForeignKey('applications.application_id'))
    application = relationship("Application", back_populates="user_application")


class LoginModel(Base):
    __tablename__ = 'login_details'
    login_id = mapped_column(Integer, primary_key=True, index=True)
    user_name = mapped_column(String, nullable=False)
    user_password = mapped_column(String, nullable=False)
    user_id = mapped_column(ForeignKey('users.user_id'), nullable=False)
    user = relationship("Users", back_populates="login_info")
