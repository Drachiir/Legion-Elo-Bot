import requests
import json
from collections import Counter
import pathlib
from pathlib import Path
import datetime
import os
import glob
import re
import PIL
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from imgurpython import ImgurClient
import numpy as np

with open('Files/Secrets.json') as f:
    secret_file = json.load(f)
    header = {'x-api-key': secret_file.get('apikey')}
    imgur_client = ImgurClient(secret_file.get('imgur'), secret_file.get('imgurcs'))

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def im_has_alpha(img_arr):
    h,w,c = img_arr.shape
    return True if c ==4 else False

def create_image_mmstats(dict, ranked_count, playerid, avgelo, patch):
    if playerid != 'all':
        playername = apicall_getprofile(playerid)['playerName']
        avatar = apicall_getprofile(playerid)['avatarUrl']
    else:
        playername = 'All'
    def calc_wr(dict, mm):
        try:
            return str(round(dict[mm]['Wins']/dict[mm]['Count'] * 100, 1))
        except ZeroDivisionError as e:
            return '0'
    def calc_pr(dict, mm):
        try:
            return str(round(dict[mm]['Count'] / ranked_count * 100, 1))
        except ZeroDivisionError as e:
            return '0'
    def most_common(dict, mm):
        try:
            data = Counter(dict[mm]['Opener'])
            data2 = Counter(dict[mm]['Spell'])
            return [data.most_common(1)[0][0], data2.most_common(1)[0][0]]
        except IndexError as e:
            return 'No data'
    def get_open_wrpr(dict, mm):
        wins = 0
        count = 0
        for i, x in enumerate(dict[mm]['Opener']):
            if most_common(dict, mm)[0] in x:
                count += 1
                if dict[mm]['Results'][i] == 'won':
                    wins += 1
        try:
            return [count, round(wins / count * 100, 1), round(count / dict[mm]['Count'] * 100, 1)]
        except ZeroDivisionError as e:
            return '000'
    def get_w10(dict, i):
        try:
            return round(dict[i]['W10'] / dict[i]['Count'], 1)
        except ZeroDivisionError as e:
            return '0'
    def get_spell_wrpr(dict, mm):
        wins = 0
        count = 0
        for i, x in enumerate(dict[mm]['Spell']):
            if most_common(dict, mm)[1] in x:
                count += 1
                if dict[mm]['Results'][i] == 'won':
                    wins += 1
        try:
            return [count, round(wins / count * 100, 1), round(count / dict[mm]['Count'] * 100, 1)]
        except ZeroDivisionError as e:
            return '000'
    keys = ['Games:', 'Winrate:', 'Pickrate:', 'W on 10:', 'Open:', '', 'Games:', 'Winrate:', 'Playrate:', 'Spells:', '', 'Games:', 'Winrate:', 'Playrate:']
    url = 'https://cdn.legiontd2.com/icons/Items/'
    url2 = 'https://cdn.legiontd2.com/icons/'
    im = PIL.Image.new(mode="RGB", size=(1070, 875), color=(49,51,56))
    im2 = PIL.Image.new(mode="RGB", size=(88, 800), color=(25,25,25))
    im3 = PIL.Image.new(mode="RGB", size=(1040, 4), color=(169, 169, 169))
    I1 = ImageDraw.Draw(im)
    ttf = 'Files/RobotoCondensed-Regular.ttf'
    myFont_small = ImageFont.truetype(ttf, 20)
    myFont = ImageFont.truetype(ttf, 25)
    myFont_title = ImageFont.truetype(ttf, 30)
    if playername == 'All':
        string = ''
    else:
        string = "'s"
        avatar_url = 'https://cdn.legiontd2.com/' + avatar
        avatar_response = requests.get(avatar_url)
        av_image = Image.open(BytesIO(avatar_response.content))
        gold_border = Image.open('Files/gold_64.png')
        if im_has_alpha(np.array(av_image)):
            im.paste(av_image, (24, 100), mask=av_image)
        else:
            im.paste(av_image, (24, 100))
        im.paste(gold_border, (24, 100), mask=gold_border)
    I1.text((10, 15), str(playername)+string+" Mastermind stats (From "+str(ranked_count)+" ranked games, Avg elo: "+str(avgelo)+")", font=myFont_title, stroke_width=2, stroke_fill=(0,0,0), fill=(255, 255, 255))
    I1.text((10, 55), 'Patches: ' + ', '.join(patch), font=myFont_small, stroke_width=2, stroke_fill=(0,0,0), fill=(255, 255, 255))
    x = 126
    y = 220
    for i in dict:
        im.paste(im2, (x-12, 88))
        url_new = url + i + '.png'
        response = requests.get(url_new)
        mm_image = Image.open(BytesIO(response.content))
        im.paste(mm_image, (x, 100))
        if i == 'CashOut':
            I1.text((x-10, 175), i, font=myFont, fill=(255, 255, 255))
        else:
            I1.text((x, 175), i, font=myFont, fill=(255, 255, 255))
        I1.text((x, 220), str(dict[i]['Count']), font=myFont, fill=(255, 255, 255))
        I1.text((x, 270), str(calc_wr(dict, i))+'%', font=myFont, fill=(255, 255, 255))
        I1.text((x, 320), str(calc_pr(dict, i))+'%', font=myFont, fill=(255, 255, 255))
        I1.text((x, 370), str(get_w10(dict, i)), font=myFont, fill=(255, 255, 255))
        I1.text((x, 500), str(get_open_wrpr(dict, i)[0]), font=myFont, fill=(255, 255, 255))
        I1.text((x, 550), str(get_open_wrpr(dict, i)[1])+'%', font=myFont, fill=(255, 255, 255))
        I1.text((x, 600), str(get_open_wrpr(dict, i)[2])+'%', font=myFont, fill=(255, 255, 255))
        I1.text((x, 730), str(get_spell_wrpr(dict, i)[0]), font=myFont, fill=(255, 255, 255))
        I1.text((x, 780), str(get_spell_wrpr(dict, i)[1]) + '%', font=myFont, fill=(255, 255, 255))
        I1.text((x, 830), str(get_spell_wrpr(dict, i)[2]) + '%', font=myFont, fill=(255, 255, 255))
        url_new = url2 + str(most_common(dict, i)[0]).replace(' ', '') + '.png'
        if url_new == 'https://cdn.legiontd2.com/icons/N.png':
            url_new = 'https://cdn.legiontd2.com/icons/Secret/SadHopper.png'
        response = requests.get(url_new)
        unit_image = Image.open(BytesIO(response.content))
        im.paste(unit_image, (x, 420))
        url_new = url2 + str(most_common(dict, i)[1]).replace(' ', '') + '.png'
        if 'none' in url_new:
            url_new = 'https://cdn.legiontd2.com/icons/Granddaddy.png'
        if url_new == 'https://cdn.legiontd2.com/icons/PresstheAttack.png':
            url_new = 'https://cdn.legiontd2.com/icons/PressTheAttack.png'
        if url_new == 'https://cdn.legiontd2.com/icons/o.png':
            url_new = 'https://cdn.legiontd2.com/icons/Secret/HermitHas0Friends.png'
        response = requests.get(url_new)
        spell_image = Image.open(BytesIO(response.content))
        im.paste(spell_image, (x, 650))
        x += 106
    for k in keys:
        if (k != 'Open:') and (k != 'Spells:') and (k != ''):
            im.paste(im3, (10, y+30))
        I1.text((10, y), k, font=myFont, stroke_width=2, stroke_fill=(0,0,0), fill=(255, 255, 255))
        if (k != 'Open:') and (k != 'Spells:') and (k != ''):
            y += 50
        else:
            y += 40
    im.save('Files/output.png')
    image_upload = imgur_client.upload_from_path('Files/output.png')
    print('Uploading output.png to Imgur...')
    return image_upload['link']

