from converters.conversion_tools.easyocr_converter import EasyOCRConverter

def get_converter(config):
    if config['type'] == 'EasyOCR':
        obj = EasyOCRConverter()
    return obj