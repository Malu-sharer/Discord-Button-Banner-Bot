# -*- coding: utf-8 -*-
from discord import user
from discord_components import DiscordComponents, ComponentsBot, Button, ButtonStyle, ActionRow
import discord, sqlite3, datetime, randomstring, os
import asyncio, requests, json
from datetime import timedelta
from discord_webhook import DiscordEmbed, DiscordWebhook
from discord_buttons_plugin import ButtonType
import setting


token = setting.token

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

sta = setting.sangma

owner = [727340196131118611] #관리자아이디 넣으새요

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

@client.event
async def on_ready():
    DiscordComponents(client)
    print(" ")
    print("봇 작동중")
    print(" ")
    while True:
        game = discord.Game(sta)
        await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith('$생성 '):
        if message.author.id in owner:
            if not isinstance(message.channel, discord.channel.DMChannel):
                try:
                    amount = int(message.content.split(" ")[1])
                except:
                    await message.channel.send("올바른 생성 갯수를 입력해주세요.")
                    return
                if 1 <= amount <= 30:
                    try:
                        license_length = int(message.content.split(" ")[2])
                    except:
                        await message.channel.send("올바른 생성 기간을 입력해주세요.")
                        return
                    codes = []
                    for _ in range(amount):
                        code = "VBanner-" + randomstring.pick(20)
                        codes.append(code)
                        con = sqlite3.connect("./db/" + "license.db")
                        cur = con.cursor()
                        cur.execute("INSERT INTO license Values(?, ?, ?, ?, ?);", (code, license_length, 0, "None", 0))
                        con.commit()
                        con.close()
                    await message.channel.send(embed=discord.Embed(title="생성 성공", description="디엠을 확인해주세요.", color=0x5c6cdf))
                    await message.author.send("\n".join(codes))

    if message.content.startswith("$등록 "):
        if message.author.guild_permissions.administrator or message.author.id in owner:
            license_key = message.content.split(" ")[1]
            con = sqlite3.connect("./db/" + "license.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
            search_result = cur.fetchone()
            con.close()
            if (search_result != None):
                if (search_result[2] == 0):
                    if not (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                        con = sqlite3.connect("./db/" + str(message.guild.id) + ".db")
                        cur = con.cursor()
                        cur.execute("CREATE TABLE serverinfo (id TEXT, expiredata TEXT, mid TEXT, role TEXT, caid INTEGER, adname TEXT, result TEXT);")
                        con.commit()
                        cur.execute("INSERT INTO serverinfo VALUES(?, ?, ?, ?, ?, ?, ?)", (message.guild.id, make_expiretime(int(sqlite3.connect("./db/" + "license.db").cursor().execute("SELECT * FROM license WHERE code == ?;", (license_key,)).fetchone()[1])), "", "", "", "", ""))
                        con.commit()
                        con.close()    
                        con = sqlite3.connect("./db/" + "license.db")
                        cur = con.cursor()
                        cur.execute("UPDATE license SET isused = ?, useddate = ?, usedby = ? WHERE code == ?;", (1, nowstr(), message.guild.id, license_key))
                        con.commit()
                        con.close()
                        con = sqlite3.connect("./db/" + "license.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM license WHERE code == ?;", (license_key,))
                        await message.channel.send(embed=discord.Embed(title="서버 등록 성공", description="서버가 성공적으로 등록되었습니다.", color=0x5c6cdf))
                        con.close()
                    else:
                        await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 등록된 서버이므로 등록할 수 없습니다.", color=0x5c6cdf))
                else:
                    await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="이미 사용된 라이센스입니다.\n관리자에게 문의해주세요.", color=0x5c6cdf))
            else:
                await message.channel.send(embed=discord.Embed(title="서버 등록 실패", description="존재하지 않는 라이센스입니다.", color=0x5c6cdf))


    if message.content == "$카테고리아이디":
        await message.channel.send(message.channel.category.id)

    if message.content == "$명령어":
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                await message.channel.send(embed=discord.Embed(title="명령어 목록", description="&결과채널 : 배너를 개설한 후 정보를 해당채널에 전송합니다.\n&카테고리 (카테고리ID) : 배너채널이 개설되는 카테고리를 지정합니다.\n&배너명 (이름) : 배너를 개설할때 상대의 서버에서 만들 채널의 이름을 정합니다.\n$배너조건 : 배너조건을 등록합니다.\n$카테고리아이디 : 해당 채널의 카테고리 아이디를 전송합니다.", color=0x5c6cdf))
                return

    if message.content == "$배너":
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                try:
                    await message.delete()
                except:
                    pass
                embed = discord.Embed(title="자동 배너 개설 안내", description='배너를 신청하시려면 아래\n원하시는 버튼을 클릭해주세요.', color=0x5c6cdf)
                await message.channel.send(
                    embed=embed,
                    components = [
                        ActionRow(
                            Button(style=ButtonStyle.blue,label = "배너조건",custom_id="조건"),
                            Button(style=ButtonStyle.blue,label = "배너신청",custom_id="신청"),
                        )
                    ]
                )

    if message.content.startswith("$결과채널"):
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                con = sqlite3.connect("./db/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET result = ?",(message.channel.id,))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="채널 지정 성공", description="해당 채널에 배너개설 정보가 출력됩니다.", color=0x5c6cdf))
        

    if message.content.startswith("$카테고리 "):
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                categoryid = message.content.split(" ")[1]
                con = sqlite3.connect("./db/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET caid = ?",(categoryid,))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="카테고리 지정 성공", description="해당 카테고리에 배너채널이 생성됩니다.", color=0x5c6cdf))
                return
        
        
    
    if message.content.startswith("$배너명 "):
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                bannername = message.content.split(" ")[1]
                con = sqlite3.connect("./db/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET adname = ?",(bannername,))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="배너명 지정 성공", description=f"배너를 만들때 '{bannername}`이(가) `{message.author.guild.name}` 서버의 배너채널 이름으로 설정되었습니다.", color=0x5c6cdf))
                return

    if message.content == "$배너조건":
        if message.author.guild_permissions.administrator or message.author.id in owner:
            if (os.path.isfile("./db/" + str(message.guild.id) + ".db")):
                await message.channel.send(embed=discord.Embed(title="배너조건 변경", description="배너조건을 입력해주세요.",color=0x010101))
                def check(role):
                    return (role.author.id == message.author.id)
                role = await client.wait_for("message", timeout=60, check=check)
                role = role.content
                con = sqlite3.connect("./db/" + str(message.guild.id) +".db")
                cur = con.cursor()
                cur.execute("UPDATE serverinfo SET role = ?",(role,))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="변경 성공", description=f"성공적으로 배너조건이 변경되었습니다..",color=0x010101))
            else:
                await message.channel.send(embed=discord.Embed(title="변경 실패", description="오류가 발생했습니다. 처음부터 다시 시도해주세요.",color=0x010101))

