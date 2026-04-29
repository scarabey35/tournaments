# 🏆 TechHackathon Platform

Веб-застосунок для організації та проведення хакатонів і технічних змагань. Система підтримує повний цикл: від створення турніру — до автоматичного рейтингу команд за результатами оцінювання журі.

---

## 📋 Зміст

- [Можливості](#-можливості)
- [Технічний стек](#-технічний-стек)
- [Встановлення](#-встановлення)
- [Запуск](#-запуск)
- [Змінні середовища](#-змінні-середовища)
- [Структура проекту](#-структура-проекту)
- [Моделі бази даних](#-моделі-бази-даних)
- [Маршрути](#-маршрути)
- [Ролі та авторизація](#-ролі-та-авторизація)
- [Бізнес-логіка](#-бізнес-логіка)

---

## ✨ Можливості

- **Адміністратор** — створює турніри та раунди, керує статусами, розподіляє роботи між журі
- **Команди** — реєструються в турнірах, подають роботи (GitHub + відео + live demo)
- **Журі** — отримують призначені роботи та оцінюють їх за 5 критеріями (0–100)
- **Лідерборд** — автоматичний рейтинг команд за середнім балом усіх оцінок

---

## 🛠 Технічний стек

| Компонент | Версія |
|---|---|
| Python | 3.11 |
| Flask | 3.1.3 |
| Flask-SQLAlchemy | 3.1.1 |
| SQLAlchemy | 2.0.49 |
| Flask-Migrate | 4.1.0 |
| Flask-Login | 0.6.3 |
| Werkzeug | 3.1.8 |
| База даних | SQLite (`instance/app.db`) |

---

## 📦 Встановлення

```bash
# Клонування репозиторію
git clone https://github.com/your-username/techhackathon.git
cd techhackathon

# (Опціонально) Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Встановлення залежностей
pip install -r requirements.txt
```

**`requirements.txt`:**
```
Flask==3.1.3
Flask_Login==0.6.3
Flask_Migrate==4.1.0
flask_sqlalchemy==3.1.1
SQLAlchemy==2.0.49
Werkzeug==3.1.8
```

---

## 🚀 Запуск

```bash
python app.py
```

Або на Windows:
```bash
start.bat
```

Застосунок запуститься за адресою **http://127.0.0.1:5000/**

> База даних `instance/app.db` створюється автоматично при першому запуску.

---

## ⚙️ Змінні середовища

| Змінна | За замовчуванням | Опис |
|---|---|---|
| `SECRET_KEY` | `super-secret-key-change-in-production` | ⚠️ Обов'язково змініть у production |
| `DATABASE_URL` | `sqlite:///instance/app.db` | URI бази даних |
| `FLASK_ENV` | `development` | `development` або `production` |

---

## 📁 Структура проекту

```
project/
├── app.py                      # Точка входу, фабрика create_app()
├── requirements.txt
├── start.bat                   # Скрипт запуску для Windows
├── instance/
│   └── app.db                  # SQLite база даних
└── app/
    ├── __init__.py
    ├── config.py               # Конфігурація Dev/Prod
    ├── decorators.py           # Декоратор roles_required
    ├── extension.py            # Ініціалізація db та migrate
    ├── models/
    │   ├── __init__.py         # Реєстрація всіх моделей
    │   ├── user.py
    │   ├── tournament.py
    │   ├── team.py
    │   ├── team_member.py
    │   ├── round.py
    │   ├── submission.py
    │   ├── evaluation.py
    │   └── leaderboard.py
    ├── routes/
    │   ├── landing.py          # Публічні сторінки
    │   ├── user.py             # Реєстрація, вхід, профіль
    │   ├── admin.py            # Панель адміністратора
    │   ├── tournaments.py      # Турніри та лідерборд
    │   ├── rounds.py           # Раунди та подача робіт
    │   ├── teams.py            # Реєстрація команд
    │   └── jury.py             # Оцінювання
    ├── templates/              # Jinja2 HTML-шаблони
    └── static/                 # CSS, JS, SVG-іконки
```

---

## 🗄 Моделі бази даних

### `User` — користувачі системи
| Поле | Тип | Опис |
|---|---|---|
| `id` | Integer PK | — |
| `name` | String(255) | Ім'я |
| `email` | String(255) unique | Email |
| `password_hash` | String(255) | Хеш пароля (Werkzeug) |
| `role` | String(50) | `admin` / `team` / `jury` |
| `team_id` | FK → teams | Команда (nullable) |

### `Tournament` — турніри
| Поле | Тип | Опис |
|---|---|---|
| `id` | Integer PK | — |
| `name` | String(255) | Назва |
| `status` | String(50) | `draft` → `registration` → `running` → `finished` |
| `registration_start/end` | DateTime | Вікно реєстрації |
| `submission_deadline` | DateTime | Дедлайн подачі |
| `format` | String(50) | Формат турніру |
| `max_teams` | Integer | Ліміт команд (nullable) |
| `created_by` | FK → users | Автор |

### `Team` — команди
| Поле | Тип | Опис |
|---|---|---|
| `id` | Integer PK | — |
| `name` | String(255) | Назва |
| `city` / `organization` | String(255) | Опціонально |
| `tournament_id` | FK → tournaments | — |

### `TeamMember` — учасники команди
| Поле | Тип | Опис |
|---|---|---|
| `name` / `email` | String(255) | Дані учасника |
| `is_captain` | Boolean | Чи є капітаном |
| `team_id` | FK → teams | — |

### `Round` — раунди
| Поле | Тип | Опис |
|---|---|---|
| `name` | String(255) | Назва |
| `status` | String(50) | `draft` → `active` → `submission_closed` → `evaluated` |
| `start_time` / `end_time` | DateTime | Часові межі |
| `requirements` / `must_have` | Text | Умови раунду |
| `tournament_id` | FK → tournaments | — |

### `Submission` — подані роботи
| Поле | Тип | Опис |
|---|---|---|
| `github_url` | String(500) | Обов'язковий |
| `video_url` | String(500) | Обов'язковий |
| `live_demo_url` | String(500) | Опціонально |
| `team_id` / `round_id` | FK | — |

### `Evaluation` — оцінки журі
| Поле | Тип | Опис |
|---|---|---|
| `backend_score` | Integer 0–100 | Бекенд |
| `database_score` | Integer 0–100 | База даних |
| `frontend_score` | Integer 0–100 | Фронтенд |
| `functionality_score` | Integer 0–100 | Функціональність |
| `usability_score` | Integer 0–100 | Зручність |
| `comment` | Text | Коментар журі |

> UniqueConstraint(`submission_id`, `jury_id`) — один журі не може оцінити одну роботу двічі.

---

## 🗺 Маршрути

### Публічні (`landing`)
| Метод | URL | Опис |
|---|---|---|
| GET | `/` | Лендінг |
| GET | `/home` | Головна після входу |
| GET | `/privacy` | Політика конфіденційності |

### Користувачі (`user`)
| Метод | URL | Опис |
|---|---|---|
| GET/POST | `/register` | Реєстрація |
| GET/POST | `/login` | Вхід |
| POST | `/logout` | Вихід (через форму на сторінці профілю) |
| GET/POST | `/profile` | Профіль (POST — зміна пароля; окрема POST-форма — logout) |

### Адміністратор (`admin`, prefix `/admin`)
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/admin/dashboard` | admin | Список турнірів |
| GET/POST | `/admin/create_tournament` | admin | Створення турніру |

### Турніри (`tournaments`, prefix `/tournaments`)
| Метод | URL | Опис |
|---|---|---|
| GET | `/tournaments/` | Список усіх турнірів |
| GET | `/tournaments/<id>` | Деталі турніру |
| POST | `/tournaments/<id>/status` | Зміна статусу (admin) |
| GET | `/tournaments/<id>/leaderboard` | Рейтинг турніру |

### Раунди (`rounds`)
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET/POST | `/admin/tournaments/<id>/rounds/create` | admin | Створення раунду |
| POST | `/admin/rounds/<id>/status` | admin | Зміна статусу |
| GET | `/rounds/<id>` | — | Деталі раунду |
| GET/POST | `/rounds/<id>/submit` | team | Подача/оновлення роботи |

### Команди (`teams`)
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET/POST | `/tournaments/<id>/register` | team | Реєстрація команди |
| GET | `/teams/<id>` | — | Деталі команди |

### Журі (`jury`)
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| POST | `/admin/rounds/<id>/assign` | admin | Розподіл робіт між журі |
| GET | `/jury/assignments` | jury | Мої призначені роботи |
| GET/POST | `/jury/evaluate/<submission_id>` | jury | Оцінювання роботи |
| GET | `/admin/rounds/<id>/evaluations` | admin | Зведена таблиця оцінок |

---

## 🔐 Ролі та авторизація

Авторизація побудована на **Flask-Login** + декораторі `roles_required`:

```python
@login_required
@roles_required("admin")
def my_view():
    ...
```

| Роль | Можливості |
|---|---|
| `admin` | Створення турнірів/раундів, зміна статусів, розподіл журі, перегляд оцінок |
| `team` | Реєстрація в турнірах, подача та оновлення робіт |
| `jury` | Перегляд призначених робіт, виставлення оцінок після закриття подачі |

---

## ⚡ Бізнес-логіка

### Розподіл робіт між журі
- Кожна робота отримує **мінімум 2** оцінювачі
- Кожен журі отримує **не більше 5** робіт
- Один журі не може отримати одну роботу двічі
- Перед повторним розподілом видаляються незаповнені призначення

### Лідерборд
Розраховується динамічно з таблиці `evaluations`:

```
total_avg = (backend + database + frontend + functionality + usability) / 5
```

Команди без оцінок відображаються з нулями. Сортування — за спаданням `total_avg`.

### Статусний цикл

```
Турнір:  draft → registration → running → finished
Раунд:   draft → active → submission_closed → evaluated
```

> При створенні раунду турнір автоматично переходить зі стану `draft`/`registration` у `running`.

### Міграції БД

```bash
flask db init
flask db migrate -m "опис змін"
flask db upgrade
```

---

## 🔒 Безпека в production

- [ ] Змінити `SECRET_KEY` на довгий випадковий рядок
- [ ] Встановити `FLASK_ENV=production`
- [ ] Задати `DATABASE_URL` для PostgreSQL/MySQL
- [ ] Налаштувати HTTPS
- [ ] Вимкнути `debug=True`
