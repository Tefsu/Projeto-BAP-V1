from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class AnimesZoneScraper:
    def init_scrapy(self, browser):
        '''Recebe instancia do navegador'''
        self.driver = browser

    def search_anime_episodes(self, anime_name):
        '''Procura por novos epsodios do anime desejado na pagina de lançamentos do site'''
        self.driver.get('https://animeszone.net/')
        anime_name = anime_name.lower().replace(" ", "-")
        lancamentos = '/html/body/div[1]/div[2]/div/div/main/ul[3]/div'
        # Obtenha o HTML da página
        

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, lancamentos)))

        # Obtenha o HTML da div desejada
        lancamentos_div = self.driver.find_element(By.XPATH, lancamentos)
        lancamentos_html = lancamentos_div.get_attribute("innerHTML")
        # Use o BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(lancamentos_html, 'html.parser')

        # Encontre todos os links que correspondem ao nome do anime no formato desejado
        anime_links = soup.find_all('a', href=True)

        # Extrair o número do episódio
        episodes = []
        for link in anime_links:
            href = link['href']
            if anime_name in href:
                if ('temporada') not in href:
                    if anime_name == 'spy-x-family-2':
                        episode_number = href.split('-')[-2]
                    else:
                        episode_number = href.split('-')[-1]
                    
                    episodes.append(episode_number)
        return len(episodes), episodes

    def close(self):
        self.driver.quit()

# Exemplo de uso:
# if __name__ == "__main__":
#     scraper = AnimesZoneScraper()
#     anime_name = "Undead Unluck"  # Substitua pelo nome do anime desejado.
#     anime_name = anime_name.lower().replace(" ", "-")  # Converter para minúsculas e substituir espaços por hífens
#     num_episodes, episode_numbers = scraper.search_anime_episodes(anime_name)
#     scraper.close()

#     if num_episodes > 0:
#         print(f"{num_episodes} episódio(s) encontrado(s):")
#         for episode_number in episode_numbers:
#             print(f"Episódio {episode_number}")
#     else:
#         print(f"Nenhum episódio encontrado para o anime '{anime_name}' na página inicial.")
