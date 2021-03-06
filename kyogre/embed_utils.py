import copy
import datetime
import discord

from kyogre import utils
from kyogre.exts.pokemon import Pokemon


async def get_embed_field_indices(embed):
    index = 0
    embed_indices = {"gym": None,
                    "possible": None,
                    "interest": None,
                    "next": None,
                    "hatch": None,
                    "expires": None,
                    "status": None,
                    "team": None,
                    "details": None,
                    "weak": None,
                    "maybe": None,
                    "coming": None,
                    "here": None,
                    "tips": None,
                    "directions": None
                    }
    for field in embed.fields:
        if "gym" in field.name.lower():
            embed_indices["gym"] = index
        if "possible" in field.name.lower():
            embed_indices["possible"] = index
        if "interest" in field.name.lower():
            embed_indices["interest"] = index
        if "next" in field.name.lower():
            embed_indices["next"] = index
        if "hatch" in field.name.lower():
            embed_indices["hatch"] = index
        if "expires" in field.name.lower():
            embed_indices["expires"] = index
        if "status" in field.name.lower():
            embed_indices["status"] = index
        if "team" in field.name.lower():
            embed_indices["team"] = index
        if "details" in field.name.lower():
            embed_indices["details"] = index
        if "weak" in field.name.lower():
            embed_indices["weak"] = index
        if "tips" in field.name.lower():
            embed_indices["tips"] = index
        if "maybe" in field.name.lower():
            embed_indices["maybe"] = index
        if "coming" in field.name.lower():
            embed_indices["coming"] = index
        if "here" in field.name.lower():
            embed_indices["here"] = index
        if "directions" in field.name.lower():
            embed_indices["directions"] = index
        # if "" in field.name.lower():
        #     embed_indices[""] = index
        index += 1
    return embed_indices


async def filter_fields_for_report_embed(embed, embed_indices, enabled):
    new_embed = copy.deepcopy(embed)
    new_embed.clear_fields()
    if embed_indices['gym'] is not None:
        new_embed.add_field(name=embed.fields[embed_indices['gym']].name, value=embed.fields[embed_indices['gym']].value, inline=True) 
    if embed_indices['hatch'] is not None:
        new_embed.add_field(name=embed.fields[embed_indices['hatch']].name, value=embed.fields[embed_indices['hatch']].value, inline=True) 
    if embed_indices['expires'] is not None:
        new_embed.add_field(name=embed.fields[embed_indices['expires']].name, value=embed.fields[embed_indices['expires']].value, inline=True)
    if embed_indices['team'] is not None:
        new_embed.add_field(name=embed.fields[embed_indices['team']].name, value=embed.fields[embed_indices['team']].value, inline=True)
    if embed_indices['status'] is not None:
        new_embed.add_field(name=embed.fields[embed_indices['status']].name, value=embed.fields[embed_indices['status']].value, inline=True)
    if not enabled:
        if embed_indices['directions'] is not None:
            new_embed.add_field(name=embed.fields[embed_indices['directions']].name, value=embed.fields[embed_indices['directions']].value, inline=True)
    return new_embed