def create_image_unitstats(dict, games, playerid, avgelo, patch):
    if playerid != 'all':
        playername = apicall_getprofile(playerid)['playerName']
        avatar = apicall_getprofile(playerid)['avatarUrl']
    else:
        playername = 'All'
    def calc_wr(dict, unit):
        try:
            return str(round(dict[unit]['OpenWins']/dict[unit]['Count'] * 100, 1))
        except ZeroDivisionError as e:
            return '0'
    def calc_pr(dict, unit):
        try:
            return str(round(dict[unit]['Count'] / games * 100, 1))
        except ZeroDivisionError as e:
            return '0'
    def get_w10(dict, i):
        try:
            return round(dict[i]['W4'] / dict[i]['Count'], 1)
        except ZeroDivisionError as e:
            return '0'
    keys = ['Games:', 'Winrate:', 'Playrate:', 'W on 4:', 'Best add:', '', 'Games:', 'Winrate:', 'Playrate:', 'Best MMs:','', 'Games:', 'Winrate:', 'Playrate:', 'Best\nSpells:','', 'Games:', 'Winrate:', 'Playrate:']
    url = 'https://cdn.legiontd2.com/icons/Items/'
    url2 = 'https://cdn.legiontd2.com/icons/'
    im = PIL.Image.new(mode="RGB", size=(1700, 975), color=(49, 51, 56))
    im2 = PIL.Image.new(mode="RGB", size=(88, 900), color=(25, 25, 25))
    im3 = PIL.Image.new(mode="RGB", size=(1676, 4), color=(169, 169, 169))
    I1 = ImageDraw.Draw(im)
    ttf = 'Files/RobotoCondensed-Regular.ttf'
    myFont_small = ImageFont.truetype(ttf, 20)
    myFont = ImageFont.truetype(ttf, 25)
    myFont_title = ImageFont.truetype(ttf, 30)
    if playername == 'All':
        suffix = ''
    else:
        suffix = "'s"
        avatar_url = 'https://cdn.legiontd2.com/' + avatar
        avatar_response = requests.get(avatar_url)
        av_image = Image.open(BytesIO(avatar_response.content))
        gold_border = Image.open('Files/gold_64.png')
        if im_has_alpha(np.array(av_image)):
            im.paste(av_image, (24, 100), mask=av_image)
        else:
            im.paste(av_image, (24, 100))
        im.paste(gold_border, (24, 100), mask=gold_border)
    I1.text((10, 15), str(playername) + suffix + " Opener stats (From " + str(games) + " ranked games, Avg elo: " + str(avgelo) + ")", font=myFont_title, stroke_width=2,stroke_fill=(0, 0, 0), fill=(255, 255, 255))
    I1.text((10, 55), 'Patches: ' + ', '.join(patch), font=myFont_small, stroke_width=2, stroke_fill=(0, 0, 0),fill=(255, 255, 255))
    x = 126
    y = 175
    offset = 45
    for i in range(15):
        im.paste(im2, (x - 12, 88))
        x += 106
    x = 126
    for i, unit in enumerate(dict):
        if i == 15 or dict[unit]['Count'] == 0:
            break
        if ' ' in unit:
            string = unit.split(' ')
            unit_new = ''
            for s in string:
                unit_new = unit_new + s.capitalize()
            url_new = url2 + unit_new + '.png'
        else:
            url_new = url2 + unit.capitalize() + '.png'
        response = requests.get(url_new)
        unit_image = Image.open(BytesIO(response.content))
        im.paste(unit_image, (x, 100))
        I1.text((x, y), str(dict[unit]['Count']), font=myFont, fill=(255, 255, 255))
        I1.text((x, y+offset), str(calc_wr(dict, unit)) + '%', font=myFont, fill=(255, 255, 255))
        I1.text((x, y+offset*2), str(calc_pr(dict, unit)) + '%', font=myFont, fill=(255, 255, 255))
        I1.text((x, y+offset*3), str(get_w10(dict, unit)), font=myFont, fill=(255, 255, 255))
        new_dict = {}
        for xy in dict[unit]['OpenWith']:
            new_dict[xy] = dict[unit]['OpenWith'][xy]['Wins'] / dict[unit]['OpenWith'][xy]['Count'] * (dict[unit]['OpenWith'][xy]['Count'] / dict[unit]['Count'])
        newIndex = sorted(new_dict,key=lambda k: new_dict[k], reverse=True)
        if ' ' in newIndex[0]:
            string = newIndex[0].split(' ')
            unit_new = ''
            for s in string:
                unit_new = unit_new + s.capitalize()
            url_new = url2 + unit_new + '.png'
        else:
            url_new = url2 + newIndex[0].capitalize() + '.png'
        response = requests.get(url_new)
        temp_image = Image.open(BytesIO(response.content))
        im.paste(temp_image, (x, y + offset * 4))
        I1.text((x, y + 25+offset * 5), str(dict[unit]['OpenWith'][newIndex[0]]['Count']), font=myFont, fill=(255, 255, 255))
        I1.text((x, y + 25+offset * 6), str(round(dict[unit]['OpenWith'][newIndex[0]]['Wins'] / dict[unit]['OpenWith'][newIndex[0]]['Count']*100, 1)) + '%', font=myFont, fill=(255, 255, 255))
        I1.text((x, y + 25+offset * 7), str(round(dict[unit]['OpenWith'][newIndex[0]]['Count'] / dict[unit]['Count']*100, 1)) + '%', font=myFont, fill=(255, 255, 255))
        new_dict = {}
        for xy in dict[unit]['MMs']:
            new_dict[xy] = dict[unit]['MMs'][xy]['Wins'] / dict[unit]['MMs'][xy]['Count'] * (dict[unit]['MMs'][xy]['Count'] / dict[unit]['Count'])
        newIndex = sorted(new_dict, key=lambda k: new_dict[k], reverse=True)
        url_new = url + newIndex[0].capitalize() + '.png'
        if url_new == 'https://cdn.legiontd2.com/icons/Items/Cashout.png':
            url_new = 'https://cdn.legiontd2.com/icons/Items/CashOut.png'
        response = requests.get(url_new)
        temp_image = Image.open(BytesIO(response.content))
        im.paste(temp_image, (x, y + 25+offset * 8))
        I1.text((x, y + 50+offset * 9), str(dict[unit]['MMs'][newIndex[0]]['Count']), font=myFont,fill=(255, 255, 255))
        I1.text((x, y + 50+offset * 10), str(round(dict[unit]['MMs'][newIndex[0]]['Wins'] / dict[unit]['MMs'][newIndex[0]]['Count']*100, 1)) + '%', font=myFont, fill=(255, 255, 255))
        I1.text((x, y + 50+offset * 11),str(round(dict[unit]['MMs'][newIndex[0]]['Count'] / dict[unit]['Count'] * 100, 1)) + '%',font=myFont, fill=(255, 255, 255))
        new_dict = {}
        for xy in dict[unit]['Spells']:
            new_dict[xy] = dict[unit]['Spells'][xy]['Wins'] / dict[unit]['Spells'][xy]['Count'] * (
                        dict[unit]['Spells'][xy]['Count'] / dict[unit]['Count'])
        newIndex = sorted(new_dict, key=lambda k: new_dict[k], reverse=True)
        if ' ' in newIndex[0]:
            string = newIndex[0].split(' ')
            spell_new = ''
            for s in string:
                spell_new = spell_new + s.capitalize()
            url_new = url2 + spell_new + '.png'
        else:
            url_new = url2 + newIndex[0].capitalize() + '.png'
        response = requests.get(url_new)
        temp_image = Image.open(BytesIO(response.content))
        im.paste(temp_image, (x, y + 50+offset * 12))
        I1.text((x, y + 75 + offset * 13), str(dict[unit]['Spells'][newIndex[0]]['Count']), font=myFont,fill=(255, 255, 255))
        I1.text((x, y + 75 + offset * 14), str(round(dict[unit]['Spells'][newIndex[0]]['Wins'] / dict[unit]['Spells'][newIndex[0]]['Count'] * 100, 1)) + '%',font=myFont, fill=(255, 255, 255))
        I1.text((x, y + 75 + offset * 15),str(round(dict[unit]['Spells'][newIndex[0]]['Count'] / dict[unit]['Count'] * 100, 1)) + '%',font=myFont, fill=(255, 255, 255))
        x += 106
    for k in keys:
        if (k != 'Best add:') and (k != 'Best MMs:') and (k != '') and (k != 'Best\nSpells:'):
            im.paste(im3, (10, y+30))
        if k == 'Best\nSpells:':
            I1.text((10, y-5), k, font=myFont, stroke_width=2, stroke_fill=(0,0,0), fill=(255, 255, 255))
        else:
            I1.text((10, y), k, font=myFont, stroke_width=2, stroke_fill=(0, 0, 0), fill=(255, 255, 255))
        if (k != 'Best add:') and (k != 'Best MMs:') and (k != '') and (k != 'Best\nSpells:'):
            y += offset
        else:
            y += offset - 10
    im.save('Files/output.png')
    image_upload = imgur_client.upload_from_path('Files/output.png')
    print('Uploading output.png to Imgur...')
    return image_upload['link']