@client.event
async def on_button_click(interaction):
    if not isinstance(interaction.channel, discord.channel.DMChannel):
        if (os.path.isfile("./db/" + str(interaction.guild.id) + ".db")):
            con = sqlite3.connect("./db/" + str(interaction.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            cmdchs = cur.fetchone()
            con.close()
            try:
                tempvar = is_expired(cmdchs[1])
            except:
                os.rename("./db/" + str(interaction.guild.id) + ".db", "./db/" + str(interaction.guild.id) + f".db_old{datetime.datetime.now()}")
            if not(is_expired(cmdchs[1])):
                if interaction.responded:
                    return

        if interaction.custom_id == "조건":
            con = sqlite3.connect("./db/" + str(interaction.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            server_info = cur.fetchone()
            bannerrole = server_info[3]
            con.close()
            if server_info[3] != "서버정보":
                await interaction.respond(embed=discord.Embed(title="배너조건", description=f"{bannerrole}", color=0x5c6cdf))
            else:
                await interaction.respond(embed=discord.Embed(title="배너조건", description="배너 조건이 없으나 6시간 마다 한번 씩 직접 작성 해주셔야 합니다.\n※ 해당 내용 어길 시 아래와 같이 처벌이 이루어 집니다.\n\n1차 통보 후 메세지 삭제\n2차 무통보 채널 삭제", color=0x5c6cdf))

        if interaction.custom_id == "신청":
            nam = await interaction.user.send(embed=discord.Embed(title="배너신청", description="개설할 배너의 이름을 60초 안에 입력해주세요.", color=0x5c6cdf))
            await interaction.respond(embed=discord.Embed(title="신청 성공", description="디엠을 확인해주세요.", color=0x5c6cdf))
            def check(nacon):
                return (isinstance(nacon.channel, discord.channel.DMChannel) and (interaction.user.id == nacon.author.id))
            try:
                nacon = await client.wait_for("message", timeout=60, check=check)
                await nam.delete()
            except asyncio.TimeoutError:
                try:
                    await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="시간 초과되었습니다. 다시 시도해주세요.", color=0x5c6cdf))
                except:
                    pass
                return None
            if nacon.content == None:
                await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="오류가 발생했습니다. 다시 시도해주세요.", color=0x5c6cdf))
            else:
                con = sqlite3.connect("./db/" + str(interaction.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo")
                server_info = cur.fetchone()
                caid = server_info[4]
                con.close()

                cn = await interaction.user.guild.create_text_channel(name='『💠』：' + str(nacon.content), category=interaction.user.guild.get_channel(int(caid)))
                await asyncio.sleep(1)
                await interaction.user.send(embed=discord.Embed(title="채널 생성 성공", description=f"<#{cn}> 채널이 생성되었습니다.", color=0x5c6cdf))
                await cn.send(interaction.user.mention + "님이 생성하신 배너입니다.")
            try:
                li = await interaction.user.send(embed=discord.Embed(title="배너신청", description="자신의 서버 영구초대링크를 60초안에 입력해주세요.", color=0x5c6cdf))
                def check(incon):
                    return (isinstance(incon.channel, discord.channel.DMChannel) and (interaction.user.id == incon.author.id))
            except:
                pass
            try:
                incon = await client.wait_for("message", timeout=60, check=check)
                await li.delete()
            except asyncio.TimeoutError:
                try:
                    await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="시간 초과되었습니다. 다시 시도해주세요.", color=0x5c6cdf))
                    await cn.delete()
                except:
                    pass
                return None
            else:
                con = sqlite3.connect("./db/" + str(interaction.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo")
                server_info = cur.fetchone()
                adname = server_info[5]
                con.close()
            try:
                wh = await interaction.user.send(embed=discord.Embed(title="배너 신청", description=f"자신의 서버에 '{server_info[5]}' 라는 이름의 채널을 만들고 웹훅을 입력해주세요. ( 제한시간 5분 )", color=0x5c6cdf))
                def check(webcon):
                    return (isinstance(webcon.channel, discord.channel.DMChannel) and (interaction.user.id == webcon.author.id))
            except:
                pass
            try:
                webcon = await client.wait_for("message", timeout=300, check=check)
                await wh.delete()
            except asyncio.TimeoutError:
                try:
                    await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="시간 초과되었습니다. 다시 시도해주세요.", color=0x5c6cdf))
                    await cn.delete()
                except:
                    pass
                return None
            hook=webcon.content
            if "api/webhooks" in hook:
                hdr = {'User-Agent': 'Mozilla/5.0'}

                json = requests.get(hook, headers=hdr).json()
                try:
                    temp = json.get("token")
                except:
                    await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="잘못된 웹훅입니다. 다시 시도해주세요.", color=0x5c6cdf))
                    await cn.delete()
                    return

                if temp is None:
                    await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="잘못된 웹훅입니다. 다시 시도해주세요.", color=0x5c6cdf))
                    await cn.delete()
                    return
            if not "api/webhooks" in hook:
                await interaction.user.send(embed=discord.Embed(title="배너 신청 실패", description="잘못된 웹훅입니다. 다시 시도해주세요.", color=0x5c6cdf))
                await cn.delete()
                return
            
            web = await cn.create_webhook(name=interaction.user, reason='banner')

            await interaction.user.send(embed=discord.Embed(title="배너 신청 성공", description="웹훅 생성이 완료되었습니다.", color=0x5c6cdf))
            await interaction.user.send(f"{web.url}")

            con = sqlite3.connect("./db/" + str(interaction.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo")
            server_info = cur.fetchone()
            result = server_info[6]
            con.close()
            resultsend = discord.Embed(title=f"{interaction.user}님이 배너를 개설하였습니다.", description=f"개설 유저: {interaction.user.mention}\n개설한 배너: {nacon.content}\n서버주소: {incon.content}\n받은 웹훅: {webcon.content}", color=0x5c6cdf)
            await client.get_channel(int(server_info[6])).send(webcon.content, embed=resultsend)

client.run(token)
