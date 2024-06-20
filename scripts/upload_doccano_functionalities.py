import requests

def login(doccano_url, username, password):
    login_url = f"{doccano_url}/v1/auth/login/"
    login_data = {"username": username, "password": password}
    response = requests.post(login_url, data=login_data)
    response.raise_for_status()
    return response


def create_project(doccano_url, payload, headers):
    project_url = f"{doccano_url}/v1/projects"
    response = requests.post(project_url, headers=headers, data=payload)
    response.raise_for_status()
    project_id = response.json().get("id")
    return project_id


def process_dataset(doccano_url, payload, headers, file_path, project_id):
    process_url = f"{doccano_url}/v1/fp/process/"
    files = [("filepond", ("file", open(file_path, "rb"), "application/octet-stream"))]
    headers["referer"] = f"{doccano_url}/v1/projects/{project_id}/dataset/import"
    response = requests.post(process_url, headers=headers, data=payload, files=files)
    response.raise_for_status()
    process_id = response.text
    return process_id


def upload_data(doccano_url, payload, headers, project_id):
    upload_url = f"{doccano_url}/v1/projects/{project_id}/upload"
    headers["referer"] = f"{doccano_url}/v1/projects/{project_id}/dataset/import"
    response = requests.post(upload_url, headers=headers, data=payload)
    response.raise_for_status()
    return response.text