# Importation des modules
import discord
import datetime
import time
import os
import urllib.request

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands import MissingPermissions

# Recupérer la date
def voirdate ():
	global date
	# Récuperer la jour, le mois (en anglais) et l'année
	jour = datetime.datetime.today().strftime('%d')
	if jour[0]== "0" : jour = jour[1]
	moisen = datetime.datetime.today().strftime('%B')
	annee = datetime.datetime.today().strftime('%Y')

	# Liste avec le smois en français et en anglais
	moisentab = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	moisfrtab = ["janvier", "fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]

	# Transformer les mois en anglais vers le français
	for i in range(len(moisentab)): 
		if moisentab[i] == moisen : 
			mois = moisfrtab[i]

	# Retourner la bonne date
	date = jour + " " + mois + " " + annee

# Scrapper la date
def scrapping():
	global plat, accompagnement, pizza

	# Définition de l'URL
	urlpage = 'https://www.crous-normandie.fr/restaurant/ru-claude-bloch/'

	# Requêter le site
	page = urllib.request.urlopen(urlpage).read().decode("utf-8")

	# Parser la page 
	codesource = BeautifulSoup(page, 'html.parser')

	# Ne prendre que le text de la page
	codesource = codesource.get_text()

	# Transformer le code source en str
	codesource = str(codesource)

	# Séparer la date que l'on veux 
	debut = codesource.find(date)
	codesource = codesource[debut:]
	fin = codesource.find("Menu")

	codesource = codesource[0:fin]

	# Créer une liste contenant l'alphabet en majuscule
	alphabetmaj = []
	for i in range(26):
		alphabetmaj.append(chr(65+i))

	# Aller à la ligne dès qu'il y a une majuscule
	for i in range(len(alphabetmaj)):
		codesource = codesource.replace(alphabetmaj[i],"\n" + alphabetmaj[i])

	# Séparer les plats du reste
	debutplat = codesource.find("Plats")
	finplat = codesource.find("Accompagnement")
	plat = codesource[debutplat:finplat]

	# Séparer les accompagnements du reste
	debutaccompagnement = codesource.find("Accompagnements")
	finaccompagnement = codesource.find("Pizzas et snacking")
	accompagnement = codesource[debutaccompagnement:finaccompagnement]

	# Séparer les pizzas du reste
	debutpizza = codesource.find("Pizzas et snacking")
	finpizza = codesource.find("Desserts")
	pizza = codesource[debutpizza:finpizza]

	# Enlever les intitulés des différentes parties
	plat = plat[5:]
	accompagnement = accompagnement[15:]
	pizza = pizza[19:]

# Récupérer le Token dans le fichier config.env
load_dotenv(dotenv_path="config.env")

# Définir le préfixe du Bot
bot = commands.Bot(command_prefix=";")

@bot.event
async def on_ready():
	print("\nLe bot est connecté! \n")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=';menu'))
	print("Salut")

@bot.command(name="ping")
async def ping(ctx):
	print("Un utilisateur à utilisé la commande Ping")
	await ctx.message.delete()

	await ctx.send(f"Mon ping est de {round(bot.latency * 1000)} ms")

@bot.command(name="menu")
async def menu(ctx):
	print("Un utilisateur à utilisé la commande Menu")
	await ctx.message.delete()

	voirdate()
	scrapping()

	menu = plat + accompagnement + pizza

	# Vérifier si le menu est vide (sinon erreur)
	vide = 0
	for i in range (0,len(menu)):
		if menu[i] != "\n" : 
			vide = 1
			break
	if vide == 0 : await ctx.send(f"Il n'y a pas de menu aujourd'hui")
	else : 
		# Créer l'embed
		embed = discord.Embed(title="Le menu d'aujourd'hui est :", description=date, color=discord.Color.red())
		embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
		embed.add_field(name="Plat", value=plat, inline=False)
		embed.add_field(name="Accompagnement", value=accompagnement, inline=False)
		embed.add_field(name="Pizza", value=pizza, inline=False)
		embed.set_footer(text="Crée par Sourcier De Vérité#1962")
		await ctx.send(embed=embed)

@bot.command(name="sup")
@commands.has_permissions(manage_messages=True)
async def sup(ctx, nombre : int):
	await ctx.message.delete()
	print(f"Un utilisateur à utilisé la commande Supprimer pour {nombre} message(s)")

	await ctx.channel.purge(limit = nombre)
	await ctx.send(f"J'ai bien supprimé {nombre} messages", delete_after=5)

@bot.command(name="ban")
@commands.has_permissions(administrator=True)
async def ban(ctx, member : discord.Member, reason=None):
	await ctx.message.delete()
	print(f"Un utilisateur à utilisé le commande Ban pour l'utilisateur {member}")

	await member.ban(reason = reason)
	await ctx.send(f"Le membre {member} a bien été banni")

@sup.error
@ban.error
async def error(ctx, error):
	if isinstance(error, MissingPermissions):
		await ctx.send("Vous n'avez pas la permission de faire ça")

# Lancer le bot
bot.run(os.getenv("TOKEN"))