def extract_values(obj, key):
    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    arr.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, arr, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return key + ":", arr

    results = extract(obj, arr, key)
    return results


def count_value(playername, value, player_names, data):
    value_count = 0
    for i in range(len(player_names[1])):
        if str(player_names[1][i]).lower() == playername and str(data[1][i]).lower() == value:
            value_count = value_count + 1
    return value_count


def count_mythium(send):
    mercs = {"Snail": 20, "Giant Snail": 20, "Lizard": 40, "Dragon Turtle": 40, "Brute": 60, "Fiend": 60, "Dino": 80,
             "Hermit": 80, "Cannoneer": 100, "Imp": 100, "Safety Mole": 120, "Drake": 120, "Pack Leader": 160,
             "Mimic": 160, "Witch": 200, "Ogre": 200, "Ghost Knight": 240, "Four Eyes": 240, "Centaur": 280,
             "Shaman": 320, "Siege Ram": 320, "Needler": 360, "Kraken": 400}
    send_amount = 0
    for x in send:
        send_amount = send_amount + mercs.get(x)
    return send_amount


def count_elochange(playername, player_names, data):
    value_count = 0
    for i in range(len(player_names[1])):
        if str(player_names[1][i]).lower() == playername:
            value_count = value_count + data[1][i]
    return value_count


def handle_response(message) -> str:
    p_message = message.lower()
    if '!elo fine' in p_message:
        return str(apicall_elo('fine', 0) + ' :eggplant:')
    if '!julian' in p_message:
        return 'julian sucks'
    if '!penny' in p_message:
        return 'penny sucks'
    if '!green' in p_message:
        return 'fast & aggressive'
    if 'kidkpro' in p_message:
        return ':eggplant:'
    if 'widderson' in p_message:
        return ':banana:'
    if '!test' in p_message:
        return apicall_openstats(p_message[6:], 5, 0, '0')
    if '!github' in p_message:
        return 'https://github.com/Drachiir/Legion-Elo-Bot'


def apicall_getid(playername):
    request_type = 'players/byName/' + playername
    url = 'https://apiv2.legiontd2.com/' + request_type
    print(request_type)
    try:
        api_response = requests.get(url, headers=header)
        api_response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return 0
    else:
        playerid = json.loads(api_response.text)
        print(playerid['_id'])
        return playerid['_id']


def apicall_getprofile(playerid):
    url = 'https://apiv2.legiontd2.com/players/byId/' + playerid
    api_response = requests.get(url, headers=header)
    playername = json.loads(api_response.text)
    return playername


def apicall_getstats(playerid):
    request_type = 'players/stats/' + playerid
    url = 'https://apiv2.legiontd2.com/' + request_type
    api_response = requests.get(url, headers=header)
    stats = json.loads(api_response.text)
    return stats

def get_games_saved_count(playerid):
    if playerid == 'all':
        count = 0
        path1 = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/"
        playernames = os.listdir(path1)
        for i, x in enumerate(playernames):
            path2 = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/" + playernames[i] + "/gamedata/"
            json_files = [pos_json for pos_json in os.listdir(path2) if pos_json.endswith('.json')]
            count += len(json_files)
        return count
    else:
        playername = apicall_getprofile(playerid)['playerName']
        path = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/" + playername + "/gamedata/"
        if Path(Path(str(path))).is_dir():
            json_files = [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]
            if len(json_files) == 0:
                return 200
            else:
                return len(json_files)
        else:
            return 200

def apicall_pullgamedata(playerid, offset, path, expected):
    ranked_count = 0
    games_count = 0
    output = []
    url = 'https://apiv2.legiontd2.com/players/matchHistory/' + str(playerid) + '?limit=' + str(50) + '&offset=' + str(offset) + '&countResults=false'
    print('Pulling ' + str(50) + ' games from API...')
    api_response = requests.get(url, headers=header)
    raw_data = json.loads(api_response.text)
    print('Saving ranked games.')
    for x in raw_data:
        if ranked_count == expected:
            break
        if (raw_data == {'message': 'Internal server error'}) or (raw_data == {'err': 'Entry not found.'}):
            break
        if (x['queueType'] == 'Normal'):
            ranked_count += 1
            if (x['endingWave'] >= 10):
                date = str(x['date']).replace(':', '')
                date = date.replace('.', '')
                if Path(Path(str(path + 'gamedata/') + date + '_' + str(x['_id']) + ".json")).is_file():
                    print('File already there, breaking loop.')
                    break
                with open(str(path + 'gamedata/') + date + '_' + str(x['_id']) + ".json", "w") as f:
                    json.dump(x, f)
        games_count += 1
    output.append(ranked_count)
    output.append(games_count)
    return output

def get_games_loop(playerid, offset, path, expected):
    data = apicall_pullgamedata(playerid, offset, path, expected)
    count = data[0]
    games_count = data[1]
    while count < expected:
        offset += 50
        data = apicall_pullgamedata(playerid, offset, path, expected)
        count += data[0]
        games_count += data[1]
    else:
        print('All '+str(expected)+' required games pulled.')
    return games_count

