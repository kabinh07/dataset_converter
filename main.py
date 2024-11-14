from modules.annotation_api import get_annotator
import os
import yaml
from addict import Dict

if __name__ == "__main__":
    with open('configs/config.yaml', 'r') as f:
        config = Dict(yaml.safe_load(f))
    api = get_annotator(config.annotation_tool)
    response = api.get_json_dataset(6)