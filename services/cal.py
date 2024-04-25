from icalendar import Calendar, Event
from datetime import datetime
import pytz


# Функция для создания объекта календаря
def create_ical(event_info):
    cal = Calendar()
    event = Event()
    event.add('summary', event_info['Title'])
    event.add('dtstart', datetime.fromisoformat(event_info['DateBegin']).replace(tzinfo=pytz.utc))
    event.add('dtend', datetime.fromisoformat(event_info['DateEnd']).replace(tzinfo=pytz.utc))
    event.add('location', event_info['Place'])
    event.add('url', event_info['SiteLink'])
    cal.add_component(event)
    return cal.to_ical()
