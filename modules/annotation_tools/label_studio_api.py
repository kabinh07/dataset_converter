import requests
import json
import os

class LabelStudioAPI: 
    def __init__(
        self, 
        api_url, 
        token
    ): 
        self.url = api_url
        self.headers = {'Authorization': f'Token {token}'}
        self.json_headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}

    def check_projects(self): 
        response = requests.get(self.url+'/api/projects/', headers=self.headers)
        if response.status_code == 200:
            print(f"Successfully connected.")
        else:
            print(f"Failed to connect. Status Code: {response.status_code}")
            return
        projects = response.json()
        print(f"projects:")
        for project in projects['results']:
            print(f"ID: {project['id']} | Name: {project['title']}")
        return
    
    def get_json_dataset(
            self, 
            project_id,
            parent_dir,
            create_snapshot_body={"task_filter_options": {"annotated": "only"}}
            ):
        self.parent_dir = parent_dir
        dataset_path = os.path.join(os.path.dirname(self.parent_dir), 'downloads')
        response = self.__list_snapshots(project_id)
        if response.status_code == 200 and len(response.json()) != 0:
            print('Snapshot list already exist')
            self.__remove_all_snapshot_lists(project_id)
        response = self.__create_snapshot(project_id,create_snapshot_body)
        if not response.status_code == 201:
            print(f'Issue raised creating snapshot: \n{response.text}')
        self.__check_status(project_id)
        response = self.__download(project_id)
        if response.status_code == 200:
            with open(os.path.join(dataset_path, 'dataset.json'), 'w', encoding='utf-8') as f:
                json.dump(response.json(), f)
            print(f'Successfully saved json dataset from label studio in {os.path.join(dataset_path, 'dataset.json')}')
        else:
            print('Downloading issue')
        response = self.__delete_snapshot(project_id)
        return
    
    def __remove_all_snapshot_lists(self, project_id):
        while True:
            self.__list_snapshots(project_id)
            response = self.__delete_snapshot(project_id)
            if response.status_code != 204:
                print('Deleting snapshot failed')
                break 
            response = self.__list_snapshots(project_id)
            if len(response.json()) == 0:
                break   
        print('Successfully deleted all snapshots') 
        return
    
    def __check_status(self, project_id):
        while True:    
            response = self.__list_snapshots(project_id).json()
            if response[0]['status'] == 'completed':
                break
            print('Processing snapshot...')
        return

    def __list_snapshots(self, project_id): 
        response = requests.get(self.url+f'/api/projects/{project_id}/exports/', headers=self.headers)
        if len(response.json()):
            self.export_pk = response.json()[0]["id"]
        return response

    def __delete_snapshot(self, project_id): 
        response = requests.get(self.url+f'/api/projects/{project_id}/exports/', headers=self.headers)
        if not len(response.json()):
            print('No snapshot list found')
            return
        response = requests.delete(self.url+f'/api/projects/{project_id}/exports/{self.export_pk}', headers=self.headers)
        return response

    def __create_snapshot(self, project_id, create_snapshot_body): 
        response = requests.post(
            self.url+f'/api/projects/{project_id}/exports/', 
            json= create_snapshot_body,
            headers=self.json_headers
        )
        return response
        
    def __convert_yolo(self, project_id): 
        body = {'export_type': 'YOLO'}
        response = requests.post(
                self.url+f'/api/projects/{project_id}/exports/{self.export_pk}/convert', 
                json = self.conversion_body,
                headers=self.json_headers)
        print(f"Conversion details:\n{response.status_code}")
        return response

    def __download(self, project_id, conversion_body = None):
        response = requests.get(
            self.url+f'/api/projects/{project_id}/exports/{self.export_pk}/download',
            headers=self.headers,
            params=conversion_body, 
        )
        return response