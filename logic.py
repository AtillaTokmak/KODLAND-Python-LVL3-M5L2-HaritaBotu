import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os

class DB_Map():
    def __init__(self, database):
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id INTEGER,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                # Aynı şehri tekrar eklemeyi önle
                cursor.execute('SELECT * FROM users_cities WHERE user_id=? AND city_id=?', 
                             (user_id, city_id))
                if not cursor.fetchone():
                    conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                    conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT c.city 
                            FROM users_cities uc  
                            JOIN cities c ON uc.city_id = c.id
                            WHERE uc.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, image_path, city_names):
        """
        Verilen şehirleri harita üzerinde gösteren grafik oluşturur
        """
        try:
            # Şehir koordinatlarını topla
            coordinates = []
            valid_cities = []
            
            for city_name in city_names:
                coords = self.get_coordinates(city_name)
                if coords:
                    coordinates.append(coords)
                    valid_cities.append(city_name)
            
            if not coordinates:
                return False
            
            # Koordinatları ayır
            lats = [coord[0] for coord in coordinates]
            lons = [coord[1] for coord in coordinates]
            
            # Grafik oluştur
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
            
            # Dünya haritası (tüm şehirleri göstermek için)
            ax.set_global()
            
            # Harita özellikleri
            ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.8)
            ax.add_feature(cfeature.LAND, color='lightgreen', alpha=0.5)
            ax.add_feature(cfeature.OCEAN, color='lightblue', alpha=0.5)
            
            # Şehirleri işaretle
            for i, (lat, lon) in enumerate(zip(lats, lons)):
                ax.plot(lon, lat, 'ro', markersize=10, transform=ccrs.PlateCarree())
                ax.text(lon + 1, lat + 1, valid_cities[i], transform=ccrs.PlateCarree(),
                       fontsize=9, weight='bold', color='darkred',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
            
            # Başlık
            if len(valid_cities) == 1:
                title = f"Şehir: {valid_cities[0]}"
            else:
                title = f"{len(valid_cities)} Şehir"
            plt.title(title, fontsize=16, weight='bold', pad=20)
            
            # Grid çizgileri
            ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
            
            # Klasörü kontrol et ve oluştur
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Dosyayı kaydet
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"Harita oluşturma hatası: {e}")
            return False

    def get_all_cities(self):
        """Tüm şehirleri getir"""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM cities")
            return [row[0] for row in cursor.fetchall()]

if __name__ == "__main__":
    m = DB_Map("database.db")  # Veri tabanıyla etkileşime geçecek bir nesne oluşturma
    m.create_user_table() 
