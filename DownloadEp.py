import os
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options  # Importe a classe Options
import time

class EpisodeDownloader:
    def __init__(self):
        self.download_folder = "downloads"  # Pasta para downloads

        # Redirecione a saída padrão (stdout) para um arquivo
        self.log_file = open("log.txt", "w")
        sys.stderr = self.log_file
    
    def init_download(self, browser):
        '''Recebe instancia do navegador'''
        self.driver = browser
        
    def download_episode(self, anime_name, episode_number):
        '''Faz o download do episodio desejado'''
        # Formate a URL do episódio
        anime_name = anime_name.lower().replace(" ", "-")
        if anime_name == 'spy-x-family-2':
            formatted_url = f"https://animeszone.net/video/spy-x-family-2-episodio-{episode_number}-versao/"
        else:
            formatted_url = f"https://animeszone.net/video/{anime_name}-episodio-{episode_number}/"

        self.driver.get(formatted_url)

        # Aguarde alguns segundos para que a página seja carregada (ajuste conforme necessário)
        time.sleep(5)

        # Encontre o iframe usando seu XPath
        iframe = self.driver.find_element(By.XPATH, '//*[@id="dooplay_player_response"]/div/iframe')

        # Alterne para o contexto do iframe
        self.driver.switch_to.frame(iframe)

        # Encontre o elemento de vídeo dentro do iframe usando o XPath fornecido
        video = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[3]/video')

        # Obtenha o atributo "src" do vídeo
        video_src = video.get_attribute('src')

        if video_src:
            # Crie a estrutura de pastas
            download_path = os.path.join(self.download_folder, anime_name)
            os.makedirs(download_path, exist_ok=True)

            # Abra o link do vídeo em uma nova guia do navegador
            self.driver.execute_script(f'window.open("{video_src}");')

            # Mude o foco para a nova guia
            self.driver.switch_to.window(self.driver.window_handles[1])

            # Pausar o vídeo
            self.driver.execute_script("document.querySelector('video').pause();")

            # Aguarde alguns segundos para garantir que a nova guia seja carregada adequadamente
            time.sleep(5)

            # Baixe o vídeo da nova guia usando a biblioteca 'requests'
            print(f"Baixando episódio {episode_number} de {anime_name}...")

            response = requests.get(video_src, stream=True)
            if response.status_code == 200:
                episode_filename = f"{anime_name}-episode-{episode_number}.mp4"
                episode_path = os.path.join(download_path, episode_filename)

                with open(episode_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                print(f"Episódio {episode_number} de {anime_name} baixado com sucesso como '{episode_filename}'")
            else:
                print(f"Erro ao baixar o episódio {episode_number} de {anime_name}. Código de status: {response.status_code}")

            # Feche a nova guia
            self.driver.close()
        else:
            print(f"URL do episódio {episode_number} de {anime_name} não encontrado no elemento de vídeo dentro do iframe")

    def close(self):
        self.driver.quit()
        self.log_file.close()
        sys.stderr = sys.__stderr__


# Exemplo de uso:
# if __name__ == "__main__":
#     downloader = EpisodeDownloader()
#     anime_name = "undead-unluck"  # Substitua pelo nome do anime desejado (em letras minúsculas e com hífens)
#     episode_number = 3  # Substitua pelo número do episódio desejado.
#     downloader.download_episode(anime_name, episode_number)
#     downloader.close()

