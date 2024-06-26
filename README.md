# Научный конденсатор

## DeepHack.agents 2024

Основная концепция "Умная суммаризация научных статей"



### Модуль агента с поиском по научным статьям : <a href = "https://github.com/sakutepov/DeepHack-agents/blob/main/services/pubMed_search_agent.py">services/pubMed_search_agent.py </a>

Основные возможности
1. Автоматизированная суммаризация содержания статей <a href = "https://pubmed.ncbi.nlm.nih.gov/">PubMed</a>.
2. Простой запрос на естественном языке для получения необходимой
информации.
3. Интеграция с текущими исследовательскими процессами.
Преимущества для пользователя.
4. Экономия времени на поиск и чтение полнотекстовых статей.
5. Упрощение процесса подготовки обзоров литературы.
6. Увеличение эффективности исследовательской работы.

Класс агента PubMedSearchAgent по текстовому запросу пользователя анализирует актуальные научные статьи и на выходе предоставляет необходимую информацию.

1. Входящее сообщение анализируется, если оно на русском - получаем перевод на английский язык.
2. С помощью LLM генерируются ключевые слова и специальный поисковый запрос для PubMed, например:
   '"Cancer" OR "Disease" AND "Oncology" AND ("Treatment" OR "Prevention")'
3. Получение документов PubMed.
4. С помощью LLM происходит генерация векторов и поиск релевантных документов.
5. Переупорядочивание документов по релевантности.
6. Формирование ответа агента на основе документа.
7. Перевод ответа на исходный язык, если нужно.

Тестирование агента:
```
user_query = 'Что нового в лечении рака груди?'
pma = PubMedSearchAgent(llm)
op = pma.process_query(user_query)
print(op)
```
Результат:
```
Текст обсуждает несколько новых подходов к лечению рака груди. Один из них – это использование фототермальной терапии (PTT), которая использует световое излучение и генерацию тепла в области опухоли. Эта терапия может быть улучшена путем применения наноматериалов, которые могут проникать и целенаправленно воздействовать на опухолевую ткань. Другой подход включает использование иммунотерапии для лечения трижды негативного рака молочной железы (ТНРМЖ), который имеет тенденцию к более агрессивному течению и менее благоприятный прогноз. Иммунотерапия может использоваться в сочетании с другими методами лечения, такими как химиотерапия, и может улучшить общую выживаемость пациентов с ТНРМЖ. Также обсуждаются новые стратегии лечения, основанные на молекулярном подтипе рака молочной железы, включая целевые методы лечения, направленные на определенные мишени или молекулы, поддерживающие прогрессирование опухоли.
```

### Модуль агента с поиском научных коференций: <a href = "https://github.com/sakutepov/DeepHack-agents/blob/main/services/conference_agent.py">services/conference_agent.py </a>

Основные возможности
1. Автоматизированный поиск конференций с помощью <a href = "https://api.guap.ru/data/">портала ГУАП</a> и настраиваемого информера <a href = "https://na-konferencii.ru/">Научные-конференции.рф</a>
2. Подбор релевантных конференций и направлений
3. Организация времени исследователя, найденные конференции можно сразу добавить в личный календарь

Класс агента ConferenceAgent по текстовому запросу пользователя подбирает подходящие будущие конференции на выходе представляя небольшой анонс мероприятия, а так же документ календаря в универсальном формате.

1. Получение списка будущих конференций.
2. По сообщению пользователя и заголовкам конференций выбираются подходящие конференции.
3. Более детальная проверка отобранных конференций по их описанию
4. Выбор наиболее подходящей конференции по теме запроса
5. Формирование ответа о конференции, с возможность добавить конференцию в личный календарь

Тестирование агента:
```
user_query = 'Что нового в лечении рака груди?'
ca = ConferenceAgent(llm)
op = ca.process_query(user_query)
print(op)
```
Результат:
```
10 апреля 2024 года в Махачкале пройдёт XXV Международная научно-практическая конференция «Вызовы современности и стратегии развития общества в условиях новой реальности», на которой, предположительно, будут обсуждаться вопросы, связанные с новыми методами лечения рака груди.
```

### Основной модуль main.py
Визуальная интерфейс реализован с помощью UI открытой библиотеки streamlit
В качестве LLM используется SDK <a href = "https://developers.sber.ru/portal/products/gigachat-api">GigaChat</a>
В основной модуль объединяет UI и ответы агентов.







