import datetime
import disnake
from disnake.ext import commands
import asyncio
from db import Database, Database_users
from payments import *
from bot.funcs import (update_selection_message1, update_selection_message)
from bot.classes import (DealVouchers, DealState)
from datetime import datetime, timedelta


db = Database('db.db')
db_users = Database_users('db.db')
intents = disnake.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)



def check_entering(msg):
    return msg.content.isdigit()

async def create_category(guild, name):
    existing_category = disnake.utils.get(guild.categories, name=name)
    if existing_category:
        return existing_category
    return await guild.create_category(name)


async def button_callback(interaction: disnake.Interaction):
    channel = interaction.channel
    category = channel.category
    await channel.delete(reason="Deal closed by user.")
    if category:
        await category.delete(reason="Deal closed by user.")


@bot.event
async def on_ready():
    print(f'{bot.user.name} подключился к Discord!')

@bot.command()
async def language(ctx, option):
    if option in ["ru", "en"]:
        try:
            db_users.set_lang(ctx.author.id, option)
            if option == "ru":
                await ctx.send("Вы успешно сменили язык")
            else:
                await ctx.send("You successfully chose language")
        except Exception:
            await ctx.send("You are not in database")
    else:
        await ctx.send("Invalid argument")

@commands.has_role("ADMIN")
@bot.command()
async def send_with_button(ctx):
    bitcoin_emoji = disnake.PartialEmoji(name="Bitcoin", id=1239239138616803400)
    usdt_emoji = disnake.PartialEmoji(name="usdt", id=1257213762075754588)
    ethereum_emoji = disnake.PartialEmoji(name="eth", id=1262433445083086911)
    litecoin_emoji = disnake.PartialEmoji(name="litecoin", id=1262434323311628441)
    solana_emoji = disnake.PartialEmoji(name="solana", id=1265251887607844925)

    options = [
    	disnake.SelectOption(label="Bitcoin", emoji=bitcoin_emoji, value="bitcoin_choice"),
   	    disnake.SelectOption(label="USDT", emoji=usdt_emoji, value="usdt_choice"),
        disnake.SelectOption(label="Ethereum", emoji=ethereum_emoji, value="ethereum_choice"),
        disnake.SelectOption(label="Litecoin", emoji=litecoin_emoji, value="litecoin_choice"),
        disnake.SelectOption(label="Solana", emoji=solana_emoji, value="solana_choice"),
    ]
    select = disnake.ui.Select(options=options, placeholder="Choose correct crypto")

    await ctx.send(embed = disnake.Embed(title = "Choose needable crypto", description="*Deals $250+: `1%`*\n*Deals under $250: `$2`*\n*Deals under $50 are `FREE`*"), components=[select])


