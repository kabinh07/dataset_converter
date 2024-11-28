import os
import json
from PIL import Image, ImageDraw
from modules.conversion_tools.converter import Converter

class ObjectDetection(Converter):
    def __init__(self, parent_dir, main_file):
        super().__init__(parent_dir, main_file)
        self.yolo_dataset = {}
        self.image_count = {}

    def transform_dataset(self):
        if not len(self.converted_dataset):
            self.converter()
        else:
            print(f'Converted dataset exits in {os.path.join(self.json_data_dir, 'converted_data.json')}')
        if not len(os.listdir(self.dataset_main_images)):
            self.transfer_images()
        else:
            print(f"Images exits in {self.dataset_images}")
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(os.path.join(self.dataset_main_images, file_name)):
                continue
            img_path = os.path.join(self.dataset_main_images, file_name)
            img = Image.open(img_path)
            img_sizes = img.size
            boxes = self.xywh_to_yolo([data['x'], data['y'], data['width'], data['height']], img_sizes)
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
    
    def converter(self):
        for ann in self.dataset:
            task_id = ann['id']
            image_link = ann['data']['image']
            file = image_link.split('/')[-1]
            for result in ann['annotations'][-1]['result']:
                if result['type'] == 'textarea':
                    row = result['value']
                    row['task_id'] = task_id
                    row['file_name'] = file
                    row['image_link'] = image_link
                    self.converted_dataset.append(row)
        with open(os.path.join(self.json_data_dir, 'converted_dataset.json'), 'w') as f:
            json.dump(self.converted_dataset, f)
        return
    
    def bounding_box_converter(self, bbox, shape):
        x, y, width, height = bbox
        x, y, w, h = (x + width / 2) / 100, (y + height / 2) / 100, width / 100, height / 100
        return x, y, w, h