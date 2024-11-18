import json
import urllib
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class EasyOCRConverter:
    def __init__(self):
        self.dataset = {}
        self.converted_dataset = []
        self.image_count = {}
        self.ocr_dataset = []

    def transform_dataset(self):
        with open('data/dataset.json', 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        self.__transfer_images()
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(f"dataset/main_images/{file_name}"):
                continue
            if not file_name in self.image_count:
                self.image_count[file_name] = 0
            else:
                count = self.image_count[file_name]
                count += 1
                self.image_count[file_name] = count
            img = Image.open(f"dataset/main_images/{file_name}")
            bboxes = [data['x'], data['y'], data['width'], data['height']]
            text = data['text'][0]
            try:
                new_file_name = f"{file_name.split('.')[0]}_{self.image_count[file_name]}.{file_name.split('.')[-1]}"
                self.__crop_segments(img, bboxes, new_file_name)
                self.ocr_dataset.append(
                    {
                        'filename': new_file_name,
                        'words': text
                    }
                )
            except Exception as e:
                print(f"Failed to crop and convert csv file for data:\n{data}")
        df = pd.DataFrame(self.ocr_dataset)
        df.to_csv('dataset/labels/labels.csv', index=False)
        return
    
    def draw_labels(self, add_text = True, text_size = 16, text_color = 'black', text_bg = 'white'):
        self.image_count = {}
        with open('data/converted_dataset.json', 'r') as f:
            self.converted_dataset = json.load(f)
        for data in self.converted_dataset:
            file_name = data['file_name']
            if not os.path.exists(f"dataset/main_images/{file_name}"):
                continue
            img = Image.open(f"dataset/main_images/{file_name}")
            img_w, img_h = img.size
            img_sizes = [img_w, img_h]
            bboxes = [data['x'], data['y'], data['width'], data['height']]
            text = f"Task id: {data['task_id']}\n{data['text'][0]}"
            new_img = self.__draw_bounding_box(img, bboxes)
            if add_text:
                font = ImageFont.truetype('fonts/kalpurush.ttf', text_size)
                text_image = self.__fit_text_in_white_background(text, img_sizes, font, text_bg, text_color)
                new_img = self.__collage_image(new_img, text_image)
            if not file_name in self.image_count:
                self.image_count[file_name] = 0
            else:
                value = self.image_count[file_name]
                value += 1
                self.image_count[file_name] = value
            new_img.save(f'bbox_images/{file_name.split('.')[0]}_{self.image_count[file_name]}.jpg')
        return
    
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
        
    def __fit_text_in_white_background(self, text, img_sizes, font, background, text_color):
        img = Image.new("RGB", (img_sizes[0], img_sizes[1]), background)
        draw = ImageDraw.Draw(img)
        middle_points = (5, img_sizes[1]/2)
        draw.text(middle_points, str(text), font=font, fill=text_color)
        return img

    def __draw_bounding_box(self, image, bboxes, bbox_width=2, bbox_color = 'red'):
        draw = ImageDraw.Draw(image)
        x_min, y_min, x_max, y_max = self.__xywh_to_xyxy(bboxes, image.size)
        draw.rectangle([x_min, y_min, x_max, y_max], outline=bbox_color, width=bbox_width)
        return image

    def __crop_segments(self, image, bboxes, name):
        x1, y1, x2, y2 = self.__xywh_to_xyxy(bboxes, image.size)
        crop_img = image.crop((x1, y1, x2, y2))
        path = f'dataset/images/{name}'
        crop_img.save(path)
        return

    def __xywh_to_xyxy(self, bbox, shape):
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

    def __transfer_images(self):
        self.__converter()
        if not os.path.exists('dataset/main_images'):
            os.mkdir('dataset/main_images')
        for data in self.converted_dataset:
            if not os.path.exists(f"main_files/images/{data['file_name']}"):
                downloaded = self.__image_downloader(data['image_link'])
                if not downloaded:
                    continue
            if not os.path.exists(f"dataset/main_images/{data['file_name']}"):
                subprocess.run(['cp', f"main_files/images/{data['file_name']}", "dataset/main_images"])
        return

    def __image_downloader(self, url):
        if not url[:8] == 'https://':
            url = 'https://'+url
        try:
            file_name = url.split('/')[-1]
            urllib.request.urlretrieve(url, f"dataset/images/{file_name}")
            return True
        
        except Exception as e:
            print(f'{url} is not downloadable.')
            return False

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
        with open('data/converted_dataset.json', 'w') as f:
            json.dump(self.converted_dataset, f)
        return