@bot.event
async def on_dropdown(interaction):
    user = interaction.user
    guild = interaction.guild
    selected_currency = interaction.data['values'][0]
    print(user.id)
    if db_users.user_exists(user.id) == True:
        pass
    else:
        db_users.add_user(user.id)
    
    if selected_currency in ["bitcoin_choice", "usdt_choice", "litecoin_choice", "ethereum_choice", "solana_choice"]:
        lang = "en"
        for i in db_users.get_data_users():
            if i[1] == interaction.user.id:
                lang = i[2]
            else:
                lang = i[2]

        button = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="🔒 Close", custom_id="stop_deal_button")
        button.callback = button_callback
        view = disnake.ui.View()
        view.add_item(button)

        category = await create_category(guild, user)

        existing_channel = disnake.utils.get(category.channels, name=selected_currency)
        if existing_channel:
            return existing_channel
        
        # Создание канала
        channel = await category.create_text_channel(selected_currency)
        
        # Установка прав доступа
        await channel.set_permissions(category.guild.default_role, view_channel=False)  # Скрыть от всех по умолчанию
        await channel.set_permissions(user, view_channel=True)  # Разрешить видимость для user1

        await update_selection_message1(interaction)
        if lang == "ru":
            await interaction.response.send_message(f"Создан канал {channel.mention} для криптовалюты {selected_currency}.",
                                                    ephemeral=True)
            await channel.send("Ваш хэш:\nВыберите опцию", view=view)

            embed = disnake.Embed(
                title="Кто будет проводить сделку с вами?",
                description="eg. @JohnDoe\neg. 123456789123456789",
                colour=0x07df0a
            )
            await channel.send(embed=embed)
        else:
            await interaction.response.send_message(f"Created channel {channel.mention} for crypto {selected_currency}.",
                                                    ephemeral=True)
            await channel.send("Your hash:\nChoose option", view=view)

            embed = disnake.Embed(
                title="Who are you dealing with?",
                description="eg. @JohnDoe\neg. 123456789123456789",
                colour=0x07df0a
            )
            await channel.send(embed=embed)
        

        def check(msg):
            return msg.author == interaction.author and msg.channel == channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60.0)
            user_id = int(msg.content)
            member = guild.get_member(user_id)

            if member:
                if lang == "ru":
                    await channel.send(f"Пользователь {member.mention} найден. Отправляю запрос на сделку...")

                    accept_button = disnake.ui.Button(style=disnake.ButtonStyle.success, label="Согласиться на сделку",
                                                    custom_id="accept_deal_button")
                    decline_button = disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Отказаться",
                                                    custom_id="decline_deal_button"
                                                       )

                else:
                    await channel.send(f"User {member.mention} found. Requesting for a deal...")

                    accept_button = disnake.ui.Button(style=disnake.ButtonStyle.success, label="Accept for a deal",
                                                    custom_id="accept_deal_button")
                    decline_button = disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Except for a deal",
                                                    custom_id="decline_deal_button")
                    

                deal_state = DealState()

                async def accept_callback(interaction: disnake.Interaction):
                    await channel.set_permissions(member, view_channel=True)  # Разрешить видимость для user1
                    deal_state.crypto_choice = selected_currency[:-7]
                    deal_state.db = db
                    deal_state.bot = bot
                    deal_state.channel = channel
                    if deal_state.sending_user_id and deal_state.sending_user_id == interaction.user.id:
                        if lang == "ru":
                            await interaction.response.send_message("Вы уже назначены отправителем.", ephemeral=True)
                        else:
                            await interaction.response.send_message("You are already designated by sender.", ephemeral=True)
                        return

                    if deal_state.receiving_user_id and deal_state.receiving_user_id == interaction.user.id:
                        if lang == "ru":
                            await interaction.response.send_message("Вы уже назначены получающим.", ephemeral=True)
                        else:
                            await interaction.response.send_message("You are already designated by receiver.", ephemeral=True)
                        return

                    async def sending_callback_text(interaction: disnake.Interaction):
                        if deal_state.receiving_user_id and deal_state.receiving_user_id == interaction.user.id:
                            if lang == "ru":
                                await interaction.response.send_message("Вы уже назначены получающим.", ephemeral=True)
                            else:
                                await interaction.response.send_message("You are already designated by receiver.", ephemeral=True)
                            return
                        deal_state.sending_user_id = interaction.user.name
                        await deal_state.update_embed()
                        await deal_state.check_and_send_confirmation(channel)

                    async def receiving_callback_text(interaction: disnake.Interaction):
                        if deal_state.sending_user_id and deal_state.sending_user_id == interaction.user.id:
                            if lang == "ru":
                                await interaction.response.send_message("Вы уже назначены отправителем.", ephemeral=True)
                            else:
                                await interaction.response.send_message("You are already designated by sender.", ephemeral=True)
                            return
                        deal_state.receiving_user_id = interaction.user.name
                        await deal_state.update_embed()
                        await deal_state.check_and_send_confirmation(channel)

                    async def resetting_callback_text(interaction: disnake.Interaction):
                        deal_state.sending_user_id = None
                        deal_state.receiving_user_id = None
                        await deal_state.update_embed()
                    if lang == "ru":
                            await interaction.response.send_message(embed=disnake.Embed(
                        description="<a:tw_check:671101827160342551>  Вы согласились на сделку!",
                        colour=0x07df0a
                    ), ephemeral=True)
                    else:
                            await interaction.response.send_message(embed=disnake.Embed(
                        description="<a:tw_check:671101827160342551>  You agreed with deal!",
                        colour=0x07df0a
                    ), ephemeral=True)
                    
                    await channel.set_permissions(member, read_messages=True, send_messages=True)

                    deal_state.view = disnake.ui.View()
                    deal_state.view.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Sending",
                                                               custom_id="sending_button"))
                    deal_state.view.add_item(disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Receiving",
                                                               custom_id="receiving_button"))
                    deal_state.view.add_item(
                        disnake.ui.Button(style=disnake.ButtonStyle.red, label="Reset", custom_id="reset_button"))

                    deal_state.message_to_edit = await channel.send(embed=deal_state.embed3, view=deal_state.view)

                    deal_state.view.children[0].callback = sending_callback_text
                    deal_state.view.children[1].callback = receiving_callback_text
                    deal_state.view.children[2].callback = resetting_callback_text

                async def decline_callback(interaction: disnake.Interaction):
                    if lang == "ru":
                        await interaction.response.send_message(embed=disnake.Embed(
                            description="<a:tw_check:671101827160342551>  Вы отказались от сделки!",
                            colour=0xdf0707
                        ), ephemeral=True)
                    else:
                        await interaction.response.send_message(embed=disnake.Embed(
                            description="<a:tw_check:671101827160342551>  You disagree of deal!",
                            colour=0xdf0707
                        ), ephemeral=True)

                accept_button.callback = accept_callback
                decline_button.callback = decline_callback

                view = disnake.ui.View()
                view.add_item(accept_button)
                view.add_item(decline_button)
                for i in db_users.get_data_users():
                    print(member.id)
                    if i[1] == member.id:
                        if lang == "ru":
                            await member.send("Вам предлагают сделку. Пожалуйста, выберите:", view=view)
                        else:
                            await member.send("You get an offer for a deal. Please, choose:", view=view)
                
                accept_button.callback = accept_callback
                
                decline_button.callback = decline_callback

                view = disnake.ui.View()
                view.add_item(accept_button)
                view.add_item(decline_button)
                if lang == "en":
                    await member.send("You offered a deal. Please, choose:", view = view)
                else:
                    await member.send("Вам предлагают сделку. Пожалуйста, выберите:", view = view)


            else:
                await channel.send("Пользователь с таким ID не найден на сервере.")
        except asyncio.TimeoutError:
            await channel.send("Время ожидания истекло. Пожалуйста, попробуйте снова.")
    
    
    
    elif selected_currency in ["1week_", "1month_", "3month_", "forever_"]:
        deal_vouchers = DealVouchers()
        button = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="🔒 Close",
                                   custom_id="stop_deal_button")

        button.callback = button_callback
        view = disnake.ui.View()
        view.add_item(button)
        category = await create_category(guild, user)

        existing_channel = disnake.utils.get(category.channels, name=selected_currency)
        if existing_channel:
            return existing_channel
        
        # Создание канала
        channel = await category.create_text_channel(selected_currency)
        
        # Установка прав доступа
        await channel.set_permissions(category.guild.default_role, view_channel=False)  # Скрыть от всех по умолчанию
        await channel.set_permissions(user, view_channel=True)  # Разрешить видимость для user1

        await interaction.response.send_message(f"Создан канал {channel.mention} для купона {selected_currency}.",
                                                ephemeral=True)
        await channel.send("Ваш хэш:\nВыберите опцию", view=view)

        if selected_currency == "1week_":
            price = "10$"
        elif selected_currency == "1month_":
            price = "20$"
        elif selected_currency == "3month_":
            price = "40$"
        elif selected_currency == "forever_":
            price = "100$"

        deal_vouchers.sum = price
        deal_vouchers.choose = selected_currency
        deal_vouchers.user = user
        deal_vouchers.db = db
        deal_vouchers.bot = bot


        embed = disnake.Embed(title="Purchase Confirmation",
                              description="Please confirm the amount that you are purchasing",
                              colour=0x1bde66)

        embed.add_field(name="Amount",
                        value="1",
                        inline=True)
        embed.add_field(name="Price",
                        value=f"{price}",
                        inline=True)

        view = disnake.ui.View()

        button1 = disnake.ui.Button(style=disnake.ButtonStyle.green, label="Confirm",
                                    custom_id="confirm_voucher_button")

        button2 = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Cancel",
                                    custom_id="cancel_voucher_button")


        button1.callback = deal_vouchers.confirm_button_voucher
        button2.callback = deal_vouchers.button_callback

        view.add_item(button1)
        view.add_item(button2)

        await channel.send(embed=embed, view=view)
        # db.add_voucher(user.id, selected_currency)

        await update_selection_message(interaction)