def apicall_getmatchistory(playerid, games, min_elo=0, patch='0'):
    if patch != '0':
        patch_list = patch.split(',')
    games_count = 0
    if playerid != 'all':
        playername = apicall_getprofile(playerid)['playerName']
        path = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/" + playername + "/"
        if not Path(Path(str(path))).is_dir():
            print(playername + ' profile not found, creating new folder...')
            Path(str(path+'gamedata/')).mkdir(parents=True, exist_ok=True)
            with open(str(path) + "gamecount_" + playername + ".txt", "w") as f:
                data = get_games_loop(playerid, 0, path, games)
                playerstats = apicall_getstats(playerid)
                ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
                lines = [str(ranked_games), str(data)]
                f.write('\n'.join(lines))
        else:
            for file in glob.glob(path + '*.txt'):
                file_path = file
            with open(file, 'r') as f:
                txt = f.readlines()
                ranked_games_old = int(txt[0])
                games_amount_old = int(txt[1])
            playerstats = apicall_getstats(playerid)
            ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
            games_diff = ranked_games - ranked_games_old
            if ranked_games_old < ranked_games:
                games_count += get_games_loop(playerid, 0, path, games_diff)
            json_files = [pos_json for pos_json in os.listdir(path + 'gamedata/') if pos_json.endswith('.json')]
            if len(json_files) < games:
                games_count += get_games_loop(playerid, games_amount_old, path, games-len(json_files))
            with open(str(path) + "gamecount_" + playername + ".txt", "w") as f:
                f.truncate(0)
                lines = [str(ranked_games), str(games_amount_old+games_count)]
                f.write('\n'.join(lines))
        raw_data = []
        json_files = [pos_json for pos_json in os.listdir(path + 'gamedata/') if pos_json.endswith('.json')]
        count = 0
        for i, x in enumerate(sorted(json_files, reverse=True)):
            with (open(path + '/gamedata/' + x) as f):
                raw_data_partial = json.load(f)
                f.close()
                if raw_data_partial['gameElo'] > min_elo:
                    if patch == '0':
                        if i > games - 1:
                            break
                        raw_data.append(raw_data_partial)
                    else:
                        if count > games - 1:
                            break
                        for x in patch_list:
                            if str(raw_data_partial['version']).startswith('v'+x):
                                raw_data.append(raw_data_partial)
                                count += 1
    else:
        path1 = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/"
        playernames = os.listdir(path1)
        print(playernames)
        raw_data = []
        json_files = []
        json_counter = 0
        count = 0
        for i, x in enumerate(playernames):
            path2 = str(pathlib.Path(__file__).parent.resolve()) + "/Profiles/" + playernames[i] + "/gamedata/"
            json_files.extend([path2 + pos_json for pos_json in os.listdir(path2) if pos_json.endswith('.json')])
        sorted_json_files = sorted(json_files, key = lambda x: str(x.split("/")[-1].split(".")[0]), reverse=True)
        for i, x in enumerate(sorted_json_files):
            with open(x) as f:
                raw_data_partial = json.load(f)
                f.close()
                if (raw_data_partial not in raw_data) and (raw_data_partial['gameElo'] > min_elo):
                    if patch == '0':
                        if json_counter > games - 1:
                            break
                        raw_data.append(raw_data_partial)
                    else:
                        if count > games - 1:
                            break
                        for x in patch_list:
                            if str(raw_data_partial['version']).startswith('v' + x):
                                raw_data.append(raw_data_partial)
                                count += 1
                    json_counter += 1
    print(len(raw_data))
    return raw_data

def apicall_matchhistorydetails(playerid):
    playername = apicall_getprofile(playerid)['playerName']
    history_raw = apicall_getmatchistory(playerid, 10)
    player_names = extract_values(history_raw, 'playerName')
    game_results = extract_values(history_raw, 'gameResult')
    wins = count_value(str(playername).lower(), 'won', player_names, game_results)
    elochanges = extract_values(history_raw, 'eloChange')
    elochange_final = count_elochange(str(playername).lower(), player_names, elochanges)
    output = []
    if elochange_final > 0:
        output.append('+' + str(elochange_final))
    else:
        output.append(elochange_final)
    output.append(wins)
    return output

def apicall_wave1tendency(playername, option):
    playerid = apicall_getid(playername)
    if playerid == 0:
        return 'Player ' + playername + ' not found.'
    count = 0
    snail_count = 0
    kingup_atk_count = 0
    kingup_regen_count = 0
    kingup_spell_count = 0
    save_count = 0
    games = 100
    try:
        history_raw = apicall_getmatchistory(playerid, games)
    except TypeError as e:
        print(e)
        return playername + ' has not played enough games.'
    playernames = list(divide_chunks(extract_values(history_raw, 'playerName')[1], 4))
    if option == 'send':
        snail = list(divide_chunks(extract_values(history_raw, 'mercenariesSentPerWave')[1], 4))
        kingup = list(divide_chunks(extract_values(history_raw, 'kingUpgradesPerWave')[1], 4))
    elif option == 'received':
        snail = list(divide_chunks(extract_values(history_raw, 'mercenariesReceivedPerWave')[1], 4))
        kingup = list(divide_chunks(extract_values(history_raw, 'opponentKingUpgradesPerWave')[1], 4))
    gameid = extract_values(history_raw, '_id')
    while count < games:
        playernames_ranked = playernames[count]
        snail_ranked = snail[count]
        kingup_ranked = kingup[count]
        for i, x in enumerate(playernames_ranked):
            if str(x).lower() == str(playername).lower():
                if len(snail_ranked[i][0]) > 0:
                    if str(snail_ranked[i][0][0]) == 'Snail':
                        snail_count = snail_count + 1
                        break
                elif len(kingup_ranked[i][0]) > 0:
                    if str(kingup_ranked[i][0][0]) == 'Upgrade King Attack':
                        kingup_atk_count = kingup_atk_count + 1
                        break
                    if str(kingup_ranked[i][0][0]) == 'Upgrade King Regen':
                        kingup_regen_count = kingup_regen_count + 1
                        break
                    if str(kingup_ranked[i][0][0]) == 'Upgrade King Spell':
                        kingup_spell_count = kingup_spell_count + 1
                        break
                else:
                    save_count = save_count + 1
                    break
        count += 1
    send_total = kingup_atk_count+kingup_regen_count+kingup_spell_count+snail_count+save_count
    kingup_total = kingup_atk_count+kingup_regen_count+kingup_spell_count
    if send_total > 4:
        return (playername).capitalize() + "'s Wave 1 " + option + " stats: (Last " + str(send_total) + " ranked games)\nKingup: " + \
            str(kingup_total) + ' (Attack: ' + str(kingup_atk_count) + ' Regen: ' + str(kingup_regen_count) + \
            ' Spell: ' + str(kingup_spell_count) + ')\nSnail: ' + str(snail_count) + '\nSave: ' + str(save_count)
    else:
        return 'Not enough ranked data'


