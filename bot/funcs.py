import disnake

async def update_selection_message1(interaction):
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
    select = disnake.ui.Select(options=options, placeholder="Выберите нужную криптовалюту")

    await interaction.message.edit("Выберите криптовалюту:", components=[select])

async def update_selection_message(interaction):
    bitcoin_emoji = disnake.PartialEmoji(name=":Money~3:", id=1214321507749199922)
    ethereum_emoji = disnake.PartialEmoji(name=":CH_MoneyFlying:", id=901099387999105124)
    solana_emoji = disnake.PartialEmoji(name=":Money~2:", id=1188283987291021322)
    litecoin_emoji = disnake.PartialEmoji(name=":Money~5:", id=1007102830378749983)
    options = [
        disnake.SelectOption(label="Неделю", emoji=bitcoin_emoji, value="1week_"),
        disnake.SelectOption(label="Месяц", emoji=ethereum_emoji, value="1month_"),
        disnake.SelectOption(label="3 месяца", emoji=solana_emoji, value="3month_"),
        disnake.SelectOption(label="Навсегда", emoji=litecoin_emoji, value="forever_"),
    ]
    select = disnake.ui.Select(options=options, placeholder="Выберите нужный купон")

    embed = disnake.Embed(
        description='''
Бесплатные сделки на неделю - 10$

Бесплатные сделки на месяц - 20$

Бесплатные сделки на 3 месяца - 40$

Бесплатные сделки навсегда - 100$
'''
                    "\nДанные купоны дают Вам возможность проводить\n бесплатные сделки на определенный срок!"
                    "\n\nВыберите интересующий Вас купон ниже.",
        colour=0x1bde66)

    embed.set_author(name="Купоны",
                     icon_url="https://storage.googleapis.com/wp-static/thejacktherippertour.com/2018/01/gift-voucher1.png")

    view = disnake.ui.View()
    view.add_item(select)

    await interaction.message.edit(embed=embed, view=view)