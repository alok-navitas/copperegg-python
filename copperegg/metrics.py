import requests
import json

DEFAULT_API_HOST = 'https://api.copperegg.com'
DEFAULT_API_VERSION = 'v2'


class Metrics(object):

    def __init__(self, api_key, api_host=DEFAULT_API_HOST, api_version=DEFAULT_API_VERSION):
        self.api_key = api_key
        self.base_url = '{}/{}/revealmetrics'.format(api_host, api_version)

    def store_sample(self, group_name, identifier, timestamp, values):
        sample = {
            'identifier': identifier,
            'timestamp': timestamp,
            'values': values,
        }
        self._post('/samples/{}.json'.format(group_name), data=sample)

    def samples(self, group_name, metric_name, start_time=None, duration=None, sample_size=None):
        data = {
            'queries': {group_name: [{'metrics': [metric_name]}]}
        }
        if start_time:
            data['start_time'] = start_time
        if duration:
            data['duration'] = duration
        if sample_size:
            data['sample_size'] = sample_size
        samples = self._get('/samples.json', data=data)
        return samples

    def metric_groups(self):
        return self._get('/metric_groups.json')

    def metric_group(self, group_name):
        return self._get('/metric_groups/{}.json'.format(group_name))

    def create_metric_group(self, group_name, metrics):
        data = {
            'name': group_name,
            'metrics': metrics
        }
        return self._post('/metric_groups.json', data=data)

    def dashboards(self):
        return self._get('/dashboards.json')

    def create_dashboard(self, dashboard_name, widgets):
        data = {
            'name': dashboard_name,
            'data': {
                'widgets': dict((str(t[0]), t[1]) for t in enumerate(widgets))
            }
        }
        return self._post('/dashboards.json', data)

    def _get(self, path, params=None, data=None):
        headers = None
        if data is not None:
            data = json.dumps(data)
            headers = {'content-type': 'application/json'}
        return requests.get(self.base_url + path, auth=(self.api_key, None),
                            params=params, data=data, headers=headers).json()

    def _post(self, path, data=None):
        headers = None
        if data is not None:
            data = json.dumps(data)
            headers = {'content-type': 'application/json'}
        return requests.post(self.base_url + path, auth=(self.api_key, None),
                             data=data, headers=headers).json()
