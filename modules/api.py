from modules.annotation_tools.label_studio_api import LabelStudioAPI
from modules.conversion_tools.easyocr_converter import EasyOCRConverter

def get_annotator(config):
    if config.type == 'LabelStudio':
        api = LabelStudioAPI(
            api_url=config.api_url,
            token=config.token
        )
    return api

def get_converter(config):
    if config['type'] == 'EasyOCR':
        api = EasyOCRConverter()
    return api

class API:
    def __init__(self, config):
        self.config = config
        self.anntator = get_annotator(self.config.annotation_tool)
        self.converter = get_converter(self.config.converter)

    def print_project_list(self):
        self.anntator.check_projects()
        return
    
    def download_dataset(self):
        self.anntator.get_json_dataset()
        return
    
    def build_dataset(self):
        self.converter.transform_dataset()
        return
    
    def draw_bounding_boxes(self):
        self.converter.draw_bboxes()
        return