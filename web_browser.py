from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Importe a classe Options

class Browser:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")  # Nível de log SEVERE
        self.driver = webdriver.Chrome(options=chrome_options)
        self.download_folder = "downloads"  # Pasta para downloads
    
    def init_browser(self):
        return self.driver
