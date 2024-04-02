from json import JSONEncoder
from bson import ObjectId
import numpy as np

class JsonEncoder(JSONEncoder):
    """
    Custom JSON encoder
    """

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, None):
            return ""
        if isinstance(o, dict):
            if 'source' in o and isinstance(o['source'], dict) and 'name' in o['source'] and isinstance(o['source']['name'], float) and np.isnan(o['source']['name']):
                o['source']['name'] = ""
        return JSONEncoder.default(self, o)