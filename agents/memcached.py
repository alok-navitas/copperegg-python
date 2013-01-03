import copperegg.metrics
import memcache
import time
from functools import partial
from operator import itemgetter

COPPEREGG_API_KEY = None


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


class Memcached(object):

    metrics = [
        gauge('accepting_conns'),
        gauge('auth_cmds'),
        gauge('auth_errors'),
        gauge('bytes'),
        gauge('bytes_read'),
        gauge('bytes_written'),
        gauge('cas_badval'),
        gauge('cas_hits'),
        gauge('cas_misses'),
        gauge('cmd_flush'),
        gauge('cmd_get'),
        gauge('cmd_set'),
        gauge('conn_yields'),
        gauge('connection_structures'),
        gauge('curr_connections'),
        gauge('curr_items'),
        gauge('decr_hits'),
        gauge('decr_misses'),
        gauge('delete_hits'),
        gauge('delete_misses'),
        gauge('evictions'),
        gauge('get_hits'),
        gauge('get_misses'),
        gauge('incr_hits'),
        gauge('incr_misses'),
        gauge('limit_maxbytes'),
        gauge('listen_disabled_num'),
        gauge('reclaimed'),
        gauge('rusage_system', type=float),
        gauge('rusage_user', type=float),
        gauge('threads'),
        gauge('total_connections'),
        gauge('total_items'),
        counter('uptime'),
    ]

    def __init__(self, group_name, servers):
        self.group_name = group_name
        self.servers = servers
        self.client = memcache.Client(map(self.make_server_str, self.servers))
        self.api = copperegg.metrics.Metrics(COPPEREGG_API_KEY)

    def get_metric_group(self):
        return self.api.metric_group(self.group_name)

    def create_metric_group(self):
        group = self.api.metric_group(self.group_name)
        if not group:
            group = self.api.create_metric_group(self.group_name, [
                m.to_copperegg_metric() for m in self.metrics
            ])
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
