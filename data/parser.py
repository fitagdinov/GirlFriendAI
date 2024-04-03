import pandas as pd
import requests
import re
import os

from bs4 import BeautifulSoup
from tqdm import tqdm


class NudeGirlParser:

    base_url: str = "https://www.elitebabes.com/random-single/sort/gallery/label/1/nr/"
    img_dir_path: str = "./img_nudes/"
    data_path: str = "./data_nudes.csv"

    def load_nude_images(self,
                         start_id: int = 1,
                         end_id: int = 299999):
        if not os.path.exists(self.img_dir_path):
            os.makedirs(self.img_dir_path)
        data = pd.DataFrame(columns=['id', 'text', 'tags'])
        for album_id in tqdm(range(start_id, end_id), desc="Image loading"):
            album_num = str(album_id).zfill(6)
            url = self.base_url + album_num
            content = requests.get(url).content
            soup = BeautifulSoup(content, 'html.parser')
            tags = []
            text = ""
            for p_tag in soup.find_all('p', 'link-btn scroll'):
                for a_tag in p_tag.find_all('a'):
                    tag = re.search(r'href="(.*?)"', str(a_tag)).group(1)
                    if 'tag' in tag:
                        tags.append(a_tag.text)
            if 'Sex' in tags or 'Lesbian' in tags:
                continue
            for ul_tag in soup.find_all('ul', 'list-gallery static css'):
                for i, li_tag in enumerate(ul_tag.find_all('li')):
                    image_url = re.search(r'href="(.*?)"', str(li_tag)).group(1)
                    img_data = requests.get(image_url).content
                    text = ' '.join(re.search(r'/(.*?).jpg', image_url).group(1).split('-')[:-1])
                    text = text[text.rfind('/') + 1:]
                    image_num = str(i+1).zfill(2)
                    with open(self.img_dir_path + f'img_{album_num}_{image_num}.jpg', 'wb') as handler:
                        handler.write(img_data)
            id_data = {'id': [album_num], 'text': [text], 'tags': [';'.join(tags).replace(' ', '_')]}
            data = pd.concat([data, pd.DataFrame(id_data)], axis=0)
        data.to_csv(self.data_path, index=False)


if __name__ == "__main__":
    parser = NudeGirlParser()
    parser.load_nude_images()
