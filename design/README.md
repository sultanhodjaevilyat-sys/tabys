# Дизайн Tabys (Figma)

**Файл:** https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz

Дизайн сделан до кода и совпадает с ним 1 в 1: цвета и шрифты в Figma — это **переменные и стили**, их значения выгружены в [`tokens.json`](tokens.json) и используются в `frontend/src/styles.css` как CSS-переменные (`--green`, `--gold` …).

## Страницы файла

| Страница Figma | Что внутри |
|---|---|
| **Дизайн-система** | Цвета (12 переменных), 9 стилей текста, отступы и радиусы, компоненты |
| **Desktop 1440** | 10 экранов сайта |
| **Mobile 390** | Мобильные версии (адаптив, бургер-меню) |

## Экраны → маршруты сайта

| Экран | Маршрут | Figma |
|---|---|---|
| Главная + 3D-модель | `/` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=3-2) |
| Панель владельца | `/dashboard` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=4-37) |
| Аудитор потерь | `/audit` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=4-108) |
| AI-ассистент | `/assistant` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=4-181) |
| Меню и техкарты | `/menu` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=5-123) |
| Склад и прогноз | `/warehouse` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=5-227) |
| Матрица меню | `/insights` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=5-362) |
| Тарифы (Stripe) | `/pricing` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=5-460) |
| Оплата успешна | `/billing/success` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=8-268) |
| 404 | `*` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=8-311) |
| Mobile — Главная | `/` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=6-8) |
| Mobile — Панель | `/dashboard` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=6-85) |
| Mobile — AI-ассистент | `/assistant` | [открыть](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=6-113) |

## Компоненты Figma → компоненты React

| Figma | Варианты / свойства | React (`frontend/src`) |
|---|---|---|
| [Button](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-7) | Type = Primary / Ghost · текст Label | `.btn`, `.btn.ghost` |
| [Chip](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-13) | State = Default / Active | `.chip`, `.chip.active` (фильтры меню, примеры в чате) |
| [Badge](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-22) | Group = Звезда / Лошадка / Загадка / Собака | `components/ui.jsx → Badge` |
| [StatCard](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-32) | Tone = Default / Danger · Label, Value, Hint | `components/ui.jsx → StatCard` |
| [FeatureCard](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-33) | Icon, Title, Text | `.feature` на главной |
| [IncidentCard](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-37) | Tag, Title, Amount, Text | `.incident` в аудиторе |
| [NavBar](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-44) / [NavBar Mobile](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=6-2) | активная ссылка | `components/Layout.jsx` |
| [Footer](https://www.figma.com/design/WveOJjh2JQ1AHckUkBgZOz?node-id=2-64) | — | `components/Layout.jsx` |

## Почему такие решения

- **Зелёный + золотой.** «Табыс» по-казахски — прибыль: зелёный = деньги и доверие, золотой = акцент на сэкономленных деньгах.
- **Красный только для потерь.** Пользователь сразу видит, где кафе теряет деньги (карточки аудитора, строки с перерасходом).
- **Inter.** Читается на кассовых моноблоках и телефонах, полностью поддерживает кириллицу и знак ₸.
- **Карточки 14 px радиус, отступы кратны 4/8.** Единый ритм на всех экранах.
- **Mobile-first таблицы.** На телефоне таблицы превращаются в списки «название → значение».
