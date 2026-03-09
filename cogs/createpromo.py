import sqlite3
from disnake import Embed, Role, ApplicationCommandInteraction
from disnake.ext import commands
from utils import config  
import datetime


# Подключение к базе данных SQLite
conn = sqlite3.connect("promocodes.db")
cursor = conn.cursor()

# Создание таблиц
cursor.execute("""
CREATE TABLE IF NOT EXISTS promocodes (
    code TEXT PRIMARY KEY,
    role_id INTEGER NOT NULL,
    max_uses INTEGER NOT NULL,
    uses_left INTEGER NOT NULL
)
""")
conn.commit()


class PromoCreate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="createpromo", description="Создать промокод")
    async def create_promo(
        self,
        inter: ApplicationCommandInteraction,
        code: str,
        role: Role,
        max_uses: int = 1
    ):
        
    
        if inter.author.id not in config.OWNER_IDS:
            await inter.response.send_message("❌ Эта команда доступна только владельцам.", ephemeral=True)
            return

        # Проверка на существование промокода
        cursor.execute("SELECT * FROM promocodes WHERE code = ?", (code,))
        if cursor.fetchone():
            await inter.response.send_message(f"⚠️ Промокод `{code}` уже существует! Придумайте другое название.", ephemeral=True)
            return

        # Сохранение промокода
        cursor.execute("INSERT INTO promocodes (code, role_id, max_uses, uses_left) VALUES (?, ?, ?, ?)",
                       (code, role.id, max_uses, max_uses))
        conn.commit()

        # Embedik
        embed = Embed(
            title="🎉 Промокод успешно создан!",
            color=0x00FF00,
            timestamp=datetime.datetime.now(),

        )
        embed.add_field(name="🛍️ Промокод", value=f"`{code}`", inline=False)
        embed.add_field(name="🔑 Роль", value=role.mention, inline=False)
        embed.add_field(name="📈 Максимальные активации", value=f"{max_uses}", inline=False)
        embed.set_footer(text=f"Создано: {inter.author}")
        embed.set_image(url="https://impult.ru/preview/r/456x456/upload/iblock/6da/w83h460byaflbly4y0lvgz5umtaxzlsg.jpg")


        await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="promo", description="Активировать промокод")
    async def use_promo(self, inter: ApplicationCommandInteraction, code: str):
       
        cursor.execute("SELECT role_id, uses_left FROM promocodes WHERE code = ?", (code,))
        result = cursor.fetchone()

        if result:
            role_id, uses_left = result
            role = inter.guild.get_role(role_id)

            if role:
                await inter.author.add_roles(role)

                if uses_left > 1:
                    cursor.execute("UPDATE promocodes SET uses_left = uses_left - 1 WHERE code = ?", (code,))
                    conn.commit()
                else:
                    # Удаляем промокод, если активации закончились
                    cursor.execute("DELETE FROM promocodes WHERE code = ?", (code,))
                    conn.commit()

                # Embedik
                embed = Embed(
                    title="✅ Вы успешно активировали промокод!",
                    description=f"Вы успешно получили приз - {role.mention}.",
                    color=0x00FF00,
                    timestamp=datetime.datetime.now(),

                )
                embed.set_footer(text=f"Поздравляем, {inter.author.name}!")
                embed.set_image(url="https://impult.ru/preview/r/456x456/upload/iblock/6da/w83h460byaflbly4y0lvgz5umtaxzlsg.jpg")
                await inter.response.send_message(embed=embed)
            else:
                await inter.response.send_message("⚠️ Эта роль больше не существует на сервере.", ephemeral=True)
        else:
            embed = Embed(
                title="❌ Неверный промокод",
                description="Этот промокод не существует или уже был использован.",
                color=0xFF0000,
                timestamp=datetime.datetime.now(),

            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="viewpromos", description="Просмотр всех доступных промокодов.")
    async def view_promos(self, inter: ApplicationCommandInteraction):
        
        if inter.author.id not in config.OWNER_IDS:
            await inter.response.send_message("❌ Эта команда доступна только владельцам.", ephemeral=True)
            return

        cursor.execute("SELECT code, role_id, max_uses, uses_left FROM promocodes")
        promocodes = cursor.fetchall()

        if promocodes:
            embed = Embed(
                title="📜 Список всех доступных промокодов",
                description="Вот список всех промокодов, которые можно использовать:",
                color=0x00FF00,
                timestamp=datetime.datetime.now(),

            )
            for code, role_id, max_uses, uses_left in promocodes:
                role = inter.guild.get_role(role_id)
                role_name = role.name if role else "Роль не найдена"
                embed.add_field(
                    name=f"🎫 Промокод: `{code}`",
                    value=f"🔑 Роль: {role_name}\n📈 Макс. активаций: {max_uses}\n🕒 Осталось активаций: {uses_left}",
                    inline=False
                    
                )
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            await inter.response.send_message("🚫 Нет доступных промокодов.", ephemeral=True)


def setup(bot):
    bot.add_cog(PromoCreate(bot))
