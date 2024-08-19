import asyncio
import cryptocompare
import disnake
from payments import *
from datetime import datetime, timedelta
from disnake.ext import commands
from disnake import TextInputStyle
import json

def check_entering(msg):
    print(msg)
    value = float(int(msg.content))
    if 1 < value < 10000:
        return value

def check_entering_receiving_address(msg):
    
    value = msg.content
    try: 
        str(value)
        print(value)
        return value
    except Exception:
        return False


class DealVouchers:
    def __init__(self):
        self.user = None
        self.sum = None
        self.choose = None
        self.crypto_choice = 0
        self.crypto_class = None
        self.bot = None
        self.needs_crypto_send = None
        self.db = None
        self.rate = None
    async def button_callback(self, interaction: disnake.Interaction):
        embed = disnake.Embed(title="Cancel",
                            description="The deal was canceled",
                            colour=0xdf0707)

        await interaction.response.send_message(embed=embed)

    async def button_for_sending_money(self, interaction: disnake.Integration):
        payment_class = self.crypto_class
        if self.crypto_choice == "ethereum_voucher":
            balance = await payment_class.check_balance()
        else:
            balance = payment_class.check_balance()
        
        print(self.needs_crypto_send)
        if float(balance) >= float(self.needs_crypto_send):
            self.db.add_voucher(interaction.user.id, self.choose, datetime.now())
            bal = balance * 1e9
            payment_class.send_payment("3RN3T1NRmrCD2Y8aDxNUDz67sTyHrQSUjCker9Jexj98", bal-5000)
            await interaction.response.send_message(embed = disnake.Embed(
                title = f"> Transaction completed ✅",
                description= f"*You received pass*",
                
            ))
            
        elif balance > 0:
            
            await interaction.response.send_message(embed = disnake.Embed(
                title = f"> Getting {balance} {self.crypto_choice.split('_')[0]}",
                description= f"*Needs {self.needs_crypto_send-balance} more*"
            ))
        else:
            await interaction.channel.send(embed = disnake.Embed(
                title = f"> We haven't fixed any transaction",
                description= f"*You need to send again*",
                
            ))

    async def send_crypto_callback(self, interaction: disnake.Interaction):
        self.sum = self.sum[:-1]
        print(self.sum)
        selected_currency = interaction.data['values'][0]

        self.crypto_choice = selected_currency[:-7]
        payment_url = ""
        if self.crypto_choice == "bitcoin_voucher":
            payment = BitcoinPayment("0c881939cdaf4b4a9f9e3c7d439b9d4e")
            payment_url = payment.get_address()
            self.crypto_class = payment

        elif self.crypto_choice == "usdt_voucher":
            payment = UsdtPayment("02b62268c6b04bd49ded8090a5f539e4")
            payment_url = payment.get_address()
            self.crypto_class = payment
        elif self.crypto_choice == "ethereum_voucher":
            payment = EthereumPayment()
            payment_url = payment.get_address()
            self.crypto_class = payment

        elif self.crypto_choice == "litecoin_voucher":
            payment = LitecoinPayment()
            payment_url = payment.get_address()
            self.crypto_class = payment

        elif self.crypto_choice == "solana_voucher":
            payment = SolanaPayment()
            payment_url = payment.get_address()
            self.crypto_class = payment
        
        if self.crypto_choice.split('_')[0] == "bitcoin":
            self.needs_crypto_send = int(self.sum) / cryptocompare.get_price('BTC', currency='USD')['BTC']['USD']
        elif self.crypto_choice.split('_')[0] == "usdt":
            self.needs_crypto_send = int(self.sum) / cryptocompare.get_price('USDT', currency='USD')['USDT']['USD']
        elif self.crypto_choice.split('_')[0] == "ethereum":
            self.needs_crypto_send = int(self.sum) / cryptocompare.get_price('ETH', currency='USD')['ETH']['USD']
        elif self.crypto_choice.split('_')[0] == "litecoin":
            self.needs_crypto_send = int(self.sum) / cryptocompare.get_price('LTC', currency='USD')['LTC']['USD']
        elif self.crypto_choice.split('_')[0] == "solana":
            self.needs_crypto_send = int(self.sum) / cryptocompare.get_price('SOL', currency='USD')['SOL']['USD']
        if self.crypto_choice.split == "bitcoin":
            self.rate = cryptocompare.get_price('BTC', currency='USD')['BTC']['USD']
        elif self.crypto_choice.split == "usdt":
            self.rate = cryptocompare.get_price('USDT', currency='USD')['USDT']['USD']
        elif self.crypto_choice.split == "ethereum":
            self.rate = cryptocompare.get_price('ETH', currency='USD')['ETH']['USD']
        elif self.crypto_choice.split == "litecoin":
            self.rate =cryptocompare.get_price('LTC', currency='USD')['LTC']['USD']
        elif self.crypto_choice.split == "solana":
            self.rate = cryptocompare.get_price('SOL', currency='USD')['SOL']['USD']
        
        button = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="✅ I sent money",
                                               custom_id="check_sending_money")
        button.callback = self.button_for_sending_money
        # db.add_deal()
        await interaction.channel.send(embed=disnake.Embed(
                        title="🕹 Payment Invoice",
                        description="> Please send the funds as part of the deal to the Middleman address specified below.\n> To ensure the validation of your payment, please copy and paste the amount provided.",
                        colour=0x00ff40
                    ).add_field(
                        name=f"{self.crypto_choice.split('_')[0]} Address",
                        value=f"{payment_url}",
                        inline=False
                    ).add_field(
                        name=f"{self.crypto_choice.split('_')[0]} Amount",
                        value=self.needs_crypto_send,
                        inline=False
                    ).add_field(
                        name="USD Amount",
                        value=f"${self.sum}",
                        inline=False
                    ).add_field(
                        name=f"Exchange Rate: 1 {self.crypto_choice.split('_')[0]} = ${self.rate}",
                        value="> *Waiting for transaction*",
                        inline=False
                    ), view=disnake.ui.View().add_item(button))



    async def confirm_button_voucher(self, interaction: disnake.Interaction):
        bitcoin_emoji = disnake.PartialEmoji(name="Bitcoin", id=1239239138616803400)
        usdt_emoji = disnake.PartialEmoji(name="usdt", id=1257213762075754588)
        ethereum_emoji = disnake.PartialEmoji(name="eth", id=1262433445083086911)
        litecoin_emoji = disnake.PartialEmoji(name="litecoin", id=1262434323311628441)
        solana_emoji = disnake.PartialEmoji(name="solana", id=1265251887607844925)

        select_options = [
            disnake.SelectOption(label="Bitcoin", emoji=bitcoin_emoji, value="bitcoin_voucher_choice"),
            disnake.SelectOption(label="USDT", emoji=usdt_emoji, value="usdt_voucher_choice"),
            disnake.SelectOption(label="Ethereum", emoji=ethereum_emoji, value="ethereum_voucher_choice"),
            disnake.SelectOption(label="Litecoin", emoji=litecoin_emoji, value="litecoin_voucher_choice"),
            disnake.SelectOption(label="Solana", emoji=solana_emoji, value="solana_voucher_choice")
            ]
        select_menu = disnake.ui.Select(
            options=select_options,
            placeholder="Select a cryptocurrency",
            min_values=1,
            max_values=1
        )
        select_menu.callback = self.send_crypto_callback

        embed = disnake.Embed(title="Payment Pending",
                            description=f"Please send ${self.sum[:-1]}.00 with one method crypto sending",
                            colour=0xf3ed44)

        await interaction.response.send_message(embed=embed, view=disnake.ui.View().add_item(select_menu))


