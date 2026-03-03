// Основные утилиты JavaScript

// Функция для форматирования даты
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Функция для показа уведомлений (если используется глобально)
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления если его нет
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification hidden';
        document.body.appendChild(notification);
    }

    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}

// Функция для обработки ошибок API
function handleApiError(error) {
    console.error('API Error:', error);
    showNotification('Произошла ошибка при выполнении запроса', 'error');
}
