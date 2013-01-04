import copperegg.metrics
import memcache
import time
from functools import partial
from operator import itemgetter


class Metric(object):

    def __init__(self, name, getter=None, label=None, kind='gauge', type=int):
        self.name = name
        self.getter = getter if getter else itemgetter(name)
        self.label = label if label else name
        self.kind = kind
        self.type = type

    def to_copperegg_metric(self):
        suffix = '_f' if self.type == float else ''
        ce_type = 'ce_{}{}'.format(self.kind, suffix)
        return {
            'type': ce_type,
            'name': self.name,
            'label': self.label
        }

    def __repr__(self):
        return '{}{}'.format(
            self.__class__.__name__,
            (self.name, self.getter, self.label, self.kind, self.type)
        )


gauge = partial(Metric, kind='gauge')
counter = partial(Metric, kind='counter')


class Agent(object):

    metrics = []

    def __init__(self, api_key, group_name, dashboard_name, servers):
        self.group_name = group_name
        self.dashboard_name = dashboard_name
        self.servers = servers
        self.client = memcache.Client(map(self.make_server_str, self.servers))
        self.api = copperegg.metrics.Metrics(api_key)

    def create_dashboard(self):
        dashboards = filter(lambda d: d['name'] == self.dashboard_name, self.api.dashboards())
        dashboard = dashboards[0] if len(dashboards) else None
        if not dashboard:
            group_name = self.metric_group['name']
            widgets = []
            for server in self.servers:
                for metric in self.metric_group['metrics']:
                    widget = {
                        'type': 'metric',
                        'style': 'both',
                        'metric': [group_name, int(metric['position']), metric['label']],
                        'match': 'select',
                        'match_param': server['name']
                    }
                    widgets.append(widget)
            dashboard = self.api.create_dashboard(self.dashboard_name, widgets)
        return dashboard

    def get_metric_group(self):
        return self.api.metric_group(self.group_name)

    def create_metric_group(self):
        group = self.get_metric_group()
        if not group:
            group = self.api.create_metric_group(self.group_name, [
                m.to_copperegg_metric() for m in self.metrics
            ])
        self.metric_group = group
        return group

    def make_server_str(self, server):
        return '{hostname}:{port}'.format(**server)

    def get_server_by_identifier(self, server_identifier):
        for server in self.servers:
            if server_identifier.startswith(self.make_server_str(server)):
                return server
        return None

    def sample(self):
        result = self.client.get_stats()
        data = {}
        for entry in result:
            server_identifier, stats = entry
            server = self.get_server_by_identifier(server_identifier)
            if server:
                server_name = server.get('name', server_identifier)
                server_data = {}
                for metric in self.metrics:
                    value = metric.getter(stats)
                    server_data[metric.name] = metric.type(value)
                data[server_name] = server_data
        return data

    def report(self):
        sample = self.sample()
        if sample:
            for identifier, values in sample.iteritems():
                self.api.store_sample(self.group_name, identifier,
                                      int(time.time()), values)
