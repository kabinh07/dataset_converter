import os
import pandas as pd
from modules.conversion_tools.converter import Converter

class Craft(Converter):
    def __init__(self, parent_dir, main_file):
        super().__init__(parent_dir, main_file)
        self.dir_check()
        self.loader()
        self.craft_dataset = {}
    
    def transform_dataset(self):
        self.convert_transfer()
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(os.path.join(self.dataset_main_images, file_name)):
                continue
            img_path = os.path.join(self.main_file_dir, file_name)
            img, img_sizes = self.image_loader(img_path)
            boxes = self.xywh_to_points([data['x'], data['y'], data['width'], data['height']], img_sizes)
            text = data['text'][0]
            single_array_boxes = []
            for box in boxes:
                single_array_boxes.extend(box)
            single_array_boxes.append(text)
            output = ','.join([str(element) for element in single_array_boxes])
            if not file_name in self.craft_dataset:
                self.craft_dataset[file_name] = [output]
            else:
                value = self.craft_dataset[file_name]
                value.append(output)
                value = list(set(value))
                self.craft_dataset[file_name] = value
        for key, values in self.craft_dataset.items():
            image_path = os.path.join(self.dataset_images, key)
            text_path = os.path.join(self.dataset_labels, key.split('.')[0]+'.txt')
            self.copy_image(image_path)
            if not os.path.exists(text_path):
                for value in values: 
                    with open(text_path, 'a') as f:
                        f.write(value)
                        f.write('\n')
        return
            

