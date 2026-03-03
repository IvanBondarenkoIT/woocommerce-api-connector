"""
Утилита для нормализации телефонных номеров.

Приводит телефоны к единому международному формату для корректного поиска
и сравнения в разных системах (WooCommerce, LILU).
"""

import re
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


class PhoneNormalizer:
    """
    Класс для нормализации телефонных номеров.
    
    Приводит телефоны к международному формату: +79991234567
    """
    
    # Коды стран по умолчанию
    COUNTRY_CODES = {
        'RU': '+7',
        'UA': '+380',
        'BY': '+375',
        'KZ': '+7',
        'GE': '+995',
    }
    
    def __init__(self, default_country: str = 'RU'):
        """
        Инициализация нормализатора.
        
        Args:
            default_country: Код страны по умолчанию (RU, UA, BY и т.д.)
        """
        self.default_country = default_country
        self.default_code = self.COUNTRY_CODES.get(default_country, '+7')
        logger.debug(f"PhoneNormalizer initialized with default country: {default_country}")
    
    def normalize(self, phone: Optional[str]) -> Optional[str]:
        """
        Нормализовать телефонный номер.
        
        Приводит телефон к формату: +79991234567
        
        Args:
            phone: Телефонный номер в любом формате
        
        Returns:
            Нормализованный телефон или None если не удалось нормализовать
        
        Examples:
            >>> normalizer = PhoneNormalizer()
            >>> normalizer.normalize("8 (999) 123-45-67")
            '+79991234567'
            >>> normalizer.normalize("+7 999 123 45 67")
            '+79991234567'
            >>> normalizer.normalize("9991234567")
            '+79991234567'
        """
        if not phone:
            return None
        
        # Убираем все пробелы, дефисы, скобки и другие символы
        cleaned = re.sub(r'[\s\-\(\)\.]', '', str(phone).strip())
        
        if not cleaned:
            return None
        
        # Если уже начинается с +, оставляем как есть
        if cleaned.startswith('+'):
            # Убираем все нецифровые символы после +
            digits = re.sub(r'[^\d]', '', cleaned[1:])
            if digits:
                return f"+{digits}"
            return None
        
        # Если начинается с 8 (российский формат), заменяем на +7
        if cleaned.startswith('8') and len(cleaned) >= 10:
            digits = cleaned[1:]  # Убираем 8
            # Проверяем что это 10 цифр
            if len(digits) == 10 and digits.isdigit():
                return f"{self.default_code}{digits}"
        
        # Если начинается с 7 (российский формат без +)
        if cleaned.startswith('7') and len(cleaned) >= 11:
            digits = cleaned
            # Проверяем что это 11 цифр (7 + 10 цифр)
            if len(digits) == 11 and digits.isdigit():
                return f"+{digits}"
        
        # Если только цифры (10 цифр для России)
        if cleaned.isdigit():
            if len(cleaned) == 10:
                # 10 цифр - добавляем код страны
                return f"{self.default_code}{cleaned}"
            elif len(cleaned) == 11 and cleaned.startswith('7'):
                # 11 цифр начинается с 7
                return f"+{cleaned}"
            elif len(cleaned) > 10:
                # Больше 10 цифр - возможно уже с кодом страны
                return f"+{cleaned}"
        
        # Если ничего не подошло, пытаемся добавить код страны
        if cleaned.isdigit() and len(cleaned) >= 9:
            logger.warning(f"Could not determine phone format for: {phone}, adding default code")
            return f"{self.default_code}{cleaned}"
        
        logger.warning(f"Could not normalize phone: {phone}")
        return None
    
    def is_valid(self, phone: Optional[str]) -> bool:
        """
        Проверить, является ли телефон валидным.
        
        Args:
            phone: Телефонный номер
        
        Returns:
            True если телефон валидный, False иначе
        """
        normalized = self.normalize(phone)
        if not normalized:
            return False
        
        # Проверяем что это международный формат с +
        if not normalized.startswith('+'):
            return False
        
        # Проверяем что после + только цифры
        digits = normalized[1:]
        if not digits.isdigit():
            return False
        
        # Минимум 10 цифр (для большинства стран)
        if len(digits) < 10:
            return False
        
        return True


def normalize_phone(phone: Optional[str], default_country: str = 'RU') -> Optional[str]:
    """
    Удобная функция для быстрой нормализации телефона.
    
    Args:
        phone: Телефонный номер
        default_country: Код страны по умолчанию
    
    Returns:
        Нормализованный телефон или None
    
    Example:
        >>> normalize_phone("8 (999) 123-45-67")
        '+79991234567'
    """
    normalizer = PhoneNormalizer(default_country=default_country)
    return normalizer.normalize(phone)


def is_valid_phone(phone: Optional[str], default_country: str = 'RU') -> bool:
    """
    Удобная функция для проверки валидности телефона.
    
    Args:
        phone: Телефонный номер
        default_country: Код страны по умолчанию
    
    Returns:
        True если телефон валидный
    """
    normalizer = PhoneNormalizer(default_country=default_country)
    return normalizer.is_valid(phone)
