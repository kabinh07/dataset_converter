from modules.api import API
import yaml
from addict import Dict
import argparse
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    url = os.getenv('URL')
    token = os.getenv('TOKEN')
    with open('configs/config.yaml', 'r') as f:
        config = Dict(yaml.safe_load(f))
    config.annotation_tool.api_url = url
    config.annotation_tool.token = token
    print(config)
    api = API(config)
    parser = argparse.ArgumentParser()
    parser.add_argument("method", type=str, help="type checkprojects to see the availbale projects\ntype download to download dataset\ntype createdataset to build images and labels from downloaded datset\ntype drawbbox to draw bbox on images and save them")
    parser.add_argument("--project", type=int, help="type your project id")
    args = parser.parse_args()

    project_id = None

    if args.method == 'download':
        if not args.project:
            print("please add project id")
            return
        project_id = args.project
        api.download_dataset(project_id)

    elif args.method == 'checkprojects':
        api.print_project_list()
    
    elif args.method == 'build':
        api.build_dataset()
    
    elif args.method == 'delete':
        api.remove_all_data()

    elif args.method == 'draw':
        api.draw_bounding_boxes()
    
    else:
        print('Invalid argument.')
    
if __name__ == "__main__":
    main()