async def build_raid_embeds(kyogre, ctx, raid_dict, enabled, assume=False):
    guild = ctx.guild
    author = raid_dict.get('reporter', None)
    if author:
        author = guild.get_member(author)
    utils_cog = kyogre.cogs.get('Utilities')
    location_matching_cog = kyogre.cogs.get('LocationMatching')
    ctype = raid_dict['type']
    raid_embed = discord.Embed(colour=guild.me.colour)
    gym = location_matching_cog.get_gym_by_id(guild.id, raid_dict['gym'])
    if gym:
        gym_info = f"**{gym.name}**\n{'_EX Eligible Gym_' if gym.ex_eligible else ''}"
        if gym.note is not None:
            gym_info += f"\n**Note**: {gym.note}"
        raid_embed.add_field(name='**Gym:**', value=gym_info, inline=False)
        raid_gmaps_link = gym.maps_url
        waze_link = utils_cog.create_waze_query(gym.latitude, gym.longitude)
        apple_link = utils_cog.create_applemaps_query(gym.latitude, gym.longitude)
        raid_embed.add_field(name='Directions',
                             value=f'[Google]({raid_gmaps_link}) | [Waze]({waze_link}) | [Apple]({apple_link})',
                             inline=False)
    if raid_dict['exp']:
        end = datetime.datetime.utcfromtimestamp(raid_dict['exp']) + datetime.timedelta(
            hours=kyogre.guild_dict[guild.id]['configure_dict']['settings']['offset'])
        exp_msg = f"{end.strftime('%I:%M %p')}"
    else:
        exp_msg = "Set with **!timerset**"
    if ctype == 'raid' or assume:
        raid_pokemon = raid_dict['pokemon']
        pkmn = Pokemon.get_pokemon(kyogre, raid_pokemon)
        if enabled:
            min_cp, max_cp = pkmn.get_raid_cp_range(False)
            bmin_cp, bmax_cp = pkmn.get_raid_cp_range(True)
            cp_range = f"**CP Range:** {min_cp}-{max_cp}\n **Boosted:** {bmin_cp}-{bmax_cp}"
            weak_str = utils.types_to_str(guild, pkmn.weak_against.keys(), kyogre.config)
            raid_embed.add_field(name='**Details:**', value='**{pokemon}** ({pokemonnumber}) {type}{cprange}'
                                 .format(pokemon=str(pkmn),
                                         pokemonnumber=str(pkmn.id),
                                         type=utils.types_to_str(guild, pkmn.types, kyogre.config),
                                         cprange='\n' + cp_range,
                                         inline=True))
            raid_embed.add_field(name='**Weaknesses:**', value='{weakness_list}'.format(weakness_list=weak_str))
            raid_embed.add_field(name='**Next Group:**', value='Set with **!starttime**')
            if assume:
                raid_embed.add_field(name='**Hatches:**', value=exp_msg)
            else:
                raid_embed.add_field(name='**Expires:**', value=exp_msg)
        raid_img_url = pkmn.img_url
    else:
        egg_info = kyogre.raid_info['raid_eggs'][str(raid_dict['egglevel'])]
        egg_img = egg_info['egg_img']
        boss_list = []
        for entry in egg_info['pokemon']:
            p = Pokemon.get_pokemon(kyogre, entry)
            boss_list.append(str(p) + utils.types_to_str(guild, p.types, kyogre.config))
        if enabled:
            raid_embed.add_field(name='**Next Group:**', value='Set with **!starttime**', inline=True)
            raid_embed.add_field(name='**Hatches:**', value=exp_msg, inline=True)
            raid_embed.add_field(name='**Possible Bosses:**', value='{bosslist}'
                                      .format(bosslist='\n'.join(boss_list)), inline=True)
            # if len(egg_info['pokemon']) > 1:
            #     raid_embed.add_field(name='**Possible Bosses:**', value='{bosslist1}'
            #                          .format(bosslist1='\n'.join(boss_list[::2])), inline=True)
            #     raid_embed.add_field(name='\u200b', value='{bosslist2}'
            #                          .format(bosslist2='\n'.join(boss_list[1::2])), inline=True)
            # else:
            #     raid_embed.add_field(name='**Possible Bosses:**', value='{bosslist}'
            #                          .format(bosslist=''.join(boss_list)), inline=True)
            #     raid_embed.add_field(name='\u200b', value='\u200b', inline=True)

        raid_img_url = 'https://raw.githubusercontent.com/klords/Kyogre/master/images/eggs/{}?cache=0' \
            .format(str(egg_img))
    if enabled:
        timestamp = (ctx.message.created_at + datetime.timedelta(
            hours=kyogre.guild_dict[guild.id]['configure_dict']['settings']['offset'])).strftime(
            '%I:%M %p (%H:%M)')
        if author:
            raid_embed.set_footer(text='Reported by {author} - {timestamp}'
                                  .format(author=author.display_name, timestamp=timestamp),
                                  icon_url=author.avatar_url_as(format=None, static_format='jpg', size=32))
        raid_embed.add_field(name='**Tips:**',
                             value='`!i` if interested\n`!c` if on the way\n`!h` '
                                   'when you arrive\n`!x` to cancel your status\n'
                                   "`!s` to signal lobby start\n`!shout` to ping raid party",
                             inline=True)
    raid_embed.set_thumbnail(url=raid_img_url)
    report_embed = raid_embed
    embed_indices = await get_embed_field_indices(report_embed)
    report_embed = await filter_fields_for_report_embed(report_embed, embed_indices, enabled)
    return report_embed, raid_embed
