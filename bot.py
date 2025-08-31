import discord
from discord.ext import commands
import sqlite3
from logic import db_map
import os
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} çalışıyor!')
    db_map.create_user_table()

@bot.command()
async def start(ctx):
    await ctx.send("Harita Botu aktif! Şehirleri keşfetmeye hazır!")

@bot.command()
async def help_me(ctx):
    help_text = """
    Bot Komutları:
    `!start` - Botu başlat
    `!show_city <şehir>` - Şehri haritada göster
    `!remember_city <şehir>` - Şehri kaydet
    `!show_my_cities` - Kaydettiğim şehirleri göster
    `!all_cities` - Tüm mevcut şehirleri listele
    """
    await ctx.send(help_text)

@bot.command()
async def show_city(ctx, *, city_name):
    try:
        image_path = f"maps/{ctx.author.id}_{city_name}.png"
        if db_map.create_graph(image_path, [city_name]):
            with open(image_path, 'rb') as f:
                await ctx.send(f"{city_name} haritada:", file=discord.File(f))
            os.remove(image_path)
        else:
            await ctx.send("Şehir bulunamadı! Mevcut şehirleri görmek için `!all_cities`")
    except Exception as e:
        await ctx.send(f"Hata: {str(e)}")

@bot.command()
async def remember_city(ctx, *, city_name):
    result = db_map.add_city(ctx.author.id, city_name)
    if result == 1:
        await ctx.send(f"{city_name} kaydedildi!")
    else:
        await ctx.send("Şehir bulunamadı! Mevcut şehirleri görmek için `!all_cities`")

@bot.command()
async def show_my_cities(ctx):
    try:
        user_cities = db_map.select_cities(ctx.author.id)
        if not user_cities:
            await ctx.send("Henüz hiç şehir kaydetmemişsin! `!remember_city <şehir>` ile kaydedebilirsin.")
            return
        image_path = f"maps/{ctx.author.id}_my_cities.png"
        if db_map.create_graph(image_path, user_cities):
            with open(image_path, 'rb') as f:
                cities_text = "\n".join([f"{city}" for city in user_cities])
                await ctx.send(f"{ctx.author.name}'in şehirleri:\n{cities_text}", file=discord.File(f))
            os.remove(image_path)
        else:
            await ctx.send("Harita oluşturulamadı!")
    except Exception as e:
        await ctx.send(f"Hata: {str(e)}")

@bot.command()
async def all_cities(ctx):
    cities = db_map.get_all_cities()
    if cities:
        cities_list = "\n".join([f"{city}" for city in cities])
        await ctx.send(f"Mevcut Şehirler:\n{cities_list}")
    else:
        await ctx.send("Hiç şehir bulunamadı!")

if __name__ == '__main__':
    db_map = db_map('database.db')
    bot.run(TOKEN)
