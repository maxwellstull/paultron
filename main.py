import discord
import datetime
from secret_token import Token
from classes import Application


intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)
appy = Application()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    appy.load_json()

async def read_channel(channel, itr_date=None):
     # get first ever message
    current_date = datetime.datetime.now(tz=datetime.UTC)
    if itr_date is None:
        async for message in channel.history(limit=1, oldest_first=True):
            itr_date = message.created_at - datetime.timedelta(days=1)
    if itr_date is not None:
        messages = []
        while itr_date <= current_date:
            next_date = itr_date + datetime.timedelta(weeks=4)
            print("Searching " + (channel.category.name if channel.category else "/") + "/" + channel.name + " for " + itr_date.strftime("%m/%d/%Y") + " to " + next_date.strftime("%m/%d/%Y"))
            async for message in channel.history(limit=None, after=itr_date, before=next_date):
                messages.append(message)
            itr_date = next_date
    return messages

async def traverse(guild):
    # Iterate over channels
    for channel in guild.channels:
        # Check if text channel
        if type(channel) == discord.TextChannel:
            # Add text channel to server object if not there (ie first time traversing)
            if channel.id not in appy.servers[str(guild.id)].channels:
                appy.servers[str(guild.id)].add_channel(channel)
            # Get all messages, update last traversal, with a generous overlap in case 
            messages = await read_channel(channel, appy.servers[str(guild.id)].channels[str(channel.id)].last_traversal)
            appy.servers[str(guild.id)].channels[str(channel.id)].last_traversal = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=1)

            for message in messages:
                # Add user to recording data
                if str(message.author.id) not in appy.servers[str(message.guild.id)].users:
                    await add_user(message)    
                appy.servers[str(guild.id)].users[str(message.author.id)].messages.append(message.id)

                # Count user yaps
                if str(message.author.id) not in appy.servers[str(message.guild.id)].channels[str(message.channel.id)].yappers:
                    appy.servers[str(message.guild.id)].channels[str(message.channel.id)].yappers[str(message.author.id)] = 1
                else:
                    appy.servers[str(message.guild.id)].channels[str(message.channel.id)].yappers[str(message.author.id)] += 1

                # Count reactions on message
                if message.reactions:
                    for reaction in message.reactions:
                        value = None
                        if isinstance(reaction.emoji, str):
                            value = reaction.emoji
                        else:
                            value = reaction.emoji.id
                        users = [user async for user in reaction.users()]
                        for user in users:
                            if value not in appy.servers[str(message.guild.id)].reacters[str(user.id)]:
                                appy.servers[str(message.guild.id)].reacters[str(user.id)][value] = 1
                            else:
                                appy.servers[str(message.guild.id)].reacters[str(user.id)][value] += 1

                            if value not in appy.servers[str(message.guild.id)].users[str(user.id)].reactions:
                                appy.servers[str(message.guild.id)].users[str(user.id)].reactions[value] = 1
                            else:
                                appy.servers[str(message.guild.id)].users[str(user.id)].reactions[value] += 1

async def audit_yaps(channel):
    total_yaps = appy.servers[str(channel.guild.id)].summarize_yaps()
    sorted_yaps = sorted(total_yaps.keys(), key= lambda k: total_yaps[k], reverse=True)

    member_objs = {str(member.id) : member async for member in channel.guild.fetch_members()}

    
    await channel.send("""
Yapper Leaderboard for {name}
                       
1st - {first} with {ct1} yaps
2nd - {second} with {ct2} yaps
3rd - {third} with {ct3} yaps
                       
                       """.format(name=appy.servers[str(channel.guild.id)].name,
                       first=member_objs[sorted_yaps[0]].display_name, ct1=total_yaps[sorted_yaps[0]],
                       second=member_objs[sorted_yaps[1]].display_name, ct2=total_yaps[sorted_yaps[1]],
                       third=member_objs[sorted_yaps[2]].display_name, ct3=total_yaps[sorted_yaps[2]],
                       
                       ))

async def audit_reactions(channel):
    total_emoji = appy.servers[str(channel.guild.id)].summarize_reactions()
    sorted_emoji = sorted(total_emoji.keys(), key= lambda k: total_emoji[k], reverse=True)

    
    await channel.send("""
Yapper Leaderboard for {name}
                       
1st - {first} with {ct1} yaps
2nd - {second} with {ct2} yaps
3rd - {third} with {ct3} yaps
                       
                       """.format(name=appy.servers[str(channel.guild.id)].name,
                       first=sorted_emoji[0], ct1=total_emoji[sorted_emoji[0]],
                       second=sorted_emoji[1], ct2=total_emoji[sorted_emoji[1]],
                       third=sorted_emoji[2], ct3=total_emoji[sorted_emoji[2]],
                       
                       ))





async def add_server(guild):
    appy.add_server(guild.id)
    appy.servers[str(guild.id)].name = guild.name
    async for member in guild.fetch_members():
        await add_user(guild, member)
        print("adding user", member)

                        
async def add_user(guild, member):
    appy.servers[str(guild.id)].add_user(member)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    if str(message.guild.id) not in appy.servers:
        await add_server(message.guild)
        print("Adding server and all members")
    if message.content.startswith('$save'):
        appy.save_json()
    if message.content.startswith('$traverse'):
        await traverse(message.guild)
    if message.content.startswith('$audit_yaps'):
        await audit_yaps(message.channel)
    if message.content.startswith('$audit_emoji'):
        await audit_reactions(message.channel)

        
client.run(Token().token)