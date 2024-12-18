import os
import json
from PIL import Image, ImageDraw
from modules.conversion_tools.converter import Converter
import random
import subprocess

class ObjectDetection(Converter):
    def __init__(self, parent_dir, main_file, project_id, label_map = {}):
        super().__init__(parent_dir, main_file, project_id)
        self.yolo_dataset = {}
        self.image_count = {}
        self.label_map = label_map
        self.file_task_id = {}

    def transform_dataset(self):
        print(f"Label map:\n{self.label_map}")
        if not len(self.converted_dataset):
            self.converter()
        else:
            print(f'Converted dataset exits in {os.path.join(self.json_data_dir, 'converted_data.json')}')
        if not len(os.listdir(self.dataset_main_images)):
            self.transfer_images()
        else:
            print(f"Images exits in {self.dataset_images}")
        reverse_map = {}
        for key, value in self.label_map.items():
            reverse_map[value] = key
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not file_name in self.file_task_id.keys():
                self.file_task_id[file_name] = data['task_id']
            if not os.path.exists(os.path.join(self.dataset_main_images, file_name)):
                continue
            img_path = os.path.join(self.dataset_main_images, file_name)
            img = Image.open(img_path)
            img_sizes = img.size
            boxes = self.bounding_box_converter([data['x'], data['y'], data['width'], data['height']], img_sizes)
            text = data['rectanglelabels'][0]
            map_path = os.path.join(os.path.dirname(self.dataset_images), 'labels.json')
            output = [str(reverse_map[text])]
            output.extend(boxes)
            if not file_name in self.yolo_dataset:
                self.yolo_dataset[file_name] = [output]
            else:
                value = self.yolo_dataset[file_name]
                value.append(output)
                self.yolo_dataset[file_name] = value
        with open(os.path.join(self.json_data_dir, "file_task_id.json"), "w") as f:
            json.dump(self.file_task_id, f)
        with open(map_path, 'w') as f:
            json.dump(self.label_map, f)
        for key, values in self.yolo_dataset.items():
            image_path = os.path.join(self.dataset_images, key)
            text_path = os.path.join(self.dataset_labels, key.split('.')[0]+'.txt')
            self.copy_image(image_path)
            if not os.path.exists(text_path):
                for value in values: 
                    value = list(map(str, value))
                    with open(text_path, 'a') as f:
                        if len(value):
                            f.write(' '.join(value))
                            f.write('\n')
        return
    
    def draw_labels(self, add_text = True, text_size = 64, text_color = 'black', text_bg = 'white'):
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(os.path.join(self.dataset_main_images, file_name)):
                continue
            img_path = os.path.join(self.dataset_main_images, file_name)
            img = Image.open(img_path)
            img_sizes = img.size
            bboxes = self.json_to_xy([data['x'], data['y'], data['width'], data['height']], img_sizes)
            text = f"Task id: {data['task_id']}\n{data['rectanglelabels'][0]}"
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
            if int(task_id) in range(51612, 51645) or int(task_id) in range(52612, 52747) or int(task_id) in range(54979, 55811) or int(task_id) in range(46701, 46800):
                continue
            image_link = ann['data']['image']
            file = image_link.split('/')[-1]
            for result in ann['annotations'][-1]['result']:
                if result['type'] == 'rectanglelabels':
                    row = result['value']
                    row['task_id'] = task_id
                    row['file_name'] = file
                    row['image_link'] = image_link
                    self.converted_dataset.append(row)
        with open(os.path.join(self.json_data_dir, 'converted_dataset.json'), 'w') as f:
            json.dump(self.converted_dataset, f)
        return
    
    def bounding_box_converter(self, bbox, padding = 0):
        x, y, width, height = bbox
        x, y, w, h = (x + width / 2) / 100, (y + height / 2) / 100, width / 100, height / 100
        return x, y, w, h
    
    def json_to_xy(self, bbox, shape):
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
    
    def draw_bounding_box(self, image, bboxes, bbox_width=2, bbox_color='red'):
        draw = ImageDraw.Draw(image)
        x_min, y_min, x_max, y_max = bboxes
        draw.rectangle([x_min, y_min, x_max, y_max], outline=bbox_color, width=bbox_width)
        return image
    
    def splitter(self):
        images_path = self.dataset_images
        labels_path = self.dataset_labels
        images = os.listdir(images_path)
        images = [image for image in images if '.jpg' in image or '.png' in image]
        random.shuffle(images)
        total_len = len(images)
        train_range = (0, int(total_len*0.8))
        train_images = images[train_range[0]:train_range[1]]
        train_image_path = os.path.join(os.path.dirname(self.dataset_images), 'train/images')
        train_label_path = os.path.join(os.path.dirname(self.dataset_images), 'train/labels')
        valid_image_path = os.path.join(os.path.dirname(self.dataset_images), 'val/images')
        valid_label_path = os.path.join(os.path.dirname(self.dataset_images), 'val/labels')
        self.create_path(train_image_path)
        self.create_path(valid_image_path)
        self.create_path(train_label_path)
        self.create_path(valid_label_path)
        if len(os.listdir(train_image_path)) or len(os.listdir(valid_image_path)) or len(os.listdir(train_label_path)) or len(os.listdir(valid_label_path)):
            print('Data already exist in splited path')
            return
        for image in images:
            image_path = os.path.join(images_path, image)
            label_path = os.path.join(labels_path, f"{image.split('.')[0]}.txt")
            if image in train_images:
                subprocess.run(["mv", image_path, train_image_path])
                subprocess.run(["mv", label_path, train_label_path])
            else:
                subprocess.run(["mv", image_path, valid_image_path])
                subprocess.run(["mv", label_path, valid_label_path])
        subprocess.run(['rm', '-r', images_path])
        subprocess.run(['rm', '-r', labels_path])
        print("Data splitted")
        return