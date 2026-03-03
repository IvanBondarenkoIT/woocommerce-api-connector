# [УСТАРЕЛО] Отчёт отладки Imunify360 — 27 января 2026

> **Итог:** Выводы неверны. Решение — **WC_USER_AGENT в .env** (User-Agent работает, whitelist был пуст).
> См. [IMUNIFY360_QUICK_FIX.md](../docs/guides/IMUNIFY360_QUICK_FIX.md)

---

## Ситуация

Работало утром, днём — 500 «Access denied by Imunify360».

## Вывод отчёта (неверный)

Отчёт делал вывод, что нужен whitelist. На самом деле сработало добавление WC_USER_AGENT в .env.

## Оставлено для истории тестов

Оригинальный текст отчёта сохранён в git history.
