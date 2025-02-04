from fastapi.templating import Jinja2Templates
from datetime import datetime


def _format_datetime(value: datetime, fmt="%Y-%m-%d %H:%M:%S"):
    return value.strftime(fmt)


templates = Jinja2Templates(directory="templates")
templates.env.filters["strftime"] = _format_datetime

# other `strftime` formats
# formatted_date1 = now.strftime("%A, %d %B %Y") Tuesday, 04 February 2025
# formatted_date2 = now.strftime("%I:%M %p") 02:23 PM
# formatted_date3 = now.strftime("%d/%m/%Y") 04/02/2025
# formatted_date3 = now.strftime(""%Y-%m-%d %H:%M:%S"") 2025-02-04 19:43:11