def apicall_winrate(playername, playername2, option, games, patch):
    playerid = apicall_getid(playername)
    if playerid == 0:
        return 'Player ' + playername + ' not found.'
    if playername2.lower() != 'all':
        playerid2 = apicall_getid(playername2)
        if playerid2 == 0:
            return 'Player ' + playername2 + ' not found.'
    playerstats = apicall_getstats(playerid)
    ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
    if games == 0:
        games = get_games_saved_count(playerid)
    elif games > ranked_games:
        return playername + ' has not played ' + str(games) + ' ranked games this season.'
    count = 0
    win_count = 0
    game_count = 0
    ranked_count = 0
    queue_count = 0
    games_limit = games * 4
    playername2_list = []
    gameresults = []
    try:
        history_raw = apicall_getmatchistory(playerid, games, 0, patch)
    except TypeError as e:
        print(e)
        return playername + ' has not played enough games.'
    games = len(history_raw)
    if games == 0:
        return 'No games found.'
    games_limit = games * 4
    playernames = list(divide_chunks(extract_values(history_raw, 'playerName')[1], 1))
    gameresult = list(divide_chunks(extract_values(history_raw, 'gameResult')[1], 1))
    gameid = extract_values(history_raw, '_id')
    patches = extract_values(history_raw, 'version')
    patches = list(dict.fromkeys(patches[1]))
    new_patches = []
    for x in patches:
        string = x
        periods = string.count('.')
        new_patches.append(string.split('.', periods)[0].replace('v', '') + '.' + string.split('.', periods)[1])
    patches = list(dict.fromkeys(new_patches))
    while count < games_limit:
        playernames_ranked_west = playernames[count] + playernames[count + 1]
        playernames_ranked_east = playernames[count + 2] + playernames[count + 3]
        gameresult_ranked_west = gameresult[count] + gameresult[count + 1]
        gameresult_ranked_east = gameresult[count + 2] + gameresult[count + 3]
        if playername2.lower() != 'all':
            for i, x in enumerate(playernames_ranked_west):
                if str(x).lower() == str(playername).lower():
                    if option == 'against':
                        if playernames_ranked_east[0].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_west[i] == 'won':
                                win_count += 1
                        elif playernames_ranked_east[1].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_west[i] == 'won':
                                win_count += 1
                    elif option == 'with':
                        if playernames_ranked_west[0].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_west[i] == 'won':
                                win_count += 1
                        elif playernames_ranked_west[1].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_west[i] == 'won':
                                win_count += 1
            for i, x in enumerate(playernames_ranked_east):
                if str(x).lower() == str(playername).lower():
                    if option == 'against':
                        if playernames_ranked_west[0].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_east[i] == 'won':
                                win_count += 1
                        elif playernames_ranked_west[1].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_east[i] == 'won':
                                win_count += 1
                    elif option == 'with':
                        if playernames_ranked_east[0].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_east[i] == 'won':
                                win_count += 1
                        elif playernames_ranked_east[1].lower() == playername2.lower():
                            game_count += 1
                            if gameresult_ranked_east[i] == 'won':
                                win_count += 1
        else:
            for i, x in enumerate(playernames_ranked_west):
                if str(x).lower() == str(playername).lower():
                    if option == 'against':
                        playername2_list.append(playernames_ranked_east[0])
                        gameresults.append(gameresult_ranked_west[i])
                        playername2_list.append(playernames_ranked_east[1])
                        gameresults.append(gameresult_ranked_west[i])
                    elif option == 'with':
                        if playernames_ranked_west[0].lower() != playername.lower():
                            playername2_list.append(playernames_ranked_west[0])
                            gameresults.append(gameresult_ranked_west[i])
                        elif playernames_ranked_west[1].lower() != playername.lower():
                            playername2_list.append(playernames_ranked_west[1])
                            gameresults.append(gameresult_ranked_west[i])
            for i, x in enumerate(playernames_ranked_east):
                if str(x).lower() == str(playername).lower():
                    if option == 'against':
                        playername2_list.append(playernames_ranked_west[0])
                        gameresults.append(gameresult_ranked_east[i])
                        playername2_list.append(playernames_ranked_west[1])
                        gameresults.append(gameresult_ranked_east[i])
                    elif option == 'with':
                        if playernames_ranked_east[0].lower() != playername.lower():
                            playername2_list.append(playernames_ranked_east[0])
                            gameresults.append(gameresult_ranked_east[i])
                        elif playernames_ranked_east[1].lower() != playername.lower():
                            playername2_list.append(playernames_ranked_east[1])
                            gameresults.append(gameresult_ranked_east[i])
        count += 4
        ranked_count += 1
    if playername2.lower() == 'all':
        most_common_mates = Counter(playername2_list).most_common(6)
        winrates = []
        for i, x in enumerate(most_common_mates):
            counter = 0
            for c, v in enumerate(playername2_list):
                if v == x[0]:
                    if gameresults[c] == 'won':
                        counter += 1
            winrates.append(round(counter / x[1] * 100, 2))
            winrates.append(counter)
        return str(playername).capitalize() + "'s winrate " + option + ' any players (From ' + str(ranked_count) + ' ranked games)\n' +\
            most_common_mates[0][0] + ': ' + str(winrates[1]) + ' win - ' + str(most_common_mates[0][1] - winrates[1]) + ' lose (' + str(winrates[0]) + '% winrate)\n' + \
            most_common_mates[1][0] + ': ' + str(winrates[3]) + ' win - ' + str(most_common_mates[1][1] - winrates[3]) + ' lose (' + str(winrates[2]) + '% winrate)\n' + \
            most_common_mates[2][0] + ': ' + str(winrates[5]) + ' win - ' + str(most_common_mates[2][1] - winrates[5]) + ' lose (' + str(winrates[4]) + '% winrate)\n' + \
            most_common_mates[3][0] + ': ' + str(winrates[7]) + ' win - ' + str(most_common_mates[3][1] - winrates[7]) + ' lose (' + str(winrates[6]) + '% winrate)\n' + \
            most_common_mates[4][0] + ': ' + str(winrates[9]) + ' win - ' + str(most_common_mates[4][1] - winrates[9]) + ' lose (' + str(winrates[8]) + '% winrate)\n' + \
            most_common_mates[5][0] + ': ' + str(winrates[11]) + ' win - ' + str(most_common_mates[5][1] - winrates[11]) + ' lose (' + str(winrates[10]) + '% winrate)\n' + \
            'Patches: ' + ', '.join(patches)
    else:
        try: return str(playername).capitalize() + "'s winrate " + option + ' ' + str(playername2).capitalize() + '(From ' + str(game_count) + ' ranked games)\n' +\
            str(win_count) + ' win - ' + str(game_count-win_count) + ' lose (' + str(round(win_count / game_count * 100, 2)) +\
            '% winrate)\nPatches: ' + ', '.join(patches)
        except ZeroDivisionError as e:
            print(e)
            return str(playername).capitalize() + ' and ' + str(playername2).capitalize() + ' have no games played ' + option + ' each other recently.'


