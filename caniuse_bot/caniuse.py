from enum import Enum
from json.decoder import JSONDecodeError
from typing import Dict, List, Union
import os
import pathlib
import json
import re
import difflib

from .errors import ConfigurationError


class CanIUseDB:
    def get_database(self) -> Dict:
        try:
            data: Dict = json.load(self.data_path.open())
        except OSError:
            raise ConfigurationError("Couldn't open data file.")

        return data

    def find_features(self, query) -> List[dict]:
        db = self.get_database()
        data = db['data']
        results = []
        term = re.sub(r'\W*', '', query)

        for item in data.items():
            key, feature = item
            title = feature.get('title', '')
            description = feature.get('description', '')
            keywords = feature.get('keywords', '')
            categories = ''.join(feature.get('categories', []))

            search = (key + title + description + keywords +
                      categories).lower()

            matcher = re.sub(r'\W*', '', search)

            if matcher.find(term) > -1:
                results.append(feature)

        return results

    def get_features(self, query) -> Union[List[Dict], Dict, None]:
        db = self.get_database()
        data = db['data']

        feature: Dict = data.get(query)
        if feature is not None:
            return feature

        features = self.find_features(query)
        if len(features) == 1:
            return features[0]
        elif len(features) > 1:
            return features
        else:
            return None

    def __init__(self):
        data_path = os.environ.get("CANIUSE_PATH")
        if data_path is None:
            raise ConfigurationError("CANIUSE_PATH")

        self.data_path = pathlib.Path(data_path)


class Browser(Enum):
    IE = "ie"
    EDGE = "edge"
    FIREFOX = "firefox"
    CHROME = "chrome"
    SAFARI = "safari"
    SAFARI_iOS = "ios_saf"
    OPERA = "opera"


def support_for_feature(feature_obj: Dict, browser: Browser) -> List[Dict]:
    browser_code = browser.value
    stats = list(feature_obj['stats'][browser_code].items())

    events = []
    events.append({'version': stats[-1][0], 'status': stats[-1][1][0]})

    for version, status in stats[::-1]:
        if events[-1]['status'] == status[0]:
            events[-1]['version'] = version
        else:
            events.append({'version': version, 'status': status[0]})

    return events
