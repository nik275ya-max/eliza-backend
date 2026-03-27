from sqlalchemy.orm import Session
from app.models.license import LicenseKey
from datetime import datetime
import re


class LicenseService:
    """Сервис для работы с лицензиями"""
    
    @staticmethod
    def validate_key_format(key: str) -> dict:
        """Валидация формата ключа"""
        normalized_key = key.upper().strip()
        match = re.match(r"^ELIZA-(\d{8})-([A-Z0-9]{4})-([A-Z0-9]{4})$", normalized_key)
        
        if not match:
            return {
                "valid": False,
                "error": "Неверный формат ключа. Ожидался ELIZA-YYYYMMDD-XXXX-XXXX",
                "expires_date": None,
                "expires_formatted": None,
            }
        
        date_part = match.group(1)
        
        try:
            year = int(date_part[0:4])
            month = int(date_part[4:6])
            day = int(date_part[6:8])
            expires_date = datetime(year, month, day)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if expires_date < today:
                return {
                    "valid": False,
                    "error": f"Срок действия ключа истёк {day:02d}.{month:02d}.{year}",
                    "expires_date": date_part,
                    "expires_formatted": f"{day:02d}.{month:02d}.{year}",
                    "expired": True,
                }
        except ValueError:
            return {
                "valid": False,
                "error": "Неверная дата в ключе",
                "expires_date": None,
                "expires_formatted": None,
            }
        
        return {
            "valid": True,
            "error": None,
            "expires_date": date_part,
            "expires_formatted": f"{day:02d}.{month:02d}.{year}",
            "expired": False,
        }
    
    @staticmethod
    def get_by_key(db: Session, key: str) -> LicenseKey | None:
        """Получение ключа по значению"""
        return db.query(LicenseKey).filter(LicenseKey.key == key.upper()).first()
    
    @staticmethod
    def create_key(db: Session, key: str, max_activations: int = 1) -> LicenseKey:
        """Создание нового ключа"""
        db_key = LicenseKey(
            key=key.upper(),
            is_activated=False,
            activation_count=0,
            max_activations=max_activations,
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        return db_key
    
    @staticmethod
    def activate_key(db: Session, db_key: LicenseKey) -> bool:
        """Активация ключа"""
        if db_key.activation_count >= db_key.max_activations:
            return False
        
        db_key.is_activated = True
        db_key.activation_count += 1
        db.commit()
        return True
    
    @staticmethod
    def get_all_keys(db: Session, skip: int = 0, limit: int = 100) -> list:
        """Получение всех ключей"""
        return db.query(LicenseKey).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_stats(db: Session) -> dict:
        """Получение статистики"""
        total = db.query(LicenseKey).count()
        activated = db.query(LicenseKey).filter(LicenseKey.is_activated == True).count()
        active = db.query(LicenseKey).filter(
            LicenseKey.is_activated == True,
            LicenseKey.activation_count < LicenseKey.max_activations
        ).count()
        total_activations = db.query(LicenseKey.activation_count).with_entities(
            db.func.sum(LicenseKey.activation_count)
        ).scalar() or 0
        
        return {
            "total_keys": total,
            "activated_keys": activated,
            "active_keys": active,
            "total_activations": total_activations,
        }
    
    @staticmethod
    def delete_key(db: Session, key_id: int) -> bool:
        """Удаление ключа"""
        db_key = db.query(LicenseKey).filter(LicenseKey.id == key_id).first()
        if db_key:
            db.delete(db_key)
            db.commit()
            return True
        return False


license_service = LicenseService()