def apicall_elcringo(playername, games, patch):
    playerid = apicall_getid(playername)
    if playerid == 0:
        return 'Player ' + playername + ' not found.'
    count = 0
    ranked_count = 0
    queue_count = 0
    playerstats = apicall_getstats(playerid)
    ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
    if games == 0:
        games = get_games_saved_count(playerid)
    elif games > ranked_games:
        return playername + ' has not played ' + str(games) + ' ranked games this season.'
    games_limit = games * 4
    save_count_list = []
    save_count_pre10_list = []
    save_count = 0
    save_count_pre10 = 0
    ending_wave_list = []
    worker_10_list = []
    mythium_list = []
    mythium_list_pergame = []
    kinghp_list = []
    try:
        history_raw = apicall_getmatchistory(playerid, games, 0, patch)
    except TypeError as e:
        print(e)
        return playername + ' has not played enough games.'
    games = len(history_raw)
    if games == 0:
        return 'No games found.'
    games_limit = games * 4
    playernames = list(divide_chunks(extract_values(history_raw, 'playerName')[1], 1))
    endingwaves = extract_values(history_raw, 'endingWave')
    snail = list(divide_chunks(extract_values(history_raw, 'mercenariesSentPerWave')[1], 1))
    kingup = list(divide_chunks(extract_values(history_raw, 'kingUpgradesPerWave')[1], 1))
    workers = list(divide_chunks(extract_values(history_raw, 'workersPerWave')[1], 1))
    kinghp_left = extract_values(history_raw, 'leftKingPercentHp')
    kinghp_right = extract_values(history_raw, 'rightKingPercentHp')
    gameid = extract_values(history_raw, '_id')
    gameelo = extract_values(history_raw, 'gameElo')
    gameelo_list = []
    patches = extract_values(history_raw, 'version')
    patches = list(dict.fromkeys(patches[1]))
    new_patches = []
    for x in patches:
        string = x
        periods = string.count('.')
        new_patches.append(string.split('.', periods)[0].replace('v', '') + '.' + string.split('.', periods)[1])
    patches = list(dict.fromkeys(new_patches))
    while count < games_limit:
        ending_wave_list.append(endingwaves[1][queue_count])
        playernames_ranked = playernames[count] + playernames[count + 1] + playernames[count + 2] + playernames[count + 3]
        snail_ranked = snail[count] + snail[count + 1] + snail[count + 2] + snail[count + 3]
        kingup_ranked = kingup[count] + kingup[count + 1] + kingup[count + 2] + kingup[count + 3]
        workers_ranked = workers[count] + workers[count + 1] + workers[count + 2] + workers[count + 3]
        mythium_list_pergame.clear()
        gameelo_list.append(gameelo[1][queue_count])
        for i, x in enumerate(playernames_ranked):
            if str(x).lower() == str(playername).lower():
                for n, s in enumerate(snail_ranked[i]):
                    small_send = 0
                    send = count_mythium(snail_ranked[i][n]) + len(kingup_ranked[i][n]) * 20
                    mythium_list_pergame.append(send)
                    if n <= 9:
                        if workers_ranked[i][n] > 5:
                            worker_adjusted = workers_ranked[i][n] - 5
                            small_send = worker_adjusted / 5 * 20
                        if send <= small_send:
                            save_count_pre10 += 1
                    elif n > 9:
                        worker_adjusted = workers_ranked[i][n] * (pow((1 + 6 / 100), n+1))
                        small_send = worker_adjusted / 5 * 20
                        if send <= small_send:
                            save_count += 1
                mythium_list.append(sum(mythium_list_pergame))
                worker_10_list.append(workers_ranked[i][9])
                if i == 0 or 1:
                    kinghp_list.append(kinghp_left[1][queue_count][9])
                else:
                    kinghp_list.append(kinghp_right[1][queue_count][9])
        save_count_pre10_list.append(save_count_pre10)
        save_count_list.append(save_count)
        save_count_pre10 = 0
        save_count = 0
        count = count + 4
        queue_count = queue_count + 1
        ranked_count = ranked_count + 1
    waves_post10 = round(sum(ending_wave_list) / len(ending_wave_list), 2) - 10
    saves_pre10 = round(sum(save_count_pre10_list) / len(save_count_pre10_list), 2)
    saves_post10 = round(sum(save_count_list) / len(save_count_list), 2)
    king_hp_10 = sum(kinghp_list) / len(kinghp_list)
    avg_gameelo = sum(gameelo_list) / len(gameelo_list)
    if ranked_count > 0:
        return (playername).capitalize() + "'s elcringo stats(Averages from last " + str(ranked_count) +" ranked games):<:GK:1161013811927601192>\n" \
            'Saves first 10:  ' + str(saves_pre10) + '/10 waves (' + str(round(saves_pre10 / 10 * 100, 2)) + '%)\n' +\
            'Saves after 10:  ' + str(saves_post10)+'/' + str(round(waves_post10, 2)) + ' waves (' + str(round(saves_post10 / waves_post10 * 100, 2)) + '%)\n'\
            'Worker on 10:  ' + str(round(sum(worker_10_list) / len(worker_10_list), 2)) + "\n"\
            'King hp on 10: ' + str(round(king_hp_10 * 100, 2)) + '%\n' + \
            'Game elo:  ' + str(round(avg_gameelo)) + '\n' + \
            'Patches:  ' + ', '.join(patches)
    else:
        return 'Not enough ranked data'

