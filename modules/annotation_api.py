from modules.annotation_tools.label_studio_api import LabelStudioAPI

def get_annotator(config):
    if config.type == 'LabelStudio':
        api = LabelStudioAPI(
            api_url=config.api_url,
            token=config.token
        )
    return api