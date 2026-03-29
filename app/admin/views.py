from sqladmin import Admin, ModelView
from app.core.database import engine, Base
from app.models.license import LicenseKey, AdminUser


# Представления для админ-панели
class LicenseKeyAdmin(ModelView, model=LicenseKey):
    name = "Лицензионные ключи"
    name_plural = "Лицензионные ключи"
    icon = "fa-solid fa-key"
    
    # Поля для отображения в списке
    column_list = [
        LicenseKey.id,
        LicenseKey.key,
        LicenseKey.is_activated,
        LicenseKey.activation_count,
        LicenseKey.max_activations,
        LicenseKey.created_at,
    ]
    
    # Сортировка по умолчанию
    column_default_sort = (LicenseKey.created_at, True)
    
    # Поля для поиска
    column_searchable_list = [LicenseKey.key]
    
    # Поля для фильтров
    column_filters = [LicenseKey.is_activated, LicenseKey.created_at]
    
    # Поля для формы создания/редактирования
    form_columns = [
        LicenseKey.key,
        LicenseKey.max_activations,
        LicenseKey.is_activated,
        LicenseKey.activation_count,
    ]
    
    # Названия полей
    column_labels = {
        LicenseKey.key: "Ключ",
        LicenseKey.is_activated: "Активирован",
        LicenseKey.activation_count: "Активаций",
        LicenseKey.max_activations: "Макс. активаций",
        LicenseKey.created_at: "Дата создания",
    }
    
    # Разрешить создание
    can_create = True
    
    # Разрешить редактирование
    can_edit = True
    
    # Разрешить удаление
    can_delete = True
    
    # Разрешить просмотр деталей
    can_view_details = True


class AdminUserAdmin(ModelView, model=AdminUser):
    name = "Администраторы"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    # Поля для отображения в списке
    column_list = [
        AdminUser.id,
        AdminUser.username,
        AdminUser.email,
        AdminUser.is_active,
        AdminUser.created_at,
    ]
    
    # Сортировка по умолчанию
    column_default_sort = (AdminUser.created_at, True)
    
    # Поля для поиска
    column_searchable_list = [AdminUser.username]
    
    # Поля для фильтров
    column_filters = [AdminUser.is_active]
    
    # Поля для формы создания/редактирования
    form_columns = [
        AdminUser.username,
        AdminUser.email,
        AdminUser.is_active,
    ]
    
    # Названия полей
    column_labels = {
        AdminUser.username: "Имя пользователя",
        AdminUser.email: "Email",
        AdminUser.is_active: "Активен",
        AdminUser.created_at: "Дата создания",
    }
    
    # Разрешить создание
    can_create = True
    
    # Разрешить редактирование
    can_edit = True
    
    # Разрешить удаление
    can_delete = False  # Не удалять администраторов
    
    # Разрешить просмотр деталей
    can_view_details = True
