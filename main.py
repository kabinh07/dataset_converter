from modules.api import API
import os
import yaml
from addict import Dict
import argparse

def main():
    with open('configs/config.yaml', 'r') as f:
        config = Dict(yaml.safe_load(f))

    api = API(config)
    parser = argparse.ArgumentParser()
    parser.add_argument("method", type=str, help="type checkprojects to see the availbale projects\ntype download to download dataset\ntype createdataset to build images and labels from downloaded datset\ntype drawbbox to draw bbox on images and save them")
    args = parser.parse_args()

    if args.method == 'download':
        api.download_dataset()

    elif args.method == 'checkprojects':
        api.print_project_list()
    
    elif args.method == 'createdataset':
        api.build_dataset()

    elif args.method == 'drawbbox':
        api.draw_bounding_boxes()
    
    else:
        print('Invalid argument.')
    

if __name__ == "__main__":
    main()