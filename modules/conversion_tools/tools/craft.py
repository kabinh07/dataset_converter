import os
import json
from PIL import Image, ImageDraw
from modules.conversion_tools.converter import Converter

class Craft(Converter):
    def __init__(self, parent_dir, main_file, project_id):
        super().__init__(parent_dir, main_file, project_id)
        self.craft_dataset = {}
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
            boxes = self.bounding_box_converter([data['x'], data['y'], data['width'], data['height']], img_sizes)
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

        top_left = (int(r_x)+1, int(r_y)+1)
        top_right = (int(r_x+r_w)+1, int(r_y)+1)
        bottom_left = (int(r_x+r_w)+1, int(r_y+r_h)+1)
        bottom_right = (int(r_x)+1, int(r_y+r_h)+1)

        return top_left, top_right, bottom_left, bottom_right
    
    def draw_bounding_box(self, image, bboxes, bbox_width=2, bbox_color = 'red'):
        draw = ImageDraw.Draw(image)
        x_1 = bboxes[0]
        x_2 = bboxes[1]
        x_3 = bboxes[2]
        x_4 = bboxes[3]

        draw.line([x_1, x_2], fill=bbox_color, width=bbox_width)
        draw.line([x_2, x_3], fill=bbox_color, width=bbox_width)
        draw.line([x_3, x_4], fill=bbox_color, width=bbox_width)
        draw.line([x_4, x_1], fill=bbox_color, width=bbox_width)
        return image

