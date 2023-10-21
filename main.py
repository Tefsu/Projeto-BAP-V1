import sys
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QPushButton, QLabel, QDialog, QLineEdit, QInputDialog, QMessageBox
from scrapy import AnimesZoneScraper
from web_browser import Browser
from DownloadEp import EpisodeDownloader

class AnimeListApp(QMainWindow):
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle("Anime List")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.anime_list = QListView()
        self.model = QStandardItemModel(self.anime_list)
        self.anime_list.setModel(self.model)
        self.layout.addWidget(self.anime_list)

        self.add_button = QPushButton("Adicionar Anime")
        self.add_button.clicked.connect(self.add_anime)
        self.layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Excluir Anime Selecionado")
        self.delete_button.clicked.connect(self.delete_anime)
        self.layout.addWidget(self.delete_button)

        self.search_button = QPushButton("Pesquisar Episódios")
        self.search_button.clicked.connect(self.search_episodes)
        self.layout.addWidget(self.search_button)

        self.central_widget.setLayout(self.layout)

        self.db_connection = sqlite3.connect("anime_database.db")
        self.create_table()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS animes (id INTEGER PRIMARY KEY, name TEXT)")
        self.db_connection.commit()

    def add_anime(self):
        name, ok = QInputDialog.getText(self, "Adicionar Anime", "Nome do Anime:")
        if ok:
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO animes (name) VALUES (?)", (name,))
            self.db_connection.commit()
            self.load_anime_list()

    def delete_anime(self):
        selected_index = self.anime_list.selectionModel().currentIndex()
        if selected_index.isValid():
            anime_name = selected_index.data()
            confirm = QMessageBox.question(self, "Excluir Anime", f"Tem certeza que deseja excluir o anime '{anime_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM animes WHERE name = ?", (anime_name,))
                self.db_connection.commit()
                self.load_anime_list()

    def load_anime_list(self):
        self.model.clear()
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name FROM animes")
        anime_list = cursor.fetchall()
        for anime in anime_list:
            item = QStandardItem(anime[0])
            item.setEditable(False)
            self.model.appendRow(item)

    def search_episodes(self):
        self.driver = Browser()
        self.driver = self.driver.init_browser()
        self.scraper = AnimesZoneScraper()
        selected_index = self.anime_list.selectionModel().currentIndex()
        
        if selected_index.isValid():

            self.scraper.init_scrapy(browser=self.driver)
            anime_name = selected_index.data()
            num_episodes, episode_numbers = self.scraper.search_anime_episodes(anime_name)
            self.scraper.close()
            dialog = EpisodeSearchDialog(anime_name=anime_name, num_episodes=num_episodes, episodes_numbers=episode_numbers)
            dialog.exec()


class EpisodeSearchDialog(QDialog):
    def __init__(self, anime_name, num_episodes, episodes_numbers):
        super().__init__()
        self.setWindowTitle("Pesquisar Episódios")
        self.driver = Browser()
        self.driver = self.driver.init_browser()
        self.downloadEp = EpisodeDownloader()
        self.anime_name = anime_name

        episodes = episodes_numbers
        self.not_duplicate_episodes = []
        for item in episodes:
            item = item.replace("/", "")
            if item not in self.not_duplicate_episodes:
                self.not_duplicate_episodes.append(item)
        # print(self.not_duplicate_episodes)

        self.layout = QVBoxLayout()

        self.label = QLabel(f"Pesquisando episódios para {anime_name}")
        self.layout.addWidget(self.label)

        self.result_label = QLabel(f"Quantidade de episódios encontrados: {len(self.not_duplicate_episodes)}")
        self.layout.addWidget(self.result_label)

        if len(self.not_duplicate_episodes) > 0:
            self.episodios = QLabel(f"Número dos episodios encontrados: {self.not_duplicate_episodes}")
            self.layout.addWidget(self.episodios)
            
            self.episodio = self.not_duplicate_episodes[0]

            self.download_button = QPushButton(f"Baixar Episódio: {self.episodio}")
            self.download_button.clicked.connect(self.download_episodio)
            self.layout.addWidget(self.download_button)

        self.setLayout(self.layout)

    def download_episodio(self):
        confirm = QMessageBox.question(self, "Baixar Anime", f"Tem certeza que deseja baixar o episodio {self.episodio} do anime '{self.anime_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.downloadEp.init_download(browser=self.driver)
            self.downloadEp.download_episode(anime_name=self.anime_name, episode_number=self.episodio)
            
        self.downloadEp.close()
        QMessageBox.information(self, "Download Concluído", f"Download do episódio {self.episodio} de '{self.anime_name}' foi concluído com sucesso.")
        self.close()
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimeListApp()
    window.load_anime_list()
    window.show()
    sys.exit(app.exec())
    
