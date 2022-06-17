def nplayers():
    import json
    import urllib.request

    #!pip install datapackage 
    import datapackage
    import pandas as pd
    
    data_url = 'https://datahub.io/core/country-list/datapackage.json'

    # to load Data Package into storage
    package = datapackage.Package(data_url)

    # to load only tabular data
    resources = package.resources
    for resource in resources:
        if resource.tabular:
            data = pd.read_csv(resource.descriptor['path'])
            print (data)
    data['nplayers'] = pd.NA
    country_codes = data['Code']#['FR','DE','BW','PF','AU']
    for i,country in enumerate(country_codes):
        urlstr = 'https://api.chess.com/pub/country/%s/players'%\
            country
        try:
            with urllib.request.urlopen(urlstr) as url:
                dat=json.loads(url.read().decode())
            N = len(dat['players'])
            print(country, N)
            data.iloc[i, 2] = N
        except:
            print(country, 'err')
            pass

    return(data)
        

def list_players(country_code='BW',maxplayers = None): # deafult look up botswana...
    import json
    #import ijson
    #import urllib.request
    import requests
    import pandas as pd
    import numpy as np
    if maxplayers is None:
        maxplayers = np.inf

    urlstr = 'https://api.chess.com/pub/country/%s/players'%\
        country_code
    with requests.Session() as session:
        with session.get(urlstr) as req:#urllib.request.urlopen(urlstr) as url:
                #dat=json.loads(url.read().decode())
            dat = req.json()            
        print('successful')
        rating_types = ['chess_bullet','chess_blitz','chess_rapid',
                        'fide','national','uscf']
        ratings = [-1,]*len(rating_types)
        if maxplayers < np.inf:
            player_names = dat['players'][:maxplayers]
        else:
            player_names = dat['players']
        all_ratings = pd.DataFrame(index = player_names,
                                   data = {r:pd.NA for r in rating_types})
        last_letter = '1'
        all_rating_types = set(())
        n = 0
        for player in dat['players']:
            if n == maxplayers:
                break
            n += 1
            letter = player[0]
            if letter != last_letter:
                print(player)
                last_letter = letter
            #print(player, end=' ')
            player_stats_url = f'https://api.chess.com/pub/player/{player}/stats'
            with session.get(player_url) as player_req:
                dat2 = player_req.json()
            player_info_url = f'https://api.chess.com/pub/player/{player}/stats'
            #try:
            #    with urllib.request.urlopen(player_url) as url:
            #        dat2=json.loads(url.read().decode())
            #except:
            #    raise Exception
            for i, rt in enumerate(rating_types):
                #print(i)
                success = False
                try:
                    rating_i = dat2[rt]
                    success = True
                except KeyError: 
                    ratings[i] = pd.NA
                if success:
                    try: 
                        ratings[i] = int(rating_i['last']['rating'])
                    except TypeError:
                        ratings[i] = int(rating_i) # fide etc. has just an integer
                    except:
                        ratings[i] = pd.NA

                    

            all_rating_types = all_rating_types.union(dat2.keys())
            all_ratings.loc[player] = ratings
    print(all_rating_types)
    return(all_ratings)
