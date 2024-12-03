import os
import json
import pandas as pd
from PIL import Image, ImageDraw
from modules.conversion_tools.converter import Converter

class TextRecognizerConverter(Converter):
    def __init__(self, parent_dir, main_file, project_id):
        super().__init__(parent_dir, main_file, project_id)
        self.image_count = {}
        self.ocr_dataset = []

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
            if not file_name in self.image_count:
                self.image_count[file_name] = 0
            else:
                count = self.image_count[file_name]
                count += 1
                self.image_count[file_name] = count
            img_path = os.path.join(self.dataset_main_images, file_name)
            img = Image.open(img_path)
            img_sizes = img.size
            raw_bbox = [data['x'], data['y'], data['width'], data['height']]
            padded_bbox = self.add_padding(raw_bbox, 0.25, 0.5)
            bboxes = self.bounding_box_converter(padded_bbox, img_sizes)
            text = data['text'][0]
            try:
                new_file_name = f"{file_name.split('.')[0]}_{self.image_count[file_name]}.{file_name.split('.')[-1]}"
                self.crop_segments(img, bboxes, new_file_name)
                self.ocr_dataset.append(
                    {
                        'filename': new_file_name,
                        'words': text
                    }
                )
            except Exception as e:
                print(f"Failed to crop and convert csv file for data:\n{data}")
        df = pd.DataFrame(self.ocr_dataset)
        df.to_csv(os.path.join(self.dataset_labels, 'labels.csv'), index=False)
        return
    
    def draw_labels(self, add_text = True, text_size = 16, text_color = 'black', text_bg = 'white'):
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(os.path.join(self.dataset_main_images, file_name)):
                continue
            img_path = os.path.join(self.dataset_main_images, file_name)
            img = Image.open(img_path)
            img_sizes = img.size
            bboxes = self.bounding_box_converter([data['x'], data['y'], data['width'], data['height']], img_sizes)
            text = f"Task id: {data['task_id']}\n{data['text'][0]}"
            new_img = self.draw_bounding_box(img, bboxes)
            if add_text:
                new_img = self.add_text_to_image(img, img_sizes, text, text_size, text_color, text_bg)
            if not file_name in self.image_count:
                self.image_count[file_name] = 0
            else:
                value = self.image_count[file_name]
                value += 1
                self.image_count[file_name] = value
            new_img.save(os.path.join(self.bbox_dir, f"{str(data['task_id'])}_{self.image_count[file_name]}.jpg"))
        return
    
    def converter(self):
        print(len(self.dataset))
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
        image_width = shape[0]
        image_height = shape[1]
        r_x = (x/100)*image_width
        r_y = (y/100)*image_height
        r_w = (width/100)*image_width
        r_h = (height/100)*image_height

        x1 = r_x 
        y1 = r_y 
        x2 = r_x + r_w
        y2 = r_y + r_h
        
        return x1, y1, x2, y2
    
    def draw_bounding_box(self, image, bboxes, bbox_width=2, bbox_color = 'red'):
        draw = ImageDraw.Draw(image)
        x_min, y_min, x_max, y_max = bboxes
        draw.rectangle([x_min, y_min, x_max, y_max], outline=bbox_color, width=bbox_width)
        return image
    
    def add_padding(self, bbox, x_pad, y_pad):
        x, y, w, h = bbox
        x, y, w, h = x - x_pad, y - y_pad, w + x_pad, h + y_pad
        return x, y, w, h
    
        
    

    

    

    

    

    

    