class DealState:
    def __init__(self):
        self.rate = None
        self.sending_user_id = None
        self.receiving_user_id = None
        self.message_to_edit = None
        self.confirm_message = None
        self.correct_count = 0
        self.crypto_choice = "bitcoin"
        self.sum = None
        self.embed3 = disnake.Embed(
            title="Confirmed Role Identities",
            description="Both users have confirmed their roles within this deal.",
            colour=0x39db39
        )
        self.needs_crypto_send = 0
        self.db = None
        self.bot = None
        self.view = disnake.ui.View()
        self.confirm_view = disnake.ui.View()
        self.needs_crypto_send = None
        self.crypto_class = None
        self.channel = None

    async def update_embed(self):
        self.embed3.clear_fields()
        self.embed3.add_field(name="Sending", value=f"{self.sending_user_id or 'None'}", inline=True)
        self.embed3.add_field(name="Receiving", value=f"{self.receiving_user_id or 'None'}", inline=True)
        if self.message_to_edit:
            await self.message_to_edit.edit(embed=self.embed3, view=self.view)

    async def check_and_send_confirmation(self, channel):
        if self.sending_user_id and self.receiving_user_id:
            self.channel = channel
            for item in self.view.children:
                item.disabled = True
            await self.message_to_edit.edit(embed=self.embed3, view=self.view)
            await self.message_to_edit.delete()
            print(self.receiving_user_id)
            confirm_embed = disnake.Embed(
                title="Confirmed Role Identities",
                description="Both users have confirmed their roles within this deal",
                colour=0x00b0f4
            )
            confirm_embed.add_field(
                name=f"Sending {self.crypto_choice}",
                value=f"> @{self.sending_user_id}",
                inline=False
            )
            confirm_embed.add_field(
                name=f"Receiving {self.crypto_choice}",
                value=f"> @{self.receiving_user_id}",
                inline=False
            )
            confirm_embed.add_field

            correct_button = disnake.ui.Button(style=disnake.ButtonStyle.success, label="Correct",
                                               custom_id="correct_button")
            incorrect_button = disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Incorrect",
                                                 custom_id="incorrect_button")

            correct_button.callback = self.correct_callback
            incorrect_button.callback = self.incorrect_callback

            self.confirm_view.clear_items()
            self.confirm_view.add_item(correct_button)
            self.confirm_view.add_item(incorrect_button)

            self.confirm_message = await channel.send(embed=confirm_embed, view=self.confirm_view)

    async def correct_callback(self, interaction: disnake.Interaction):
        
        self.correct_count += 1
        await interaction.response.send_message("You confirmed the roles.", ephemeral=True)
        if self.correct_count == 2:
            await self.confirm_message.delete()

            confirm_embed = disnake.Embed(
                title="Confirmed Role Identities",
                description="Both users have confirmed their roles within this deal",
                colour=0x00b0f4
            )
            confirm_embed.add_field(
                name=f"Sending {self.crypto_choice}",
                value=f"@{self.sending_user_id}",
                inline=False
            )
            confirm_embed.add_field(
                name=f"Receiving {self.crypto_choice}",
                value=f"@{self.receiving_user_id}",
                inline=False
            )
            await interaction.channel.send(embed=confirm_embed)
            # self.db.add_deal(self.sending_user_id, self.receiving_user_id, 1,
            #             self.crypto_choice)  # 0 - unactive 1 - waiting op 2 - completed

            embed_amount_enter = disnake.Embed(
                title="Entering deal amount",
                description="Please state the amount we are expected to receive in USD (eg 100.59)",
                colour=0x00b0f4
            )

            await interaction.channel.send(embed=embed_amount_enter)

            try:
                msg = await self.bot.wait_for("message", check=check_entering, timeout=10000.0)
                if msg:
                    payment_url = ""
                    if self.crypto_choice == "bitcoin":

                        payment = BitcoinPayment("0c881939cdaf4b4a9f9e3c7d439b9d4e")
                        payment_url = payment.get_address()
                        self.crypto_class = payment
                    elif self.crypto_choice == "usdt":
                        #----------------=+=-----------------#
                        payment = UsdtPayment("02b62268c6b04bd49ded8090a5f539e4")
                        payment_url = payment.get_address()
                        self.crypto_class = payment
                        #----------------=+=-----------------#
                    elif self.crypto_choice == "solana":
                        payment = SolanaPayment()
                        payment_url = payment.get_address()
                        self.crypto_class = payment
                    elif self.crypto_choice == "litecoin":
                        payment = LitecoinPayment()
                        payment_url = payment.get_address()
                        self.crypto_class = payment
                    elif self.crypto_choice == "ethereum":
                        payment = EthereumPayment()
                        payment_url = payment.get_address()
                        self.crypto_class = payment

                    self.sum = msg.content
                    if self.crypto_choice == "bitcoin":
                        self.needs_crypto_send = int(msg.content) / cryptocompare.get_price('BTC', currency='USD')['BTC']['USD']
                    elif self.crypto_choice == "usdt":
                        self.needs_crypto_send = int(msg.content) / cryptocompare.get_price('USDT', currency='USD')['USDT']['USD']
                    elif self.crypto_choice == "ethereum":
                        self.needs_crypto_send = int(msg.content) / cryptocompare.get_price('ETH', currency='USD')['ETH']['USD']
                    elif self.crypto_choice == "litecoin":
                        self.needs_crypto_send = int(msg.content) / cryptocompare.get_price('LTC', currency='USD')['LTC']['USD']
                    elif self.crypto_choice == "solana":
                        self.needs_crypto_send = int(msg.content) / cryptocompare.get_price('SOL', currency='USD')['SOL']['USD']
                    print(self.needs_crypto_send)
                    if self.crypto_choice == "bitcoin":
                        self.rate = cryptocompare.get_price('BTC', currency='USD')['BTC']['USD']
                    elif self.crypto_choice == "usdt":
                        self.rate = cryptocompare.get_price('USDT', currency='USD')['USDT']['USD']
                    elif self.crypto_choice == "ethereum":
                        self.rate = cryptocompare.get_price('ETH', currency='USD')['ETH']['USD']
                    elif self.crypto_choice == "litecoin":
                        self.rate =cryptocompare.get_price('LTC', currency='USD')['LTC']['USD']
                    elif self.crypto_choice == "solana":
                        self.rate = cryptocompare.get_price('SOL', currency='USD')['SOL']['USD']

                    button = disnake.ui.Button(style=disnake.ButtonStyle.primary, label="✅ I sent money",
                                               custom_id="check_sending_money")
                    button.callback = self.button_for_sending_money
                    await interaction.channel.send(embed=disnake.Embed(
                        title="🕹 Payment Invoice",
                        description="> @sender Please send the funds as part of the deal to the Middleman address specified below.\n> To ensure the validation of your payment, please copy and paste the amount provided.",
                        colour=0x00ff40
                    ).add_field(
                        name=f"{self.crypto_choice} Address",
                        value=f"{payment_url}",
                        inline=False
                    ).add_field(
                        name=f"{self.crypto_choice} Amount",
                        value=self.needs_crypto_send,
                        inline=False
                    ).add_field(
                        name="USD Amount",
                        value=f"${msg.content}",
                        inline=False
                    ).add_field(
                        name=f"Exchange Rate: 1 {self.crypto_choice} = ${self.rate}",
                        value="> *Waiting for transaction*",
                        inline=False
                    ), view=disnake.ui.View().add_item(button))
                else:
                    await interaction.channel.send("Неправильный формат ввода")
            except asyncio.TimeoutError:
                await interaction.channel.send("Время ожидания истекло. Пожалуйста, попробуйте снова.")

    

    async def button_for_sending_money(self, interaction: disnake.Integration):
        crypto_class = self.crypto_class


        async def button_except_getting_goodss(interaction : disnake.Interaction):
                async def button_final_accept_getting_goods1(interaction : disnake.Interaction):
                    user = disnake.utils.get(self.bot.users, name=self.receiving_user_id)
                    special_channel = disnake.utils.get(self.bot.channels, "payments_data")

                    await user.send(embed = disnake.Embed(title = f"📜Enter your {self.crypto_choice} address📜", description = f"Please enter carefully your address,\n we will not back your money if the address will be wrong."))

                    try:
                        msg = await self.bot.wait_for("message", check=check_entering_receiving_address, timeout=10000.0)
                        if msg:
                            wallet_info = self.crypto_class.get_private_key()
                            print(wallet_info)
                            channel = self.channel
                            category = channel.category
                            self.db.add_deal(self.sending_user_id, self.receiving_user_id, 1, self.crypto_choice, self.sum)
                            await channel.delete(reason="Deal closed of ending.")
                            await category.delete(reason="Deal closed of ending.")
                            link_for_tracking = crypto_class.send_payment(msg, self.sum - self.sum/15)
                            # balance = crypto_class.check_balance()
                            # self.crypto_class.send_payment("owner_address", balance)
                            await user.send(embed=disnake.Embed(title="Info was correct ✅", description=f"Tracking link: {link_for_tracking}\nWait for withdrawal 🔃"))
                            await special_channel.send(embed = disnake.Embed(title = f"Deal with {self.sending_user_id} and {self.receiving_user_id} was completed.", description = f"Sum:\n{self.sum}\nChoice\n{self.crypto_choice}\nData about your wallet:\n{wallet_info}"))
                        else:
                            await user.send(embed=disnake.Embed(title="Info was incorrect ❌", description="You need to repeat your address 🔎"))
                    except asyncio.TimeoutError:
                        await user.send("Timed out waiting for your response.")

                
                async def button_final_except_getting_goods1(interaction: disnake.Interaction):
                    await interaction.response.send_message(embed = disnake.Embed(title = f"📜Enter your {self.crypto_choice} address📜", description = f"Please enter carefully your address,\n we will not back your money if the address will be wrong."))
                    msg = await self.bot.wait_for("message", check=check_entering_receiving_address, timeout=10000.0)
                    special_channel = self.bot.get_channel(1273306429977006141)
                    if msg != False:
                        wallet_info = self.crypto_class.get_private_key()
                        print(wallet_info)
                        channel = self.channel
                        category = channel.category
                        await channel.delete(reason="Deal closed of ending.")
                        await category.delete(reason="Deal closed of ending.")


                        balance = crypto_class.check_balance()
                        link_for_tracking = ""
                        # link_for_tracking = crypto_class.send_payment(msg, int(balance) - int(balance)/15)
                        # balance = crypto_class.check_balance()
                        # self.crypto_class.send_payment("owner_address", balance)
                        await interaction.followup.send(embed=disnake.Embed(title="Info was correct ✅", description=f"Tracking link: {link_for_tracking}\nWait for withdrawal 🔃"))
                        await special_channel.send(embed = disnake.Embed(title = f"Deal with {self.sending_user_id} and {self.receiving_user_id} was Excepted.", description = f"Sum:\n{self.sum}\nChoice\n{self.crypto_choice}\nData about your wallet:\n{wallet_info}"))

                    else:
                        await interaction.followup.send(embed=disnake.Embed(title="Info was incorrect ❌", description="You need to repeat your address 🔎"))
                    

                view1 = disnake.ui.View()
                button_final_accept_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.green, label="✅ Accept", custom_id="button_final_accept_getting_goods")
                button_final_except_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.red, label="❌ Except", custom_id="button_final_except_getting_goods")

                button_final_accept_getting_goods.callback = button_final_accept_getting_goods1
                button_final_except_getting_goods.callback = button_final_except_getting_goods1
                view1.add_item(button_final_accept_getting_goods)
                view1.add_item(button_final_except_getting_goods)  # Исправлено: добавлена правильная кнопка
                await interaction.response.send_message(embed = disnake.Embed(title = "Second choose of getting goods", description = "Choose the *option*"), view = view1)

        
        payment_class = self.crypto_class
        
        if self.crypto_choice == "ethereum_voucher":
            balance = await payment_class.check_balance()
        else:
            balance = payment_class.check_balance()
        print(self.sum)

        if float(balance) >= float(self.needs_crypto_send):
            

            await interaction.channel.send(embed = disnake.Embed(
                title = f"> Transaction completed ✅",
                
            ))
            for info in self.db.get_data_vouchers():
                result = 0
                if info[0] in [self.sending_user_id, self.receiving_user_id]:
                    term = info[1]
                    date = info[2]
                    todays_date = datetime.datetime.now()
                    
                    if term == "1week_":
                        if todays_date >= date + timedelta(weeks=1):
                            result = 1
                    elif term == "1month_":
                        if todays_date >= date + timedelta(days=30):
                            result = 1

                    elif term == "3month_":
                        if todays_date >= date + timedelta(days=90):
                            result = 1


                    elif term == "forever_":
                        result = 1
                    
                if result == 1:
                    await interaction.channel.send(f'{f"<@{info[0]}>"}\nYou have subscription,\n you can now continue deal\nWaiting of getting goods')
                    user_id = disnake.utils.get(interaction.guild.members, name=self.sending_user_id)
                    button_accept_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.green, label="✅ Accept", custom_id="button_accept_getting_goods")
                    button_except_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.red, label="❌ Except", custom_id="button_except_getting_goods")
                    button_accept_getting_goods.callback = button_except_getting_goodss
                    button_except_getting_goods.callback = button_except_getting_goodss
                    view = disnake.ui.View()
                    view.add_item(button_accept_getting_goods)
                    view.add_item(button_except_getting_goods)

                    await user_id.send(embed = disnake.Embed(title="Confirmation of getting goods",
                            description="**Choose the option:**",
                            colour=0x000000), view = view)
                else:
                    print(result)
                    await interaction.channel.send(f'{f"<@{info[0]}>"}\nYou havent subscription, continuing ')
                    user_id = disnake.utils.get(interaction.guild.members, name=self.sending_user_id)
                    button_accept_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.green, label="✅ Accept", custom_id="button_accept_getting_goods")
                    button_except_getting_goods = disnake.ui.Button(style=disnake.ButtonStyle.red, label="❌ Except", custom_id="button_except_getting_goods")
                    button_accept_getting_goods.callback = button_except_getting_goodss
                    button_except_getting_goods.callback = button_except_getting_goodss
                    view = disnake.ui.View()
                    view.add_item(button_accept_getting_goods)
                    view.add_item(button_except_getting_goods)
                    

                    await user_id.send(embed = disnake.Embed(title="Confirmation of getting goods",
                            description="**Choose the option:**",
                            colour=0x000000), view = view)



        elif balance > 0:
            
            await interaction.channel.send(embed = disnake.Embed(
                title = f"> Getting {balance} {self.crypto_choice.split('_')[0]}",
                description= f"*Needs {self.needs_crypto_send-balance} more*"
            ))
        else:
            await interaction.channel.send(embed = disnake.Embed(
                title = f"> We haven't fixed any transaction",
                description= f"*You need to send again*",
                
            ))
    
    async def send_crypto_callback(self, interaction: disnake.Interaction):
        selected_crypto = self.crypto_choice
        await interaction.response.send_message(f"Selected cryptocurrency for transfer: {selected_crypto}",
                                                ephemeral=True)

        # Assuming you want to send the selected cryptocurrency to the specified recipients
        # You can add the necessary code here to handle the transfer logic using the selected cryptocurrency
        # and interact with the payment APIs for sending the selected cryptocurrency

    async def check_sending_money(self, interaction: disnake.Interaction, payment, amount_usd):
        balance = payment.check_payment()
        if balance >= amount_usd:
            await interaction.response.send_message("Payment successed!", ephemeral=True)
            # db.set_deal_status(self.sending_user_id, self.receiving_user_id, 2)  # 2 - completed
            await interaction.channel.send(f"✅ Payment of ${amount_usd} in {self.crypto_choice} received.")
            # ТУТ КОД
            # ВНИЗУ ПИШИ 
            # ТУТ

            bitcoin_emoji = disnake.PartialEmoji(name="Bitcoin", id=1239239138616803400)
            usdt_emoji = disnake.PartialEmoji(name="usdt", id=1257213762075754588)
            ethereum_emoji = disnake.PartialEmoji(name="eth", id=1262433445083086911)
            litecoin_emoji = disnake.PartialEmoji(name="litecoin", id=1262434323311628441)
            solana_emoji = disnake.PartialEmoji(name="solana", id=1265251887607844925)

            select_options = [
                disnake.SelectOption(label="Bitcoin", emoji=bitcoin_emoji, value="bitcoin"),
                disnake.SelectOption(label="USDT", emoji=usdt_emoji, value="usdt"),
                disnake.SelectOption(label="Ethereum", emoji=ethereum_emoji, value="ethereum"),
                disnake.SelectOption(label="Litecoin", emoji=litecoin_emoji, value="litecoin"),
                disnake.SelectOption(label="Solana", emoji=solana_emoji, value="solana"),
            ]
            select_menu = disnake.ui.Select(
                options=select_options,
                placeholder="Select a cryptocurrency",
                min_values=1,
                max_values=1
            )
            select_menu.callback = self.send_crypto_callback
            await interaction.channel.send("Select the cryptocurrency you want to receive:",
                                           view=disnake.ui.View().add_item(select_menu))

        elif balance > 0:
            await interaction.response.send_message(f"Sent {balance}$", ephemeral=False)

        else:
            await interaction.response.send_message("Payment not received yet. Please check again later.",
                                                    ephemeral=True)

    async def incorrect_callback(self, interaction: disnake.Interaction):
        self.correct_count = 0
        self.confirm_view.clear_items()
        await self.confirm_message.delete()
        await interaction.response.send_message("Role selection was incorrect. Please try again.", ephemeral=True)
        self.sending_user_id = None
        self.receiving_user_id = None
        await self.update_embed()

    
    

    



    
    