from pymongo import MongoClient
from pymongo.collection import Collection
from app.core import settings
from urllib.parse import quote_plus
from enum import Enum
from typing import Union

uri = "%s://%s:%s@%s" % (
    settings.MONGO_SCHEME,
    quote_plus(settings.MONGO_USER),
    quote_plus(settings.MONGO_PASSWORD),
    settings.MONGO_HOST,
)

client = MongoClient(uri)
db = client[settings.DATABASE_NAME]


class MONGO_COLLECTIONS(Enum):
    EVENTS = "events"
    USERS = "users"
    INVITE = "invites"


def get_collection(collection_name: MONGO_COLLECTIONS) -> Union[Collection, None]:
    try:
        coll_name = collection_name.value
        return db[coll_name]
    # catching the error just to throw it again? Yes, i know 🙃
    except AttributeError as e:
        print(f"AttributeError: {e}")
        return None
    except AssertionError as e:
        print(f"AssertionError: {e}")
        return None
    except ArithmeticError as e:
        print(f"ArithmeticError: {e}")
        return None
