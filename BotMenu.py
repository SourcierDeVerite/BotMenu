# https://bit.ly/2YM69Ia
import discord
import datetime
import time
import os
import urllib.request
import mysql.connector
import json

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option,create_choice
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from mysql.connector import errorcode

#-----------------------------------------------------------------------------------------------------------

def datajson():
	global data, listeRestaurant
	f = open("./data.json", encoding="utf-8")
	data = json.load(f)
	listeRestaurant = []
	url = []
	for i in range(len(data["restaurant"])):
		listeRestaurant.append(data["restaurant"][i]["lieu"] + ": " + data["restaurant"][i]["nom"])
	
def connexionBDD():
	global bdd
	try:
		bdd = mysql.connector.connect(
			user = "botmenu",
			password = os.getenv("mdpBDD"),
			host = "localhost",
			database = "botmenu"
			)

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR: print("Nom d'utilisateur ou mot de passe incorrect")
		elif err.errno == errorcode.ER_BAD_DB_ERROR: print("La base de donnée n'existe pas")
		else: print(err)

def select(requete:str):
	curseur = bdd.cursor()
	curseur.execute(requete)
	reponse = curseur.fetchall()
	return reponse

def requete(requete:str):
	curseur = bdd.cursor()
	curseur.execute(requete)
	bdd.commit()

