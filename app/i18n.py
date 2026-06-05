from __future__ import annotations

from typing import Any

PRESET_LABELS: dict[str, dict[str, str]] = {
    "ai": {"en": "AI — artificial intelligence", "ru": "AI — искусственный интеллект"},
    "vibe_coding": {"en": "Vibe coding", "ru": "Vibe coding"},
    "web_dev": {"en": "Web development", "ru": "Веб-программирование"},
    "programming": {"en": "Programming (all)", "ru": "Программирование (всё)"},
    "sites": {"en": "Website development", "ru": "Разработка сайтов"},
    "design": {"en": "Design & art", "ru": "Дизайн и арт"},
    "mobile": {"en": "Mobile apps", "ru": "Мобильные приложения"},
    "seo": {"en": "SEO & marketing", "ru": "SEO и продвижение"},
    "texts": {"en": "Copywriting", "ru": "Тексты"},
}

MESSAGES: dict[str, dict[str, str]] = {
  "access_denied": {"en": "Access denied", "ru": "Нет доступа"},
  "error": {"en": "Error", "ru": "Ошибка"},
  "btn_sources": {"en": "🌐 Sources", "ru": "🌐 Источники"},
  "btn_categories": {"en": "📂 Categories", "ru": "📂 Разделы"},
  "btn_budget": {"en": "💰 Budget", "ru": "💰 Бюджет"},
  "btn_keywords": {"en": "🔍 Keywords", "ru": "🔍 Искать слова"},
  "btn_exclude": {"en": "🚫 Exclude", "ru": "🚫 Исключить"},
  "btn_show": {"en": "📋 Current settings", "ru": "📋 Текущие настройки"},
  "btn_apply": {"en": "✅ Apply", "ru": "✅ Применить"},
  "btn_apply_reset": {"en": "🔄 Apply + reset DB", "ru": "🔄 Применить + сброс базы"},
  "btn_back_menu": {"en": "◀️ Back to menu", "ru": "◀️ В меню"},
  "btn_back": {"en": "◀️ Back", "ru": "◀️ Назад"},
  "btn_next": {"en": "Next →", "ru": "Далее →"},
  "btn_only_new": {"en": "🆕 New only", "ru": "🆕 Только новые"},
  "btn_send_current": {"en": "📥 Send current listings", "ru": "📥 Прислать текущие"},
  "btn_back_filters": {"en": "◀️ Back to filters", "ru": "◀️ Назад к фильтрам"},
  "btn_language": {"en": "🌐 Language", "ru": "🌐 Язык"},
  "help_menu": {
    "en": "Settings menu. Use buttons below, /menu or /language",
    "ru": "Меню настроек. Кнопки ниже, /menu или /language",
  },
  "btn_lang_en": {"en": "🇬🇧 English", "ru": "🇬🇧 English"},
  "btn_lang_ru": {"en": "🇷🇺 Русский", "ru": "🇷🇺 Русский"},
  "no_sources": {"en": "No sources in config.yaml", "ru": "Нет источников в config.yaml"},
  "menu_plain": {
    "en": "Settings menu. Use the buttons below or /menu",
    "ru": "Меню настроек. Используйте кнопки ниже или /menu",
  },
  "onboarding_plain": {
    "en": "Welcome! Configure the bot with the buttons below.\nStep 1: choose categories and sources, then tap Next.",
    "ru": "Добро пожаловать! Настройте бота кнопками ниже.\nШаг 1: выберите разделы и источники, затем «Далее».",
  },
  "language_title": {
    "en": "<b>🌐 Choose your language</b>\n\nEnglish is selected by default.\nYou can change it anytime in the menu.",
    "ru": "<b>🌐 Выберите язык</b>\n\nПо умолчанию — English.\nПозже можно сменить в меню.",
  },
  "language_saved_en": {"en": "✅ Language set to <b>English</b>", "ru": "✅ Language set to <b>English</b>"},
  "language_saved_ru": {"en": "✅ Язык: <b>Русский</b>", "ru": "✅ Язык: <b>Русский</b>"},
  "main_menu": {
    "en": (
      "<b>⚙️ Monitor settings</b>\n\n"
      "Enable sources, categories and filters, then tap <b>Apply</b>.\n\n"
      "After changing filters, use <b>Apply + reset DB</b> so old listings "
      "are not sent again.\n\n{summary}"
    ),
    "ru": (
      "<b>⚙️ Настройка мониторинга</b>\n\n"
      "Включите источники, разделы и параметры, затем нажмите "
      "<b>Применить</b>.\n\n"
      "После смены фильтров лучше нажать "
      "<b>Применить + сброс базы</b> — тогда старые заказы "
      "не придут повторно.\n\n{summary}"
    ),
  },
  "onboarding_step1": {
    "en": (
      "<b>👋 Welcome!</b>\n\n"
      "Set up filters first — otherwise the bot may send "
      "<b>dozens of old listings</b> at once.\n\n"
      "<b>Step 1 of 2 — filters</b>\n"
      "Choose FL.ru categories and enable the platforms you need.\n\n"
      "{summary}"
    ),
    "ru": (
      "<b>👋 Добро пожаловать!</b>\n\n"
      "Перед запуском настройте фильтры — иначе бот может "
      "прислать <b>десятки старых заказов</b> разом.\n\n"
      "<b>Шаг 1 из 2 — фильтры</b>\n"
      "Выберите разделы FL.ru и включите нужные площадки.\n\n"
      "{summary}"
    ),
  },
  "onboarding_step2": {
    "en": (
      "<b>Step 2 of 2 — existing listings</b>\n\n"
      "There are already published projects on the sites. "
      "What should we do with them?\n\n"
      "🆕 <b>New only</b> (recommended)\n"
      "The bot remembers current listings <b>without messages</b>. "
      "Only projects that appear <b>after</b> setup will be sent.\n\n"
      "📥 <b>Send current listings</b>\n"
      "One-time delivery of all matching projects right now "
      "(can be <b>many</b> messages!). After that — new only."
    ),
    "ru": (
      "<b>Шаг 2 из 2 — текущие заказы</b>\n\n"
      "На сайтах уже есть опубликованные проекты. "
      "Как с ними поступить?\n\n"
      "🆕 <b>Только новые</b> (рекомендуется)\n"
      "Бот запомнит текущие заказы <b>без сообщений</b>. "
      "В Telegram придут только те, что появятся <b>после</b> настройки.\n\n"
      "📥 <b>Прислать текущие</b>\n"
      "Разовая рассылка всех подходящих заказов прямо сейчас "
      "(может быть <b>много</b> сообщений!). "
      "Дальше — только новые."
    ),
  },
  "validate_no_sources": {
    "en": "⚠️ <b>Step 1.</b> Enable at least one source (🌐 Sources).",
    "ru": "⚠️ <b>Шаг 1.</b> Включите хотя бы один источник (кнопка «🌐 Источники»).",
  },
  "validate_no_categories": {
    "en": "⚠️ <b>Step 1.</b> FL.ru is enabled — choose at least one category (📂 Categories).",
    "ru": "⚠️ <b>Шаг 1.</b> FL.ru включён — выберите хотя бы один раздел (кнопка «📂 Разделы»).",
  },
  "onboarding_done": {
    "en": "✅ <b>Monitoring started!</b>\n\n{summary}\n\n{extra}",
    "ru": "✅ <b>Мониторинг запущен!</b>\n\n{summary}\n\n{extra}",
  },
  "onboarding_failed": {
    "en": "❌ Could not finish setup. Please try again.",
    "ru": "❌ Не удалось завершить настройку. Попробуйте ещё раз.",
  },
  "apply_saved": {
    "en": "✅ <b>Filters saved and applied!</b>\n\n{summary}{extra}",
    "ru": "✅ <b>Фильтры сохранены и применены!</b>\n\n{summary}{extra}",
  },
  "apply_failed": {
    "en": "❌ Error while saving. Please try again.",
    "ru": "❌ Ошибка при сохранении. Попробуйте ещё раз.",
  },
  "budget_title": {
    "en": "<b>Minimum budget</b>\n\nCurrent: <b>{value}</b>\n(0 = any budget)\n\nSend a number, e.g. <code>5000</code>",
    "ru": "<b>Минимальный бюджет</b>\n\nСейчас: <b>{value}</b> ₽\n(0 = любой бюджет)\n\nОтправьте число, например: <code>5000</code>",
  },
  "keywords_title": {
    "en": "<b>Search keywords</b>\n\nCurrent: {words}\n\nSend words separated by commas.\nTo clear — send <code>-</code>",
    "ru": "<b>Искать слова</b>\n\nСейчас: {words}\n\nОтправьте слова через запятую.\nЧтобы очистить — отправьте <code>-</code>",
  },
  "exclude_title": {
    "en": "<b>Exclude keywords</b>\n\nCurrent: {words}\n\nSend words separated by commas.\nTo clear — send <code>-</code>",
    "ru": "<b>Исключить слова</b>\n\nСейчас: {words}\n\nОтправьте слова через запятую.\nЧтобы очистить — отправьте <code>-</code>",
  },
  "budget_saved": {
    "en": "✅ Minimum budget: <b>{value}</b>",
    "ru": "✅ Минимальный бюджет: <b>{value}</b> ₽",
  },
  "budget_any": {"en": "✅ Minimum budget: <b>any</b>", "ru": "✅ Минимальный бюджет: <b>любой</b>"},
  "budget_invalid": {
    "en": "Enter a whole number, e.g. <code>3000</code>",
    "ru": "Введите целое число, например <code>3000</code>",
  },
  "keywords_saved": {
    "en": "✅ Search keywords updated.\nDon't forget to tap <b>Apply</b> in the menu.",
    "ru": "✅ Слова для поиска обновлены.\nНе забудьте нажать <b>Применить</b> в меню.",
  },
  "exclude_saved": {
    "en": "✅ Excluded keywords updated.\nDon't forget to tap <b>Apply</b> in the menu.",
    "ru": "✅ Слова-исключения обновлены.\nНе забудьте нажать <b>Применить</b> в меню.",
  },
  "categories_title": {
    "en": "<b>📂 FL.ru categories</b>\n\nTap to enable or disable:",
    "ru": "<b>📂 Разделы FL.ru</b>\n\nНажмите, чтобы включить или выключить раздел:",
  },
  "categories_onboarding": {
    "en": "<b>Step 1 — FL.ru categories</b>\n\nTap to enable or disable:",
    "ru": "<b>Шаг 1 — разделы FL.ru</b>\n\nНажмите, чтобы включить или выключить:",
  },
  "sources_title": {
    "en": "<b>🌐 Sources</b>\n\nTap to enable or disable a platform.",
    "ru": "<b>🌐 Источники</b>\n\nНажмите, чтобы включить или выключить площадку.",
  },
  "sources_onboarding": {
    "en": "<b>Step 1 — sources</b>\n\nTap to enable or disable a platform.",
    "ru": "<b>Шаг 1 — источники</b>\n\nНажмите, чтобы включить или выключить площадку.",
  },
  "apply_reset_extra": {
    "en": "🗄 Database reset. Remembered <b>{count}</b> current listings (no notifications).",
    "ru": "🗄 База сброшена. Запомнено <b>{count}</b> текущих заказов (без уведомлений).",
  },
  "apply_extra": {
    "en": "Monitoring now uses the new filters.",
    "ru": "Мониторинг использует новые фильтры.",
  },
  "finish_current": {
    "en": "📥 Sent <b>{count}</b> current listings.\nFrom now on — <b>new only</b>.",
    "ru": "📥 Отправлено <b>{count}</b> текущих заказов.\nДальше будут приходить только <b>новые</b>.",
  },
  "finish_seed": {
    "en": "🆕 Remembered <b>{count}</b> current listings without notifications.\nFrom now on — <b>new only</b>.",
    "ru": "🆕 Запомнено <b>{count}</b> текущих заказов без уведомлений.\nДальше будут приходить только <b>новые</b>.",
  },
  "summary_title": {"en": "Current filters", "ru": "Текущие фильтры"},
  "summary_no_sources": {"en": "sources not configured", "ru": "источники не настроены"},
  "summary_no_categories": {"en": "no categories selected", "ru": "разделы не выбраны"},
  "summary_sources": {"en": "Sources", "ru": "Источники"},
  "summary_categories": {"en": "FL.ru categories", "ru": "Разделы FL.ru"},
  "summary_budget": {"en": "Min. budget", "ru": "Мин. бюджет"},
  "summary_kw_all": {"en": "Search (all)", "ru": "Искать (все)"},
  "summary_kw_foreign": {"en": "Search (foreign)", "ru": "Искать (зарубеж.)"},
  "summary_exclude": {"en": "Exclude", "ru": "Исключить"},
  "summary_budget_any": {"en": "any", "ru": "любой"},
  "notify_new_project": {"en": "New project on", "ru": "Новый проект на"},
  "notify_auto_translate": {
    "en": "auto-translated to Russian",
    "ru": "автоперевод на русский",
  },
  "notify_budget": {"en": "Budget", "ru": "Бюджет"},
  "notify_deadline": {"en": "Deadline", "ru": "Сроки"},
  "notify_category": {"en": "Category", "ru": "Категория"},
  "notify_published": {"en": "Published", "ru": "Опубликован"},
  "notify_open": {"en": "Open project", "ru": "Открыть проект"},
  "monitor_started": {
    "en": (
      "✅ Freelance feed monitoring started.\n"
      "Added {count} current projects to the database (no notifications).\n"
      "New listings will arrive every {interval}."
    ),
    "ru": (
      "✅ Мониторинг фриланс-лент запущен.\n"
      "В базу добавлено {count} текущих проектов (без уведомлений).\n"
      "Следующие новые проекты будут приходить каждые {interval}."
    ),
  },
  "spam_backlog": {
    "en": (
      "⚠️ Found <b>{count}</b> new listings in one poll.\n"
      "To avoid spam they were saved <b>without notifications</b>.\n"
      "You will only get new listings one by one from now on."
    ),
    "ru": (
      "⚠️ Обнаружено <b>{count}</b> новых объявлений за один опрос.\n"
      "Чтобы не было спама, они добавлены в базу <b>без уведомлений</b>.\n"
      "Дальше будут приходить только по одному новому заказу."
    ),
  },
  "spam_limit": {
    "en": (
      "ℹ️ Found <b>{pending}</b> new listings in one poll.\n"
      "Sent the first <b>{sent}</b>; the other <b>{skipped}</b> were saved without notifications."
    ),
    "ru": (
      "ℹ️ За один опрос найдено <b>{pending}</b> новых объявлений.\n"
      "Отправлено первых <b>{sent}</b>, остальные <b>{skipped}</b> "
      "добавлены в базу без уведомлений."
    ),
  },
}


def t(lang: str, key: str, **kwargs: Any) -> str:
    entry = MESSAGES.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if kwargs:
        return text.format(**kwargs)
    return text


def preset_label(lang: str, preset_id: str, fallback: str) -> str:
    labels = PRESET_LABELS.get(preset_id, {})
    return labels.get(lang) or labels.get("en") or fallback
