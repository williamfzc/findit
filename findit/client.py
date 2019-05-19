import requests
import requests.exceptions
import numpy as np

from findit import toolbox


class FindItClient(object):
    def __init__(self, host: str = None, port: int = None):
        host = host or 'http://127.0.0.1'
        port = port or 9410
        self.url = '{}:{}'.format(host, port)

    def heartbeat(self) -> bool:
        target_url = '{}/'.format(self.url)
        try:
            resp = requests.get(target_url)
            return resp.ok
        except requests.exceptions.ConnectionError:
            return False

    def analyse_with_path(self, target_pic_path: str, template_pic_name: str) -> dict:
        with open(target_pic_path, 'rb+') as f:
            pic_data = f.read()
        resp = requests.post(
            '{}/analyse'.format(self.url),
            data={'template_name': template_pic_name},
            files={'file': pic_data}
        )
        return resp.json()

    def analyse_with_object(self, target_pic_object: np.ndarray, template_pic_name: str) -> dict:
        with toolbox.cv2file(target_pic_object) as temp_path:
            analyse_result = self.analyse_with_path(temp_path, template_pic_name)
        return analyse_result


if __name__ == '__main__':
    cli = FindItClient()
    assert cli.heartbeat()
    result = cli.analyse_with_path('../sample/pics/screen.png', 'wechat_logo.png')
    print(result)
