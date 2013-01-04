import argparse
import json
import importlib
import time

parser = argparse.ArgumentParser(description='Monitor things with CopperEgg.')
parser.add_argument('-g', '--group', dest='group', help='Group name', required=True)
parser.add_argument('-c', '--config', dest='config', help='Config file', default='config.json')
args = parser.parse_args()

group_name = args.group
config = None
with open(args.config) as config_file:
    config = json.loads(config_file.read())
group_config = config['agents'][group_name]

module = importlib.import_module(group_config['plugin_module'])
Agent = getattr(module, group_config['plugin_class'])

agent = Agent(config['api_key'], group_name, group_config['dashboard_name'], group_config['servers'])
interval = group_config['interval']
agent.create_metric_group()
agent.create_dashboard()

while True:
    agent.report()
    time.sleep(interval)