def apicall_openstats(playername, games, min_elo, patch):
    if playername == 'all':
        playerid = 'all'
        if ((games == 0) or (games > get_games_saved_count(playerid)* 0.25)) and (min_elo < 2700) and (patch == '0'):
            return 'Too many games, please limit data.'
        if games == 0:
            games = get_games_saved_count(playerid)
    else:
        playerid = apicall_getid(playername)
        if playerid == 0:
            return 'Player ' + playername + ' not found.'
        playerstats = apicall_getstats(playerid)
        ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
        if games == 0:
            games = get_games_saved_count(playerid)
        elif games > ranked_games:
            return playername + ' has not played ' + str(games) + ' ranked games this season.'
    try:
        history_raw = apicall_getmatchistory(playerid, games, min_elo, patch)
    except TypeError as e:
        print(e)
        return playername + ' has not played enough games.'
    if len(history_raw) == 0:
        return 'No games found.'
    games = len(history_raw)
    unit_dict = {}
    with open('Files/units.json', 'r') as f:
        units_json = json.load(f)
        units_extracted = extract_values(units_json, 'unitId')
        value_extracted = extract_values(units_json, 'totalValue')[1]
    for i, x in enumerate(units_extracted[1]):
        if value_extracted[i] and int(value_extracted[i]) <= 270 and int(value_extracted[i]) > 0:
            string = x
            string = string.replace('_', ' ')
            string = string.replace(' unit id', '')
            unit_dict[string] = {'Count': 0,'OpenWins': 0,'W4': 0,'OpenWith': {},'MMs': {},'Spells': {}}
    unit_dict['pack rat nest'] = {'Count': 0, 'OpenWins': 0,'W4': 0, 'OpenWith': {},'MMs': {},'Spells': {}}
    playernames = list(divide_chunks(extract_values(history_raw, 'playerName')[1], 4))
    masterminds = list(divide_chunks(extract_values(history_raw, 'legion')[1], 4))
    gameresult = list(divide_chunks(extract_values(history_raw, 'gameResult')[1], 4))
    workers = list(divide_chunks(extract_values(history_raw, 'workersPerWave')[1], 4))
    spell = list(divide_chunks(extract_values(history_raw, 'chosenSpell')[1], 4))
    fighters = list(divide_chunks(extract_values(history_raw, 'buildPerWave')[1], 4))
    gameid = extract_values(history_raw, '_id')
    gameelo = extract_values(history_raw, 'gameElo')
    patches = extract_values(history_raw, 'version')
    patches = list(dict.fromkeys(patches[1]))
    new_patches = []
    gameelo_list = []
    count = 0
    for x in patches:
        string = x
        periods = string.count('.')
        new_patches.append(string.split('.', periods)[0].replace('v', '') + '.' + string.split('.', periods)[1])
    patches = list(dict.fromkeys(new_patches))
    print('Starting openstats command...')
    while count < games:
        playernames_ranked = playernames[count]
        masterminds_ranked = masterminds[count]
        gameresult_ranked = gameresult[count]
        workers_ranked = workers[count]
        spell_ranked = spell[count]
        gameelo_list.append(gameelo[1][count])
        if playername != 'all':
            for i, x in enumerate(playernames_ranked):
                if str(x).lower() == playername.lower():
                    opener_ranked_raw = [fighters[count][i][0],fighters[count][i][1],fighters[count][i][2],fighters[count][i][3]]
                    player_num = i
                    break
        else:
            opener_ranked_raw = []
            for i in range(4):
                opener_ranked_raw.extend([fighters[count][i][0],fighters[count][i][1],fighters[count][i][2],fighters[count][i][3]])
        opener_ranked = []
        for i, x in enumerate(opener_ranked_raw):
            opener_ranked.extend([[]])
            for v, y in enumerate(x):
                string = y.split('_unit_id:')
                opener_ranked[i].append(string[0].replace('_', ' '))
        if playername.lower() != 'all':
            s = set()
            for x in range(4):
                for y in opener_ranked[x]:
                    s.add(y)
            for y in s:
                if y != opener_ranked[0][0]:
                    if y in unit_dict[opener_ranked[0][0]]['OpenWith']:
                        unit_dict[opener_ranked[0][0]]['OpenWith'][y]['Count'] += 1
                        if gameresult_ranked[player_num] == 'won':
                            unit_dict[opener_ranked[0][0]]['OpenWith'][y]['Wins'] += 1
                    else:
                        unit_dict[opener_ranked[0][0]]['OpenWith'][y] = {'Count': 1, 'Wins': 0}
                        if gameresult_ranked[player_num] == 'won':
                            unit_dict[opener_ranked[0][0]]['OpenWith'][y]['Wins'] += 1
                else:
                    unit_dict[opener_ranked[0][0]]['Count'] += 1
                    if masterminds_ranked[player_num] not in unit_dict[opener_ranked[0][0]]['MMs']:
                        unit_dict[opener_ranked[0][0]]['MMs'][masterminds_ranked[player_num]] = {'Count': 1, 'Wins': 0}
                    else:
                        unit_dict[opener_ranked[0][0]]['MMs'][masterminds_ranked[player_num]]['Count'] += 1
                    if spell_ranked[player_num] not in unit_dict[opener_ranked[0][0]]['Spells']:
                        unit_dict[opener_ranked[0][0]]['Spells'][spell_ranked[player_num]] = {'Count': 1, 'Wins': 0}
                    else:
                        unit_dict[opener_ranked[0][0]]['Spells'][spell_ranked[player_num]]['Count'] += 1
                    unit_dict[opener_ranked[0][0]]['W4'] += workers_ranked[player_num][3]
                    if gameresult_ranked[player_num] == 'won':
                        unit_dict[opener_ranked[0][0]]['OpenWins'] += 1
                        unit_dict[opener_ranked[0][0]]['MMs'][masterminds_ranked[player_num]]['Wins'] += 1
                        unit_dict[opener_ranked[0][0]]['Spells'][spell_ranked[player_num]]['Wins'] += 1
        else:
            counter = 0
            for i in range(4):
                s = set()
                for x in range(counter, counter+4):
                    for y in opener_ranked[x]:
                        s.add(y)
                for y in s:
                    if y != opener_ranked[counter][0]:
                        if y in unit_dict[opener_ranked[counter][0]]['OpenWith']:
                            unit_dict[opener_ranked[counter][0]]['OpenWith'][y]['Count'] += 1
                            if gameresult_ranked[i] == 'won':
                                unit_dict[opener_ranked[counter][0]]['OpenWith'][y]['Wins'] += 1
                        else:
                            unit_dict[opener_ranked[counter][0]]['OpenWith'][y] = {'Count': 1, 'Wins': 0}
                            if gameresult_ranked[i] == 'won':
                                unit_dict[opener_ranked[counter][0]]['OpenWith'][y]['Wins'] += 1
                    else:
                        unit_dict[opener_ranked[counter][0]]['Count'] += 1
                        if masterminds_ranked[i] not in unit_dict[opener_ranked[counter][0]]['MMs']:
                            unit_dict[opener_ranked[counter][0]]['MMs'][masterminds_ranked[i]] = {'Count': 1,'Wins': 0}
                        else:
                            unit_dict[opener_ranked[counter][0]]['MMs'][masterminds_ranked[i]]['Count'] += 1
                        if spell_ranked[i] not in unit_dict[opener_ranked[counter][0]]['Spells']:
                            unit_dict[opener_ranked[counter][0]]['Spells'][spell_ranked[i]] = {'Count': 1, 'Wins': 0}
                        else:
                            unit_dict[opener_ranked[counter][0]]['Spells'][spell_ranked[i]]['Count'] += 1
                        unit_dict[opener_ranked[counter][0]]['W4'] += workers_ranked[i][3]
                        if gameresult_ranked[i] == 'won':
                            unit_dict[opener_ranked[counter][0]]['OpenWins'] += 1
                            unit_dict[opener_ranked[counter][0]]['MMs'][masterminds_ranked[i]]['Wins'] += 1
                            unit_dict[opener_ranked[counter][0]]['Spells'][spell_ranked[i]]['Wins'] += 1
                counter += 4
        count += 1
    newIndex = sorted(unit_dict, key=lambda x: unit_dict[x]['Count'], reverse=True)
    unit_dict = {k: unit_dict[k] for k in newIndex}
    avgelo = round(sum(gameelo_list)/len(gameelo_list))
    return create_image_unitstats(unit_dict, games, playerid, avgelo, patches)