def date ():

	jour = datetime.datetime.today().strftime('%d')
	if jour[0]== "0" : jour = jour[1]
	moisen = datetime.datetime.today().strftime('%B')
	annee = datetime.datetime.today().strftime('%Y')

	moisentab = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	moisfrtab = ["janvier", "fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]

	for i in range(len(moisentab)): 
		if moisentab[i] == moisen : 
			mois = moisfrtab[i]

	date = jour + " " + mois + " " + annee
	return date

def scrap(num:int):

	menu = {}
	alphabetmaj = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

	url = data["restaurant"][num]["lien"]

	page = urllib.request.urlopen(url).read().decode("utf-8")
	codesource = BeautifulSoup(page, 'html.parser')
	codesource = codesource.get_text()
	codesource = str(codesource)

	debut = codesource.find(date())
	codesource = codesource[debut:]
	fin = codesource.find("Dîner")
	codesource = codesource[:fin]

	categorie = data["restaurant"][num]["categorie"]

	for i in range (len(categorie)):
		debut = codesource.find(categorie[i])
		if i == len(categorie)-1: 
			menu[categorie[i]] = codesource[debut+len(categorie[i]):]
		else: 
			menu[categorie[i]] = codesource[debut+len(categorie[i]):codesource.find(categorie[i+1])]

	for i in range (len(menu)):
		menu[categorie[i]] = menu[categorie[i]].replace("VG", "vg")
		for ii in range(25):    
			menu[categorie[i]] = menu[categorie[i]].replace(alphabetmaj[ii],"\n" + alphabetmaj[ii])

		menu[categorie[i]] = menu[categorie[i]].replace("vg", "VG")

	return menu
   
def embedsimple(message):
	embed = discord.Embed(title=message, color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	embed.set_footer(text="Crée par Sourcier De Vérité#1962") 

	return embed

def embedmenu(menu:dict, num:int):
	embed = discord.Embed(title="Le menu d'aujourd'hui est :",description=date(),color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	
	embed.add_field(name="Restaurant", value=data["restaurant"][num]["lieu"]+": "+data["restaurant"][num]["nom"] , inline=False)
	
	for i in data["restaurant"][num]["categorie"]:
		embed.add_field(name=i, value=menu[i], inline=False)

	embed.set_footer(text="Crée par Sourcier De Vérité#9113")

	return embed

def embedhelp():
	embed = discord.Embed(title="Voici les commandes disponibles :",color=discord.Color.red())
	embed.set_author(name="Crous", icon_url="https://upload.wikimedia.org/wikipedia/commons/b/b5/Crous_logo.jpg")
	embed.add_field(name="Ping", value="Permet d'obtenir le ping du bot", inline=False)
	embed.add_field(name="Menu", value="Permet d'envoyer le menu d'aujourd'hui, en choissisant le restaurant universitaire de votre choix", inline=False)
	embed.add_field(name="Sup x", value="Permet de supprimer x messages (Reservé au Admin)", inline=False)
	embed.add_field(name="Ban x", value="Permet de bannir un membre (Reservé au Admin)", inline=False)
	embed.set_footer(text="Crée par Sourcier De Vérité#1962")
	
	return embed

#-----------------------------------------------------------------------------------------------------------

load_dotenv(dotenv_path="config.env")
datajson()
connexionBDD()

listeServeur=[]
for i in range(len(select("SELECT id FROM guild"))):
    listeServeur.append(int(select("SELECT id FROM guild")[i][0]))

bot=commands.Bot(command_prefix=";", help_command=None)
slash=SlashCommand(bot, sync_commands=True)
adminServeur=[715926570795008010]

@bot.event
async def on_ready():
	print("\nLe bot est connecté ! \n")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='/help'))

#-----------------------------------------------------------------------------------------------------------

@bot.event
async def on_guild_join(guild):
	requete("INSERT INTO guild(id, name) SELECT '" + str(guild.id) + "', '" + str(guild.name) + "' FROM dual WHERE NOT EXISTS (SELECT 1 FROM guild WHERE ID = " + str(guild.id) + ");")
	print("Le Botmenu a rejoint le serveur " + str(guild.name) + " (" + str(guild.id) + ")")

@bot.event
async def on_guild_remove(guild):
	requete("DELETE FROM guild WHERE id = " + str(guild.id) + ";")
	print("Le Botmenu a quitté le serveur " + str(guild.name) + " (" + str(guild.id) + ")")

#-----------------------------------------------------------------------------------------------------------

@slash.slash(name="Ping", description="Envoie le ping du bot", guild_ids=listeServeur)
async def ping(ctx):
	print("Un utilisateur à utilisé la commande Ping")

	message = "Mon ping est de " + str(round(bot.latency * 1000)) + "ms"

	await ctx.reply(embed=embedsimple(message))

@slash.slash(name="Menu", description="Envoie le menu du RU", guild_ids=listeServeur, options=[create_option(name="restaurant", description="Choisir le restaurant", required=False, choices=listeRestaurant, option_type=3)])
async def menu(ctx, restaurant: str="son restau préféré"):
	print("Un utilisateur à utilisé la commande Menu pour le restaurant", restaurant)

	try:
		if restaurant == "son restau préféré":
			restaurant = select("SELECT restaurant FROM guild WHERE id=" + str(ctx.guild.id))[0][0]
			if restaurant == None:
				message = "Aucun restaurant par défaut n'est configuré, faite /conf pour en configurer un"
				await ctx.send(embed=embedsimple(message))
			else:
				await ctx.send(embed=embedmenu(scrap(restaurant),restaurant))
		else:
			await ctx.send(embed=embedmenu(scrap(listeRestaurant.index(restaurant)),listeRestaurant.index(restaurant)))
		
	except urllib.error.HTTPError as exception:
		message = "Désolé, mais le site du Crous est inaccessible pour l'instant"
		await ctx.send(embed=embedsimple(message))

	except Exception as e: 
		message = "Désolé, il y a eu un problème"
		await ctx.send(embed=embedsimple(message))
		print(e)

@slash.slash(name="Sup", description="Supprimer des messages", guild_ids=listeServeur, options=[create_option(name="nombre", description="Nombre de message à supprimer (0 pour tout supprimer)", required=True, option_type=4)])
@commands.has_permissions(administrator = True)
async def sup(ctx, nombre: int):
	if nombre == 0 : 
		print(f"Un utilisateur à utilisé la commande Supprimer le salon #{ctx.channel}")

		newchannel = await (ctx.channel).clone()
		await(ctx.channel).delete()

		message = "J'ai bien vidé le channel #" + str(newchannel)
		await newchannel.send(embed=embedsimple(message),delete_after=5)
	else : 
		print(f"Un utilisateur à utilisé la commande Supprimer pour {nombre} message(s)")
	
		await ctx.channel.purge(limit = nombre)
		message = "J'ai bien supprimé " + str(nombre) + " message(s)"

		await ctx.send(embed=embedsimple(message),delete_after=5)

@slash.slash(name="Ban", description="Bannir un membre", guild_ids=listeServeur, options=[create_option(name="membre", description="Membre à ban", required=True, option_type=6)])
@commands.has_permissions(administrator=True)
async def ban(ctx, membre, reason=None):
	print(f"Un utilisateur à utilisé la commande Ban pour l'utilisateur {membre}")

	await membre.ban(reason = reason)

	message = "Le membre " + str(membre) + " a bien été banni"

	await ctx.send(embed=embedsimple(message))

@slash.slash(name="Help", description="Donne toutes les commande disponibles", guild_ids=listeServeur)
async def help(ctx):

	print(f"Un utilisateur à utilisé la commande Help")

	await ctx.send(embed=embedhelp())

@slash.slash(name="Configuration", description="Configure les différents paramètres", guild_ids=listeServeur, options=[create_option(name="restaurant", description="Choisir son restaurant par défaut", required=False, choices=listeRestaurant, option_type=3)])
async def annonce(ctx, restaurant: str=None):
	print("Un utilisateur à utilisé la commande Configuration")

	requete("UPDATE guild SET restaurant=" + str(listeRestaurant.index(restaurant)) + " WHERE id=" + str(ctx.guild.id))

	message = "Changement effectué"
	await ctx.send(embed=embedsimple(message))

@slash.slash(name="Sync", description="Synchroniser les serveurs dans la BDD", guild_ids=adminServeur)
async def sync(ctx):
	if ctx.author.id != 300325657324552193:
		message = "Vous n'avez pas la permission de faire ça"
		await ctx.send(embed=embedsimple(message))
		return

	for guild in bot.guilds:
		requete("INSERT INTO guild(id, name) SELECT '" + str(guild.id) + "', '" + str(guild.name) + "' FROM dual WHERE NOT EXISTS (SELECT 1 FROM guild WHERE ID = " + str(guild.id) + ");")
	message = "Synchronisation réussi"	
	await ctx.send(embed=embedsimple(message))

@sup.error
@ban.error
async def error(ctx, error):
	if isinstance(error, MissingPermissions):
		message = "Vous n'avez pas la permission de faire ça"

		await ctx.send(embed=embedsimple(message))

bot.run(os.getenv("TOKEN"))