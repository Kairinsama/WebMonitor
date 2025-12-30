import ast
import warnings
import time
from collections import OrderedDict
import os

from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from task.utils.selector.selector import SelectorABC as FatherSelector

warnings.filterwarnings("ignore")

USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'


class ChromeSelector(FatherSelector):
    def __init__(self, debug=False):
        self.debug = debug

    def get_html(self, url, headers, task_id=None):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Default UA
        ua_set = False
        
        extra_headers = {}
        if headers:
            header_dict = ast.literal_eval(headers)
            if type(header_dict) != dict:
                raise Exception('必须是字典格式')

            for key, value in header_dict.items():
                if key.lower() == 'user-agent':
                    options.add_argument(f'user-agent={value}')
                    ua_set = True
                else:
                    extra_headers[key] = value
        
        if not ua_set:
            options.add_argument(f'user-agent={USERAGENT}')

        driver = webdriver.Chrome(options=options)
        
        if extra_headers:
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': extra_headers})

        try:
            driver.get(url)
            time.sleep(2)
            
            # Screenshot logic
            if task_id:
                save_dir = os.path.join(settings.BASE_DIR, 'db', 'screenshot')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'{task_id}.png')
                if os.path.exists(save_path):
                    os.remove(save_path)
                driver.save_screenshot(save_path)
            
            if self.debug:
                basepath = os.path.dirname(os.path.dirname(__file__))
                save_path = os.path.join(basepath, '..', 'static', 'error')
                os.makedirs(save_path, exist_ok=True)
                driver.save_screenshot(os.path.join(save_path, 'screenshot.png'))
            
            html = driver.page_source
        finally:
            driver.quit()
        return html

    def get_by_xpath(self, url, selector_dict, headers=None, task_id=None):
        html = self.get_html(url, headers, task_id)

        result = OrderedDict()
        for key, xpath_ext in selector_dict.items():
            result[key] = self.xpath_parse(html, xpath_ext)

        return result

    def get_by_css(self, url, selector_dict, headers=None, task_id=None):
        html = self.get_html(url, headers, task_id)

        result = OrderedDict()
        for key, css_ext in selector_dict.items():
            result[key] = self.css_parse(html, css_ext)

        return result
    
    def get_by_json(self, url, selector_dict, headers=None, task_id=None):
        html = self.get_html(url, headers, task_id)

        result = OrderedDict()
        for key, json_ext in selector_dict.items():
            result[key] = self.json_parse(html, json_ext)

        return result
