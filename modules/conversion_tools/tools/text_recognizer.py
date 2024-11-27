import os
import pandas as pd
from modules.conversion_tools.converter import Converter

class TextRecognizerConverter(Converter):
    def __init__(self, parent_dir, main_file):
        super().__init__(parent_dir, main_file)
        self.dir_check()
        self.loader()
        self.image_count = {}
        self.ocr_dataset = []

    def transform_dataset(self):
        self.convert_transfer()
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
            img_path = os.path.join(self.main_file_dir, file_name)
            img, img_sizes = self.image_loader(img_path)
            bboxes = self.xywh_to_xyxy([data['x'], data['y'], data['width'], data['height']], img_sizes)
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
            img, img_sizes = self.image_loader(img_path)
            bboxes = self.xywh_to_xyxy([data['x'], data['y'], data['width'], data['height']], img_sizes)
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

    
        
    

    

    

    

    

    

    