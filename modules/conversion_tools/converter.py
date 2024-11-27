import os
import subprocess
import json
import urllib
from PIL import Image, ImageDraw, ImageFont

class Converter:
    def __init__(self, parent_dir, main_file):
        self.parent_dir = parent_dir
        self.main_file_dir = main_file
        self.dataset = []
        self.converted_dataset = []

    def dir_check(self):
        self.json_data_dir = os.path.join(self.parent_dir, 'json_data')
        self.dataset_images = os.path.join(self.parent_dir, 'dataset/images')
        self.dataset_labels = os.path.join(self.parent_dir, 'dataset/labels')
        self.dataset_main_images = os.path.join(self.parent_dir, 'dataset/main_images')
        self.bbox_dir = os.path.join(self.parent_dir, 'bbox_images')
        if not os.path.exists(self.dataset_images):
            os.makedirs(self.dataset_images)
        if not os.path.exists(self.dataset_labels):
            os.makedirs(self.dataset_labels)
        if not os.path.exists(self.dataset_main_images):
            os.makedirs(self.dataset_main_images)
        if not os.path.exists(self.bbox_dir):
            os.makedirs(self.bbox_dir)
        return
    
    def loader(self):
        dataset_path = os.path.join(self.json_data_dir, 'dataset.json')
        if not os.path.exists(dataset_path):
            print(f"No dataset found in {dataset_path}")
            return
        with open(dataset_path, 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        converted_dataset_path = os.path.join(self.json_data_dir, 'converted_dataset.json')
        if not os.path.exists(converted_dataset_path):
            print(f"No converted dataset found in {converted_dataset_path}")
            print(f"Only dataset loaded from path {dataset_path}")
            return
        with open(converted_dataset_path, 'r') as f:
            self.converted_dataset = json.load(f)
        print(f"Both dataset and converted dataset loaded from path {dataset_path} & {converted_dataset_path}")
        return 
    
    def image_loader(self, img_path):
        img = Image.open(img_path)
        img_w, img_h = img.size
        img_sizes = [img_w, img_h]
        return img, img_sizes
    
    def convert_transfer(self): 
        if not len(self.converted_dataset):
            self.__converter()
        else:
            print(f'Converted dataset exits in {os.path.join(self.json_data_dir, 'converted_data.json')}')
        if not len(os.listdir(self.dataset_main_images)):
            self.__transfer_images()
        else:
            print(f"Images exits in {self.dataset_images}")
    
    def __converter(self):
        for ann in self.dataset:
            task_id = ann['id']
            image_link = ann['data']['image']
            file = image_link.split('/')[-1]
            for result in ann['annotations'][0]['result']:
                if result['type'] == 'textarea':
                    row = result['value']
                    row['task_id'] = task_id
                    row['file_name'] = file
                    row['image_link'] = image_link
                    self.converted_dataset.append(row)
        with open(os.path.join(self.json_data_dir, 'converted_dataset.json'), 'w') as f:
            json.dump(self.converted_dataset, f)
        return
    
    def __image_downloader(self, url):
        if not url[:8] == 'https://':
            print(f'{url} is not valid.')
            return
        try:
            file_name = url.split('/')[-1]
            urllib.request.urlretrieve(url, os.path.join(self.dataset_main_images, file_name))
            return True
        
        except Exception as e:
            print(f'{url} is not accessable.')
            return False
    
    def __transfer_images(self):
        for data in self.converted_dataset:
            if not os.path.exists(os.path.join(self.main_file_dir, data['file_name'])):
                downloaded = self.__image_downloader(data['image_link'])
                if not downloaded:
                    continue
            if not os.path.exists(os.path.join(self.dataset_main_images, data['file_name'])):
                subprocess.run(['cp', os.path.join(self.main_file_dir, data['file_name']), self.dataset_main_images])
        return
    
    def copy_image(self, path):
        image_name = path.split('/')[-1]
        if not os.path.exists(path):
            subprocess.run(['cp', os.path.join(self.dataset_main_images, image_name), path])
        return
    
    def xywh_to_xyxy(self, bbox, shape):
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
    
    def xywh_to_points(self, bbox, shape):
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

    def crop_segments(self, image, bboxes, name):
        x1, y1, x2, y2 = bboxes
        crop_img = image.crop((x1, y1, x2, y2))
        path = os.path.join(self.dataset_images, name)
        crop_img.save(path)
        return
    
    def draw_bounding_box(self, image, bboxes, method, bbox_width=2, bbox_color = 'red'):
        draw = ImageDraw.Draw(image)
        if method == 'rect':
            x_min, y_min, x_max, y_max = bboxes
            draw.rectangle([x_min, y_min, x_max, y_max], outline=bbox_color, width=bbox_width)
        elif method == 'lines':
            x_1 = bboxes[0]
            x_2 = bboxes[1]
            x_3 = bboxes[2]
            x_4 = bboxes[3]
            
            draw.line([x_1, x_2], fill=bbox_color, width=bbox_width)
            draw.line([x_2, x_3], fill=bbox_color, width=bbox_width)
            draw.line([x_3, x_4], fill=bbox_color, width=bbox_width)
            draw.line([x_4, x_1], fill=bbox_color, width=bbox_width)
        return image
    
    def __fit_text_in_white_background(self, text, img_sizes, background, text_color):
        img = Image.new("RGB", (img_sizes[0], img_sizes[1]), background)
        draw = ImageDraw.Draw(img)
        middle_points = (5, img_sizes[1]/2)
        draw.text(middle_points, str(text), font=self.font, fill=text_color)
        return img
    
    def __collage_image(self, img1, img2, orientation='horizontal'):
        # Resize images to the same height or width based on orientation
        if orientation == 'horizontal':
            # Resize to the same height
            img1 = img1.resize((img1.width, img2.height))
            img2 = img2.resize((img2.width, img1.height))
            # Create a blank image wide enough to fit both images
            collage_width = img1.width + img2.width
            collage_height = img1.height
        elif orientation == 'vertical':
            # Resize to the same width
            img1 = img1.resize((img2.width, img1.height))
            img2 = img2.resize((img2.width, img2.height))
            # Create a blank image tall enough to fit both images
            collage_width = img1.width
            collage_height = img1.height + img2.height
        else:
            raise ValueError("Invalid orientation. Choose 'horizontal' or 'vertical'.")

        collage = Image.new("RGB", (collage_width, collage_height), "white")
        
        # Paste the images onto the collage
        if orientation == 'horizontal':
            collage.paste(img1, (0, 0))
            collage.paste(img2, (img1.width, 0))
        else:
            collage.paste(img1, (0, 0))
            collage.paste(img2, (0, img1.height))
        
        return collage
    
    def add_text_to_image(self, img, img_sizes, text, text_size, text_color, text_bg):
        self.font = ImageFont.truetype('fonts/kalpurush.ttf', text_size)
        text_image = self.__fit_text_in_white_background(text, img_sizes, text_bg, text_color)
        new_img = self.__collage_image(img, text_image)
        return new_img
    
    