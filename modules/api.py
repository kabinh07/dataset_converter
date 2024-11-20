from modules.annotation_tools.label_studio_api import LabelStudioAPI
from modules.conversion_tools.text_recognizer import TextRecognizerConverter
import subprocess
import os

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

    def print_project_list(self):
        self.anntator.check_projects()
        return
    
    def download_dataset(self, project_id):
        self.anntator.get_json_dataset(project_id)
        return
    
    def build_dataset(self):
        self.converter.transform_dataset()
        return
    
    def draw_bounding_boxes(self):
        self.converter.draw_labels()
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