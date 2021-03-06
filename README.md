# copperegg-python

CopperEgg API library for Python

## Installation

```
git clone git@github.com:hdmessaging/copperegg-python.git
cd copperegg-python
pip install -r requirements.txt
```

## Getting started

### Setup

```python
from copperegg.metrics import Metrics

# Get a Metrics object:
api_key = 'xxxxxxxxxxxxxxxx'
metrics = Metrics(api_key)
```

### Creating a metric group

```
group = create_metric_group('coffee_group',  [
    {
        'type': 'ce_counter',
        'name': 'cups_served',
        'unit': 'Cups'
    },
    {
        'type': 'ce_gauge_f',
        'name': 'current_amount',
        'unit': 'Liters'
    }
])
```

### Getting a metric group

```python
group = metrics.metric_group('coffee_group')
```

### Sending a data sample

```python
import time
metrics.store_sample('coffee_group', 'lolcathost', int(time.time()), {
    'cups_served': 12,
    'current_amount': 0.1
})
```

### Monitoring

Create a config file `config.json`:
```json
{
    "api_key": "API_KEY",
    "agents": {
        "memcached": {
            "plugin_module": "agents.memcached",
            "plugin_class": "Memcached",
            "dashboard_name": "Memcached Dashboard",
            "servers": [
                {
                    "name": "lolcathost",
                    "hostname": "127.0.0.1",
                    "port": 11211
                }
            ],
            "interval": 60
        }
    }
}
```

Start the agent:
```
python monitor.py -g memcached
```
