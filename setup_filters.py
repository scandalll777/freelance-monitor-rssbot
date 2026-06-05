#!/usr/bin/env python3
"""Окно настройки фильтров для пользователей без редактирования YAML."""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from app.config_io import (
    apply_preserved_yaml_fields,
    config_path,
    load_yaml_config,
    save_yaml_config,
)
from app.filter_presets import (
    FILTER_PRESETS,
    detect_active_preset_ids,
    extra_feeds,
    merge_presets,
)

BASE_DIR = Path(__file__).resolve().parent


def _parse_words(text: str) -> list[str]:
    parts = []
    for chunk in text.replace(";", ",").split(","):
        word = chunk.strip()
        if word:
            parts.append(word)
    return parts


def _format_words(words: list[str]) -> str:
    return ", ".join(words or [])


class FilterSetupApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Настройка фильтров FL.ru")
        self.root.geometry("560x640")
        self.root.minsize(480, 520)

        self._checks: dict[str, tk.BooleanVar] = {}
        self._load_current()

        self._build_ui()

    def _load_current(self) -> None:
        raw = load_yaml_config()
        self._active_ids = detect_active_preset_ids(
            raw.get("feeds", []),
            raw.get("categories_include", []) or [],
        )
        self._min_budget = str(raw.get("min_budget", 0) or 0)
        self._keywords_inc = _format_words(raw.get("keywords_include", []) or [])
        self._keywords_exc = _format_words(
            raw.get("keywords_exclude", []) or ["бесплатно", "за отзыв"]
        )

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 4}

        ttk.Label(
            self.root,
            text="Выберите разделы FL.ru для мониторинга",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", **pad)

        ttk.Label(
            self.root,
            text="Отметьте галочками нужные категории. Можно выбрать несколько.",
            wraplength=520,
        ).pack(anchor="w", padx=12)

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        canvas = tk.Canvas(frame, highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for preset in FILTER_PRESETS:
            var = tk.BooleanVar(value=preset.id in self._active_ids)
            self._checks[preset.id] = var
            row = ttk.Frame(inner)
            row.pack(fill="x", pady=3)
            ttk.Checkbutton(row, text=preset.label, variable=var).pack(anchor="w")
            ttk.Label(row, text=preset.hint, foreground="#555555").pack(
                anchor="w", padx=22
            )

        extra = ttk.LabelFrame(self.root, text="Дополнительные фильтры")
        extra.pack(fill="x", padx=12, pady=8)

        ttk.Label(extra, text="Минимальный бюджет (руб., 0 = любой):").grid(
            row=0, column=0, sticky="w", padx=8, pady=4
        )
        self._budget_var = tk.StringVar(value=self._min_budget)
        ttk.Entry(extra, textvariable=self._budget_var, width=12).grid(
            row=0, column=1, sticky="w", pady=4
        )

        ttk.Label(
            extra, text="Искать слова (через запятую, необязательно):"
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 0))
        self._inc_var = tk.StringVar(value=self._keywords_inc)
        ttk.Entry(extra, textvariable=self._inc_var).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=4
        )

        ttk.Label(
            extra, text="Исключить слова (через запятую):"
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 0))
        self._exc_var = tk.StringVar(value=self._keywords_exc)
        ttk.Entry(extra, textvariable=self._exc_var).grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=4
        )
        extra.columnconfigure(1, weight=1)

        btns = ttk.Frame(self.root)
        btns.pack(fill="x", padx=12, pady=12)
        ttk.Button(btns, text="Сохранить", command=self._save).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(
            btns,
            text="Сохранить и обновить базу",
            command=self._save_and_reset,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Закрыть", command=self.root.destroy).pack(side="right")

        ttk.Label(
            self.root,
            text="После смены фильтров нажмите «Сохранить и обновить базу», "
            "чтобы не получить старые заказы повторно.",
            wraplength=520,
            foreground="#444444",
        ).pack(anchor="w", padx=12, pady=(0, 12))

    def _collect_data(self) -> dict:
        selected = [pid for pid, var in self._checks.items() if var.get()]
        feeds, categories_include = merge_presets(selected)
        feeds = feeds + extra_feeds(load_yaml_config().get("feeds", []) or [])

        try:
            min_budget = int(self._budget_var.get().strip() or "0")
        except ValueError as exc:
            raise ValueError("Минимальный бюджет должен быть числом") from exc

        return apply_preserved_yaml_fields(
            {
                "feeds": feeds,
                "categories_include": categories_include,
                "keywords_include": _parse_words(self._inc_var.get()),
                "keywords_exclude": _parse_words(self._exc_var.get()),
                "min_budget": max(0, min_budget),
                "max_budget": 0,
            },
            load_yaml_config(),
        )

    def _save(self, *, ask_reset: bool = False) -> bool:
        try:
            data = self._collect_data()
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return False

        save_yaml_config(data, config_path(BASE_DIR))
        messagebox.showinfo(
            "Сохранено",
            f"Фильтры записаны в {config_path(BASE_DIR).name}.\n"
            f"Выбрано разделов: {len([v for v in self._checks.values() if v.get()])}",
        )

        if ask_reset:
            if messagebox.askyesno(
                "Обновить базу?",
                "Сбросить базу заказов и запомнить текущие проекты "
                "без уведомлений?\n\nРекомендуется после смены фильтров.",
            ):
                self._run_reset()
        return True

    def _save_and_reset(self) -> None:
        if self._save(ask_reset=True):
            pass

    def _run_reset(self) -> None:
        reset_bat = BASE_DIR / "reset_database.bat"
        if reset_bat.is_file():
            subprocess.Popen(
                ["cmd", "/c", str(reset_bat)],
                cwd=str(BASE_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            messagebox.showinfo(
                "База обновляется",
                "Открылось окно сброса базы.\n"
                "Дождитесь сообщения «Готово», затем запустите start_bot.bat",
            )
        else:
            db = BASE_DIR / "data" / "projects.db"
            if db.is_file():
                db.unlink()
            messagebox.showinfo(
                "База удалена",
                "Файл projects.db удалён.\n"
                "При следующем запуске бот заполнит базу заново.",
            )

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    sys.path.insert(0, str(BASE_DIR))
    FilterSetupApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
