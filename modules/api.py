from modules.annotation_tools.label_studio_api import LabelStudioAPI
from modules.conversion_tools.tools.text_recognizer import TextRecognizerConverter
from modules.conversion_tools.tools.craft import Craft
from modules.conversion_tools.tools.object_detection import ObjectDetection

from modules.drawing_tools.tools.coco_format import COCOFormat

from modules.counter.object_counter import ObjectCounter

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
        self.project_id = config.annotation_tool.project_id
        if self.config.dataset:
            self.parent_dir, self.main_file = struct_data_dir(self.config.dataset)
        if self.config.annotation_tool:
            self.anntator = self.__get_annotator(self.config.annotation_tool)
        if self.config.converter:
            self.converter = self.__get_converter(self.config.converter)
        if self.config.draw:
            self.drawing_tool = self.__get_drawing_tool(self.config.draw)
        self.object_counter = ObjectCounter(config)

    def __get_converter(self, config):
        if not self.project_id:
            print("Check projects and insert project id in config file")
            return
        if config['type'] == 'TextRecognizer':
            api = TextRecognizerConverter(self.parent_dir, self.main_file, self.project_id)
        elif config['type'] == 'Craft':
            api = Craft(self.parent_dir, self.main_file, self.project_id)
        elif config['type'] == 'ObjectDetection':
            api = ObjectDetection(self.parent_dir, self.main_file, self.project_id)
        return api
    
    def __get_annotator(self, config):
        if config.type == 'LabelStudio':
            api = LabelStudioAPI(
                api_url=config.api_url,
                token=config.token
            )
        return api
    
    def __get_drawing_tool(self, config):
        if config.type == 'COCO':
            api = COCOFormat(config, self.parent_dir)
        return api

    def print_project_list(self):
        self.anntator.check_projects()
        return
    
    def download_dataset(self):
        if not self.project_id:
            print("Check projects and insert project id in config file")
            return
        self.anntator.get_json_dataset(self.project_id, self.parent_dir)
        return
    
    def build_dataset(self):
        self.converter.transform_dataset()
        return
    
    def split_dataset(self):
        self.converter.splitter()
    
    def draw_bounding_boxes(self):
        self.converter.draw_labels()
        return
    
    def draw_coco(self):
        self.drawing_tool.draw_labels()
        return
    
    def obj_counter(self):
        self.object_counter.get_object_count()
    
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