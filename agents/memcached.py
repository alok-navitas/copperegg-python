from agents.agent import *


class Memcached(Agent):
    """
    Agent for monitoring memcached.
    """

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
