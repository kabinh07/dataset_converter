from modules.annotation_tools.label_studio_api import LabelStudioAPI
from modules.conversion_tools.text_recognizer import TextRecognizerConverter
import subprocess
import os

def struct_data_dir(config):
    parent = config.name
    main_file = config.main_files
    parent_path = os.path.join('data', parent)
    main_file_path = os.path.join('main_files', main_file)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    if not os.path.exists(main_file_path):
        print(f"Path doesn't exist {main_file_path}")
        return
    if not os.listdir(main_file_path):
        print(f'Please copy files to {main_file_path}')
        return
    return parent_path, main_file_path

def get_annotator(config):
    if config.type == 'LabelStudio':
        api = LabelStudioAPI(
            api_url=config.api_url,
            token=config.token
        )
    return api

def get_converter(config):
    if config['type'] == 'TextRecognizer':
        api = TextRecognizerConverter()
    return api

class API:
    def __init__(self, config):
        self.config = config
        self.anntator = get_annotator(self.config.annotation_tool)
        self.converter = get_converter(self.config.converter)
        self.parent_dir, self.main_file = struct_data_dir(self.config.dataset)

    def print_project_list(self):
        self.anntator.check_projects()
        return
    
    def download_dataset(self, project_id):
        self.anntator.get_json_dataset(project_id, self.parent_dir)
        return
    
    def build_dataset(self):
        self.converter.transform_dataset(self.parent_dir, self.main_file)
        return
    
    def draw_bounding_boxes(self):
        self.converter.draw_labels(self.parent_dir, self.main_file)
        return
    
    def remove_all_data(self):
        if len(os.listdir('bbox_images/')):
            subprocess.run(['rm', '-rf', 'bbox_images/*'])
        if len(os.listdir('data/')):
            subprocess.run(['rm', '-rf', 'data/*'])
        if len(os.listdir('dataset/images')):
            subprocess.run(['rm', '-rf', 'dataset/images/*'])
        if len(os.listdir('dataset/labels')):
            subprocess.run(['rm', '-rf', 'dataset/labels/*'])
        if len(os.listdir('dataset/main_images')):
            subprocess.run(['rm', '-rf', 'dataset/main_images/*'])
        return