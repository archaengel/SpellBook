from discord.ext import commands
from discord import Intents, Embed
import os
import requests
import json
from pydash.strings import slugify, upper_first

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

dnd_root = 'https://www.dnd5eapi.co'
dnd_api = dnd_root + '/api/'

@bot.command()
async def test(ctx):
    await ctx.send("Test received!")
    
@bot.command()
async def thank(ctx, arg):
    await ctx.send(f"Thank you, {arg}!")

memo = dict()
def get_classes(target):
    classes_endpoint = dnd_api + 'classes/'
    classes_res = requests.get(classes_endpoint)
    json_classes = json.loads(classes_res.text)
    for _class in json_classes['results']:
        memo[_class['index']] = _class
        
    if target in memo:
        if 'spells' not in memo[target].keys():
            target_res = requests.get(classes_endpoint + target)
            json_target = json.loads(target_res.text)
            spells_res = requests.get(dnd_root + json_target['spells'])
            json_spells = json.loads(spells_res.text)
            memo[target]['spells'] = list(spell['name'] for spell in json_spells['results'])
        return memo[target]['spells']

    return None

@bot.command()
async def spells(ctx, *args):
    if len(args) == 1:
        target = slugify(args[0])
        if  get_classes(target) is not None:
            spells = get_classes(target)
            await ctx.send(f"{upper_first(target)}s can cast {', '.join(spells)}")
            return
    spells_endpoint = dnd_api + 'spells/' + slugify("-".join(args))
    res = requests.get(spells_endpoint)
    if res.status_code == 404:
        await ctx.send(f"""A million apologies, adventurers. I cannot find '{" ".join(args)}'""")
        return
    json_res = json.loads(res.text)
    #await ctx.send(json_res['desc'][0])
    await ctx.send(embed=Embed.from_dict(json_res))
    

bot.run(os.environ['CLIENT_TOKEN'])