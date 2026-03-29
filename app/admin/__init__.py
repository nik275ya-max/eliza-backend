"""
Админ-панель для Eliza License API
Монтируется к основному приложению после инициализации
"""

from sqladmin import Admin, ModelView
from app.models.license import LicenseKey, AdminUser
from app.core.database import engine


# Представления для админ-панели
class LicenseKeyAdmin(ModelView, model=LicenseKey):
    name = "Лицензионные ключи"
    name_plural = "Лицензионные ключи"
    icon = "fa-solid fa-key"
    
    column_list = [
        LicenseKey.id,
        LicenseKey.key,
        LicenseKey.is_activated,
        LicenseKey.activation_count,
        LicenseKey.max_activations,
        LicenseKey.created_at,
    ]
    column_default_sort = (LicenseKey.created_at, True)
    column_searchable_list = [LicenseKey.key]
    column_filters = [LicenseKey.is_activated, LicenseKey.created_at]
    form_columns = [LicenseKey.key, LicenseKey.max_activations]


class AdminUserAdmin(ModelView, model=AdminUser):
    name = "Администраторы"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    column_list = [
        AdminUser.id,
        AdminUser.username,
        AdminUser.email,
        AdminUser.is_active,
        AdminUser.created_at,
    ]
    column_default_sort = (AdminUser.created_at, True)
    column_searchable_list = [AdminUser.username]
    column_filters = [AdminUser.is_active]
    form_columns = [AdminUser.username, AdminUser.email, AdminUser.is_active]


# Функция для монтирования админки к приложению
def setup_admin(app):
    """Монтирует админ-панель к FastAPI приложению"""
    admin = Admin(
        app=app,
        engine=engine,
        title="Eliza Admin",
        logo_url="https://via.placeholder.com/100x100?text=E",
    )
    admin.add_view(LicenseKeyAdmin)
    admin.add_view(AdminUserAdmin)
    return admin
