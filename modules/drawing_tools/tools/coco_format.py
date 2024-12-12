from modules.drawing_tools.draw_image import DrawImage
from PIL import Image, ImageDraw
import json
import os
import supervision as sv
import numpy as np

class COCOFormat(DrawImage):
    def __init__(self, config, parent_dir):
        super().__init__(config, parent_dir)
        self.box_annotator = sv.BoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        self.image_count = {}

    def draw_labels(self):
        images_path = os.path.join(self.dataset_path, 'images')
        labels_path = os.path.join(self.dataset_path, 'labels')
        map_path = os.path.join(self.dataset_path, 'labels.json')
        drawing_path = os.path.join(os.path.dirname(self.dataset_path), 'bbox_images')
        if not os.path.exists(drawing_path):
            os.makedirs(drawing_path)
        images = os.listdir(images_path)
        labels = [data.split('.')[0]+'.txt' for data in images]
        label_map = {}
        if not len(images):
            print(f"No images found in {images_path}")
            return
        if not len(labels):
            print(f"No labels found in {labels_path}")
            return
        if not os.path.exists(map_path):
            print(f"No label map found in {map_path}")
        else:
            with open(map_path, 'r') as f:
                label_map = json.load(f)
        for image, label in zip(images, labels):
            image_path = os.path.join(images_path, image)
            label_path = os.path.join(labels_path, label)
            with open(label_path, 'r') as f:
                label_list = f.read().split('\n')
            label_list = [list(map(float, l.split(' '))) for l in label_list if not l == '']
            classes = np.array([int(l[0]) for l in label_list])
            boxes = [l[1:] for l in label_list]
            img = Image.open(image_path)
            img_shape = img.size
            normalized_boxes = np.array([self.bbox_converter(box, img_shape) for box in boxes])
            for box, cls in zip(normalized_boxes, classes):
                detections = sv.Detections(xyxy=box.reshape(1, -1), class_id=np.array([cls]))
                img = self.box_annotator.annotate(
                    scene=img.copy(),
                    detections=detections
                )
                if label_map:
                    img = self.label_annotator.annotate(
                        scene=img,
                        detections=detections,
                        labels=[label_map[str(cls.item())]]
                    )
            img.save(os.path.join(drawing_path, image))
        return

    def bbox_converter(self, bbox, shape):
        x_center_norm, y_center_norm, width_norm, height_norm = bbox

        x_center = x_center_norm * shape[0]
        y_center = y_center_norm * shape[1]
        width = width_norm * shape[0]
        height = height_norm * shape[1]
        
        # Calculate top-left and bottom-right coordinates of the bounding box
        x_min = int(x_center - width / 2)
        y_min = int(y_center - height / 2)
        x_max = int(x_center + width / 2)
        y_max = int(y_center + height / 2)

        return np.array([x_min, y_min, x_max, y_max])
    
    def draw_bounding_box(self, drawable_image, bboxes):
        x_min, y_min, x_max, y_max = bboxes
        drawable_image.rectangle([x_min, y_min, x_max, y_max], outline=self.bounding_box_color, width=self.bounding_box_width)
        return drawable_image