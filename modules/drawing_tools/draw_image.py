import os
from PIL import Image, ImageDraw, ImageFont

class DrawImage:
    def __init__(self, config, parent_dir):
        self.parent_dir = parent_dir
        self.bounding_box_width = config.bounding_box_width
        self.bounding_box_color = config.bounding_box_color
        self.add_text = config.add_text
        self.font_path = config.font_path
        self.text_size = config.text_size
        self.text_color = config.text_color
        self.text_background = config.text_background_color
        self.__load_files()

    def __load_files(self):
        self.dataset_path = os.path.join(self.parent_dir, 'dataset')
        if not os.path.exists(self.dataset_path):
            print(f"No data found in {self.dataset_path}")
        return

    def draw_labels(self):
        pass

    def draw_bounding_box(self, image, bboxes):
        pass

    def bbox_converter(self):
        pass

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
    
    def add_text_to_image(self, img, img_sizes, text):
        self.font = ImageFont.truetype(self.font_path, self.text_size)
        text_image = self.__fit_text_in_white_background(text, img_sizes, self.text_background, self.text_color)
        new_img = self.__collage_image(img, text_image)
        return new_img