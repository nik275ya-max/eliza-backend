from sqladmin import Admin, ModelView
from app.core.database import engine, Base
from app.models.license import LicenseKey, AdminUser


# Представления для админ-панели
class LicenseKeyAdmin(ModelView, model=LicenseKey):
    column_list = [LicenseKey.id, LicenseKey.key, LicenseKey.is_activated,
                   LicenseKey.activation_count, LicenseKey.max_activations,
                   LicenseKey.created_at]
    column_default_sort = (LicenseKey.created_at, True)
    column_searchable_list = [LicenseKey.key]
    column_filters = [LicenseKey.is_activated, LicenseKey.created_at]
    form_columns = [LicenseKey.key, LicenseKey.max_activations]
    column_labels = {
        LicenseKey.key: "Ключ",
        LicenseKey.is_activated: "Активирован",
        LicenseKey.activation_count: "Активаций",
        LicenseKey.max_activations: "Макс. активаций",
        LicenseKey.created_at: "Создан",
    }


class AdminUserAdmin(ModelView, model=AdminUser):
    column_list = [AdminUser.id, AdminUser.username, AdminUser.email,
                   AdminUser.is_active, AdminUser.created_at]
    column_default_sort = (AdminUser.created_at, True)
    column_searchable_list = [AdminUser.username]
    column_filters = [AdminUser.is_active]
    form_columns = [AdminUser.username, AdminUser.email, AdminUser.is_active]
    column_labels = {
        AdminUser.username: "Имя",
        AdminUser.email: "Email",
        AdminUser.is_active: "Активен",
        AdminUser.created_at: "Создан",
    }


# Инициализация админ-панели
admin = Admin(engine=engine, title="Eliza Admin")
admin.add_view(LicenseKeyAdmin)
admin.add_view(AdminUserAdmin)