def apicall_mmstats(playername, games, min_elo, patch):
    if playername == 'all':
        playerid = 'all'
        if ((games == 0) or (games > get_games_saved_count(playerid)* 0.25)) and (min_elo < 2700) and (patch == '0'):
            return 'Too many games, please limit data.'
        if games == 0:
            games = get_games_saved_count(playerid)
    else:
        playerid = apicall_getid(playername)
        if playerid == 0:
            return 'Player ' + playername + ' not found.'
        playerstats = apicall_getstats(playerid)
        ranked_games = playerstats['rankedWinsThisSeason'] + playerstats['rankedLossesThisSeason']
        if games == 0:
            games = get_games_saved_count(playerid)
        elif games > ranked_games:
            return playername + ' has not played ' + str(games) + ' ranked games this season.'
    count = 0
    mmnames_list = ['LockIn', 'Greed', 'Redraw', 'Yolo', 'Fiesta', 'CashOut', 'Castle', 'Cartel', 'Chaos']
    masterminds_dict = {}
    for x in mmnames_list:
        masterminds_dict[x] = {"Count": 0, "Wins": 0, "W10": 0, "Results": [], "Opener": [], 'Spell': []}
    gameelo_list = []
    try:
        history_raw = apicall_getmatchistory(playerid, games, min_elo, patch)
    except TypeError as e:
        print(e)
        return playername + ' has not played enough games.'
    if len(history_raw) == 0:
        return 'No games found.'
    games = len(history_raw)
    print(games)
    playernames = list(divide_chunks(extract_values(history_raw, 'playerName')[1], 4))
    masterminds = list(divide_chunks(extract_values(history_raw, 'legion')[1], 4))
    gameresult = list(divide_chunks(extract_values(history_raw, 'gameResult')[1], 4))
    workers = list(divide_chunks(extract_values(history_raw, 'workersPerWave')[1], 4))
    opener = list(divide_chunks(extract_values(history_raw, 'firstWaveFighters')[1], 4))
    spell = list(divide_chunks(extract_values(history_raw, 'chosenSpell')[1], 4))
    gameid = extract_values(history_raw, '_id')
    gameelo = extract_values(history_raw, 'gameElo')
    patches = extract_values(history_raw, 'version')
    patches = list(dict.fromkeys(patches[1]))
    new_patches = []
    for x in patches:
        string = x
        periods = string.count('.')
        new_patches.append(string.split('.', periods)[0].replace('v', '')+'.'+string.split('.', periods)[1])
    patches = list(dict.fromkeys(new_patches))
    print('Starting mmstats command...')
    while count < games:
        playernames_ranked = playernames[count]
        masterminds_ranked = masterminds[count]
        gameresult_ranked = gameresult[count]
        workers_ranked = workers[count]
        opener_ranked = opener[count]
        spell_ranked = spell[count]
        gameelo_list.append(gameelo[1][count])
        for i, x in enumerate(playernames_ranked):
            if playerid == 'all':
                masterminds_dict[masterminds_ranked[i]]["Count"] += 1
                if gameresult_ranked[i] == 'won':
                    masterminds_dict[masterminds_ranked[i]]["Wins"] += 1
                masterminds_dict[masterminds_ranked[i]]["W10"] += workers_ranked[i][9]
                masterminds_dict[masterminds_ranked[i]]['Results'].append(gameresult_ranked[i])
                masterminds_dict[masterminds_ranked[i]]['Spell'].append(spell_ranked[i])
                if ',' in opener_ranked[i]:
                    string = opener_ranked[i]
                    commas = string.count(',')
                    masterminds_dict[masterminds_ranked[i]]['Opener'].append(string.split(',',commas)[commas])
                else:
                    masterminds_dict[masterminds_ranked[i]]['Opener'].append(opener_ranked[i])
            elif str(x).lower() == str(playername).lower():
                masterminds_dict[masterminds_ranked[i]]["Count"] += 1
                if gameresult_ranked[i] == 'won':
                    masterminds_dict[masterminds_ranked[i]]["Wins"] += 1
                masterminds_dict[masterminds_ranked[i]]["W10"] += workers_ranked[i][9]
                masterminds_dict[masterminds_ranked[i]]['Results'].append(gameresult_ranked[i])
                masterminds_dict[masterminds_ranked[i]]['Spell'].append(spell_ranked[i])
                if ',' in opener_ranked[i]:
                    string = opener_ranked[i]
                    commas = string.count(',')
                    masterminds_dict[masterminds_ranked[i]]['Opener'].append(string.split(',',commas)[commas])
                else:
                    masterminds_dict[masterminds_ranked[i]]['Opener'].append(opener_ranked[i])
        count += 1
    newIndex = sorted(masterminds_dict, key=lambda x: masterminds_dict[x]['Count'], reverse=True)
    masterminds_dict = {k: masterminds_dict[k] for k in newIndex}
    avg_gameelo = round(sum(gameelo_list)/len(gameelo_list))
    return create_image_mmstats(masterminds_dict, count, playerid, avg_gameelo, patches)

def apicall_elo(playername, rank):
    playerid = apicall_getid(playername)
    if playerid == 0:
        output = 'Player ' + str(playername) + ' not found.'
    else:
        stats = apicall_getstats(playerid)
        playtime_minutes = stats['secondsPlayed'] / 60
        playtime_hours = playtime_minutes / 60
        url = 'https://apiv2.legiontd2.com/players/stats?limit=100&sortBy=overallElo&sortDirection=-1'
        api_response = requests.get(url, headers=header)
        leaderboard = json.loads(api_response.text)
        history_details = apicall_matchhistorydetails(playerid)
        new_dict = {item['_id']: item['_id'] for item in leaderboard}
        if rank == 0:
            for i, key in enumerate(new_dict.keys()):
                if key == playerid:
                    index = i
                    return str(playername).capitalize() + ' is rank ' + str(index + 1) + ' with ' + str(
                        stats['overallElo']) + ' elo (Peak: ' + str(stats['overallPeakEloThisSeason']) + ') and ' + str(
                        round(playtime_hours)) + ' in game hours.\nThey have won ' + \
                        str(history_details[1]) + ' out of their last 10 games. (Elo change: ' + \
                        str(history_details[0]) + ')'
            else:
                return str(playername).capitalize() + ' has ' + str(stats['overallElo']) + ' elo (Peak: ' + str(
                    stats['overallPeakEloThisSeason']) + ') with ' + str(round(playtime_hours)) + ' in game hours.\n' \
                    'They have won ' + str(history_details[1]) + ' out of their last 10 games. ' \
                    '(Elo change: ' + str(history_details[0]) + ')'
        else:
            return str(playername).capitalize() + ' is rank ' + str(rank) + ' with ' + str(
                stats['overallElo']) + ' elo (Peak: ' + str(stats['overallPeakEloThisSeason']) + ') and ' + str(
                round(playtime_hours)) + ' in game hours.\nThey have won ' + \
                str(history_details[1]) + ' out of their last 10 games. (Elo change: ' + \
                str(history_details[0]) + ')'


def apicall_bestie(playername):
    playerid = apicall_getid(playername)
    if playerid == 0:
        return 'Player ' + str(playername) + ' not found.'
    else:
        request_type = 'players/bestFriends/' + playerid
        url = 'https://apiv2.legiontd2.com/' + request_type + '?limit=1&offset=0'
        api_response = requests.get(url, headers=header)
        bestie = json.loads(api_response.text)
        if not bestie:
            return 'no bestie :sob: (No data)'
        else:
            for bestie_new in bestie[0].values():
                print(bestie_new['playerName'])
                bestie_name = bestie_new['playerName']
                break
            print(bestie[0]['count'])

            return str(playername).capitalize() + "'s bestie is " + bestie_name + ' :heart: with ' + str(
                bestie[0]['count']) + ' games together.'


def apicall_showlove(playername, playername2):
    playerid = apicall_getid(playername)
    print(playername)
    print(playername2)
    if playerid == 0:
        return 'Player ' + str(playername) + ' not found.'
    else:
        request_type = 'players/bestFriends/' + playerid
        url = 'https://apiv2.legiontd2.com/' + request_type + '?limit=50&offset=0'
        api_response = requests.get(url, headers=header)
        bestie = json.loads(api_response.text)
        count = 0
        nextvaluesave = 0
        while count < len(bestie):
            for bestie_new in bestie[count].values():
                if isinstance(bestie_new, dict):
                    name = bestie_new['playerName']
                    if str(name).lower() == str(playername2).lower():
                        print('found target')
                        nextvaluesave = 1
                    count = count + 1
                else:
                    if nextvaluesave == 1:
                        love_count = bestie_new
                        print(love_count)
                        return playername.capitalize() + ' has played ' + str(
                            love_count) + ' games with ' + playername2.capitalize() + ' :heart:'
    return 'Not enough games played together'


def apicall_rank(rank):
    url = 'https://apiv2.legiontd2.com/players/stats?limit=1&offset=' + str(
        int(rank) - 1) + '&sortBy=overallElo&sortDirection=-1'
    api_response = requests.get(url, headers=header)
    player_info = json.loads(api_response.text)
    name = apicall_getprofile(player_info[0]['_id'])
    return apicall_elo(str(name['playerName']).lower(), rank)


def apicall_gamestats(playername):
    playerid = apicall_getid(playername)
    stats = apicall_getstats(playerid)
    wins = stats['rankedWinsThisSeason']
    loses = stats['rankedLossesThisSeason']
    winrate = wins / (wins + loses)
    return str(playername).capitalize() + "'s stats(Season 2023):\nElo: " + str(stats['overallElo']) + '(Peak: ' + str(
        stats['overallPeakEloThisSeason']) + ')\nGames played: ' + \
        str(wins + loses) + '\nWinrate: ' + str(round(winrate * 100)) + '%\nBehavior score: ' + str(
            stats['behaviorScore'] / 10)


