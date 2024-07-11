import time
import yaml

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from config import ParserConfig

with open('config.yaml') as file:
    params = yaml.load(file, yaml.SafeLoader)

cfg = ParserConfig(**params['instant_id'])


def parse_generated_photo(face_path: str | Path,
                          pose_path: str | Path,
                          promt: str,
                          style: str = "(No style)"):
    if isinstance(face_path, str):
        face_path = Path(face_path)
        assert face_path.exists()
    if isinstance(pose_path, str):
        pose_path = Path(pose_path)
        assert pose_path.exists()

    options = webdriver.ChromeOptions()

    for arg in cfg.webdriver_args:
        options.add_argument(arg)

    with webdriver.Chrome(options=options) as browser:
        browser.get(cfg.url)

        face_box = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-6")))
        face_box.find_element(By.TAG_NAME, "input").send_keys(str(face_path.resolve()))

        pose_box = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-7")))
        pose_box.find_element(By.TAG_NAME, "input").send_keys(str(pose_path.resolve()))

        promt_box = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-8")))
        promt_box.find_element(By.TAG_NAME, "textarea").send_keys(promt)

        style_box = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-11")))
        style_box.click()
        style_options = style_box.find_elements(By.TAG_NAME, "li")
        selected_option = [op for op in style_options if op.text.strip() == style]
        selected_option = selected_option[0] if len(selected_option) > 0 else style_options[0]
        selected_option.click()

        time.sleep(1)

        submit_button = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-9")))
        submit_button.click()

        result_box = WebDriverWait(browser, 20).until(ec.presence_of_element_located((By.ID, "component-32")))

        result = WebDriverWait(browser, 100).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "#component-32 > div.icon-buttons.svelte-1l6wqyv > a")))
        result_url = result.get_attribute("href")
        browser.switch_to.default_content()

    return result_url


if __name__ == "__main__":
    print(parse_generated_photo("../examples/face/eva_elfie.jpg",
                                "../examples/pose/raised_hands.jpg",
                                "naked girl near the car"))
