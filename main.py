import os
import disnake
from disnake.ext import commands
from utils import config

intents = disnake.Intents.all()  
bot = commands.Bot(command_prefix="!", intents=intents)  

@bot.event
async def on_ready():
    print("Я включился")
    print("Запуск!")

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

@bot.slash_command(name="reload", description="Перезагружает все модули в папке cogs")
async def reload(inter: disnake.ApplicationCommandInteraction):
    try:
        if inter.author.id in config.OWNER_IDS:
            try:
                for filename in os.listdir('./cogs'):
                    if filename.endswith('.py'):
                        cog_name = f'cogs.{filename[:-3]}'
                        bot.reload_extension(cog_name)
                
                embed = disnake.Embed(title="Успех", description="Все модули перезагружены", color=config.Success())
                embed.set_footer(text=f"Запрос от {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
            except Exception as e:
                embed = disnake.Embed(title="Ошибка", description=f"Не удалось перезагрузить модули из-за {e}", color=config.Error())
                embed.set_footer(text=f"Запрос от {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="Ошибка", description="Вам не разрешено использовать эту команду!", color=config.Error())
            embed.set_footer(text=f"Запрос от {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'Произошла ошибка при перезагрузке кодов! {e}')

bot.run(config.TOKEN)