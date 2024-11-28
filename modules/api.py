from modules.annotation_tools.label_studio_api import LabelStudioAPI
from modules.conversion_tools.tools.text_recognizer import TextRecognizerConverter
from modules.conversion_tools.tools.craft import Craft
from modules.conversion_tools.tools.object_detection import ObjectDetection
import subprocess
import os

def struct_data_dir(config):
    parent = config.name.lower()
    main_file = config.main_files.lower()
    parent_path = os.path.join('data', parent)
    main_file_path = os.path.join('main_files', main_file)
    if not os.path.exists(main_file_path):
        print(f"Path doesn't exist {main_file_path}")
        return
    if not os.listdir(main_file_path):
        print(f'Please copy files to {main_file_path}')
        return
    return parent_path, main_file_path
    
class API:
    def __init__(self, config):
        self.config = config
        self.parent_dir, self.main_file = struct_data_dir(self.config.dataset)
        self.anntator = self.__get_annotator(self.config.annotation_tool)
        self.converter = self.__get_converter(self.config.converter)

    def __get_converter(self, config):
        if config['type'] == 'TextRecognizer':
            api = TextRecognizerConverter(self.parent_dir, self.main_file)
        elif config['type'] == 'Craft':
            api = Craft(self.parent_dir, self.main_file)
        elif config['type'] == 'ObjectDetection':
            api = ObjectDetection(self.parent_dir, self.main_file)
        return api
    
    def __get_annotator(self, config):
        if config.type == 'LabelStudio':
            api = LabelStudioAPI(
                api_url=config.api_url,
                token=config.token
            )
        return api

    def print_project_list(self):
        self.anntator.check_projects()
        return
    
    def download_dataset(self, project_id):
        self.anntator.get_json_dataset(project_id, self.parent_dir)
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