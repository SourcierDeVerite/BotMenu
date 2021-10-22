# https://bit.ly/2YM69Ia
# Importation des modules
import discord
import datetime
import time
import os
import urllib.request

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option,create_choice
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from dotenv import load_dotenv
from bs4 import BeautifulSoup

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

	plat = plat[5:]
	accompagnement = accompagnement[15:]
	pizza = pizza[19:]

# Creer un embed simple
def embedsimple(message):
	embed = discord.Embed(title=message, color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	embed.set_footer(text="Crée par Sourcier De Vérité#1962") 

	return embed

# Creer un embed pour le menu
def embedmenu(plat,accompagnement,pizza,date):
	embed = discord.Embed(title="Le menu d'aujourd'hui est :", description=date,color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	embed.add_field(name="Plat", value=plat, inline=False)
	embed.add_field(name="Accompagnement", value=accompagnement, inline=False)
	embed.add_field(name="Pizza", value=pizza, inline=False)
	embed.set_footer(text="Crée par Sourcier De Vérité#1962")
	return embed

# Creer un embed pour la commande help
def embedhelp():
	embed = discord.Embed(title="Voici les commandes disponibles :",color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	embed.add_field(name="Ping", value="Permet d'obtenir le ping du bot", inline=False)
	embed.add_field(name="Menu", value="Permet d'envoyer le menu d'aujourd'hui", inline=False)
	embed.add_field(name="Sup x", value="Permet de supprimer x messages (Reservé au Admin)", inline=False)
	embed.add_field(name="Ban x", value="Permet de bannir un membre (Reservé au Admin)", inline=False)
	embed.add_field(name="Say x", value="Permet de faire dire au bot un message", inline=False)
	embed.set_footer(text="Crée par Sourcier De Vérité#1962")
	
	return embed
	
# Récupérer le Token dans le fichier config.env
load_dotenv(dotenv_path="config.env")

# Initialiser le bot
bot = commands.Bot(command_prefix=";", help_command=None)
slash = SlashCommand(bot, sync_commands=True)
guild_ids=[715926570795008010,872202739046830080,763456598697705472,887273660254138419]
#guild_ids=[715926570795008010]

@bot.event
async def on_ready():
	print("\nLe bot est connecté ! \n")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='/help'))

@slash.slash(name="Ping", description="Envoie le ping du bot", guild_ids=guild_ids)
async def ping(ctx):
	print("Un utilisateur à utilisé la commande Ping")

	message = "Mon ping est de " + str(round(bot.latency * 1000)) + "ms"
	embed = embedsimple(message)

	await ctx.reply(embed=embed)

@slash.slash(name="Menu", description="Envoie le menu du RU", guild_ids=guild_ids)
async def menu(ctx):
	print("Un utilisateur à utilisé la commande Menu")

	voirdate()
	scrapping()
	menu = plat + " " + accompagnement + " " + pizza

	# Vérifier si le menu est vide
	if menu.isspace() : 
		message = "Désolé, mais le Menu n'est pas affiché sur le site"
		await ctx.send(embed=embedsimple(message))
	else :
		await ctx.send(embed=embedmenu(plat, accompagnement, pizza, date))

@slash.slash(name="Sup", description="Supprimer des messages", guild_ids=guild_ids, options = [create_option(name="nombre",description="Nombre de message à supprimer",required=True,option_type=4)])
@commands.has_permissions(manage_messages=True)
async def sup(ctx, nombre : int):
	print(f"Un utilisateur à utilisé la commande Supprimer pour {nombre} message(s)")
	
	await ctx.channel.purge(limit = nombre)
	message = "J'ai bien supprimé " + str(nombre) + " message(s)"
	embed = embedsimple(message)

	await ctx.send(embed=embed,delete_after=5)

@slash.slash(name="Ban", description="Bannir un membre", guild_ids=guild_ids, options = [create_option(name="membre",description="Membre à ban",required=True,option_type=6)])
@commands.has_permissions(administrator=True)
async def ban(ctx, membre, reason=None):
	print(f"Un utilisateur à utilisé le commande Ban pour l'utilisateur {membre}")

	await membre.ban(reason = reason)

	message = "Le membre " + str(membre) + " a bien été banni"
	embed=embedsimple(message)

	await ctx.send(embed=embed)

@slash.slash(name="Help", description="Donne toutes les commande disponibles", guild_ids=guild_ids)
async def help(ctx):

	print(f"Un utilisateur à utilisé le commande Help")

	await ctx.send(embed=embedhelp())

@slash.slash(name="Say", description="Dire un message", guild_ids=guild_ids, options = [create_option(name="message",description="Message à envoyer",required=True,option_type=3)])
async def say(ctx, message : str):
	await ctx.send(message)

@sup.error
@ban.error
async def error(ctx, error):
	if isinstance(error, MissingPermissions):
		message = "Vous n'avez pas la permsision de faire ça"
		embed = embedsimple(message)

		await ctx.send(embed=embed)

# Lancer le bot
bot.run(os.getenv("TOKEN"))