async def create_category(guild, user):
    return await guild.create_category(name=f"Crypto-{user.name}")


async def create_crypto_channel(category, currency):
    return await category.create_text_channel(name=f"{currency}-deal")



@commands.has_role("ADMIN")
@bot.command()
async def vouchers_choose(ctx):
    bitcoin_emoji = disnake.PartialEmoji(name=":Money~3:", id=1214321507749199922)
    ethereum_emoji = disnake.PartialEmoji(name=":CH_MoneyFlying:", id=901099387999105124)
    solana_emoji = disnake.PartialEmoji(name=":Money~2:", id=1188283987291021322)
    litecoin_emoji = disnake.PartialEmoji(name=":Money~5:", id=1007102830378749983)

    options = [
        disnake.SelectOption(label="Week", emoji=bitcoin_emoji, value="1week_"),
        disnake.SelectOption(label="Month", emoji=ethereum_emoji, value="1month_"),
        disnake.SelectOption(label="3 monthes", emoji=solana_emoji, value="3month_"),
        disnake.SelectOption(label="Forever", emoji=litecoin_emoji, value="forever_"),
    ]
    select = disnake.ui.Select(options=options, placeholder="Choose needable voucher")

    embed = disnake.Embed(
        description='''

Free deals for a week - 10$

Free deals for a month - 20$

Free deals for 3 monthes - 40$

Free deals forever - 100$
'''
                    "\nThese coupons give you the opportunity to spend\n free deals for a certain period!"
                    "\n\nSelect the coupon you are interested in below.",
        colour=0x1bde66)

    embed.set_author(name="Vouchers",
                     icon_url="https://storage.googleapis.com/wp-static/thejacktherippertour.com/2018/01/gift-voucher1.png")

    await ctx.send(embed=embed, components=[select])






if __name__ == "__main__":
    #  MTAyOTY2MjY0NzA2ODY3MjA1MA.G8p0LD.40xLzSAw8xbZh0R8Om-7VoZwrsbIf2huaZ8pjU
    bot.run("")