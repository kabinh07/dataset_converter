from modules.api import API
import yaml
from addict import Dict
import argparse
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("method", type=str, help="type checkprojects to see the availbale projects\ntype download to download dataset\ntype createdataset to build images and labels from downloaded datset\ntype drawbbox to draw bbox on images and save them")
    parser.add_argument("--config", type=str, help="insert config file name")
    args = parser.parse_args()

    config_file = os.path.join('configs', 'config.yaml')
    if args.config:
        config_file = os.path.join('configs', args.config)
    
    with open(config_file, 'r') as f:
        config = Dict(yaml.safe_load(f))
    if config.annotation_tool.api_url is None:
        url = os.getenv('URL')
        config.annotation_tool.api_url = url
    if config.annotation_tool.token is None:
        token = os.getenv('TOKEN')
        config.annotation_tool.token = token
    api = API(config)

    if args.method == 'checkprojects':
        api.print_project_list()
    
    elif args.method == 'download':
        api.download_dataset()
    
    elif args.method == 'build':
        api.build_dataset()
    
    elif args.method == 'delete':
        api.remove_all_data()

    elif args.method == 'draw':
        api.draw_bounding_boxes()

    elif args.method == 'annotate':
        api.draw_coco()
    
    elif args.method == 'counter':
        api.obj_counter()
    
    else:
        print('Invalid argument.')
    
if __name__ == "__main__":
    main()