import json
import os

class ObjectCounter:
    def __init__(self, config):
        self.dataset_path = config.dataset_path
        self.project_id = config.project_id
        self.user_map_dir = config.user_map_dir
        self.user_map = {}
        self.counter = {}
        self.image_count = {}

    def get_object_count(self):
        if not os.path.exists(self.dataset_path):
            print(f"No data found in {self.dataset_path}")
            return
        with open(self.dataset_path, 'r') as f:
            self.dataset = json.load(f)
        if not os.path.exists(self.user_map_dir):
            print(f"No data found in {self.user_map_dir}")
            return
        with open(self.user_map_dir, 'r') as f:
            users = json.load(f)
        for result in users['results']:
            self.user_map[result['user']['id']] = result['user']['email']
        with open(os.path.join(os.path.dirname(self.user_map_dir), 'users.json'), 'w') as f:
            json.dump(self.user_map, f)
        for data in self.dataset:
            for ann in data['annotations']:
                if not self.user_map[ann['completed_by']] in self.counter.keys():
                    self.image_count[self.user_map[ann['completed_by']]] = 1
                    self.counter[self.user_map[ann['completed_by']]] = len(ann['result'])
                else:
                    image_counts = self.image_count[self.user_map[ann['completed_by']]]
                    image_counts += 1
                    self.image_count[self.user_map[ann['completed_by']]] = image_counts
                    value = self.counter[self.user_map[ann['completed_by']]]
                    value += len(ann['result'])
                    self.counter[self.user_map[ann['completed_by']]] = value
        with open(f'data/counts/object_counts_{self.project_id}.json', 'w') as f:
            json.dump(self.counter, f)
        with open(f'data/counts/image_counts_{self.project_id}.json', 'w') as f:
            json.dump(self.image_count, f)
        return
    
