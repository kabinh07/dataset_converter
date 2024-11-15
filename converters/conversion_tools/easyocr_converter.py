import json
import urllib
import os
import subprocess
from PIL import Image
import pandas as pd

class EasyOCRConverter:
    def __init__(self):
        with open('data/dataset.json', 'r', encoding='utf-8') as f:
            self.dataset = json.load(f)
        self.converted_dataset = []
        self.image_count = {}
        self.ocr_dataset = []

    def create_dataset(self):
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
            text = data['text']
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
                self.__image_downloader(data['image_link'])
            else:
                subprocess.run(['cp', f"main_files/images/{data['file_name']}", "dataset/main_images"])
        return

    def __image_downloader(self, url):
        if not url[:8] == 'https://':
            url = 'https://'+url
        try:
            file_name = url.split('/')[-1]
            if not os.path.exists(f"dataset/images/{file_name}"):
                urllib.request.urlretrieve(url, f"dataset/images/{file_name}")
        except Exception as e:
            print('Link is not downloadable.')
        return

    def __converter(self):
        for ann in self.dataset:
            image_link = ann['data']['image']
            file = image_link.split('/')[-1]
            for result in ann['annotations'][0]['result']:
                if result['type'] == 'textarea':
                    row = result['value']
                    row['file_name'] = file
                    row['image_link'] = image_link
                    self.converted_dataset.append(row)
        return