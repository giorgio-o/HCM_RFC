import numpy as np

"""
G.Onnis, 01.2017

Tecott Lab UCSF
"""



def get_colors_dict(experiment):
    """color dictionary for AS features, food, drink, movement features
    """
    fcolors = {

        'AS': {
            0: '#735775',     # pantone 525U
            1: '#9361B0',      # 527U
            2: '#CEA5E1',       # 529U
            3: '#E4C7EB'        # 531U
            },

        'IS': {
            0: '.4',
            1: '0',           # dark grey
            },
        
        'F': {
            0: '#A6813D',       # 125U
            1: '#D79133',       # 124U
            2: '#FFAC2A',       # pantone 123U. official food orange was #FA9531, 
            3: '#FFCC52'        # 121U
            },

        'W': {
            0: '#3F5666',       # pantone 303U
            1: '#28628E',       # 301U
            2: '#1295D8',       # 299U
            3: '#7ECCEE'        # 297U
            },

        'M': {
            0: '#5B794E',       # 364U
            1: '#56944F',       # 362U
            2: '#5DB860',       # 360U
            3: '#97D88A'        # 358U
            },

        'other': {
            0: '#DD5061',       # pantone 199U, dark red
            2: '#700C13',       # dark red
            3: '.5',            # mid-grey
            4: '#B02B0A',       # light dark red
            },
        }

    # fcolors = {

    #     'AS': {
    #         0: '#94679C',     # pantone 259U. used to be'#7552b4'
    #         1: '#B230C6',      # darker
    #         2: '#D1A0D8'       # lighter    
    #         },

    #     'IS': {
    #         0: '.4',
    #         1: '0',           # dark grey
    #         },
        
    #     'F': {
    #         0: '#F79B2E',       # pantone 130U. official food orange was #FA9531, 
    #         1: '#C97F3A',       # 145U, darker brown
    #         2: '#FFD378',       # 134U, lighter
    #         },

    #     'W': {
    #         0: '#1295D8',       # pantone 299U
    #         1: '#3D5588',       # 288U, darker
    #         2: '#AEE9E8',       # 317U, lighter
    #         },

    #     'M': {
    #         0: '#009700',       # light green
    #         1: '#006400',       # dark green
    #         2: '#D7D733',        # rotten yellow
    #         },

    #     'other': {
    #         0: '#DD5061',       # pantone 199U, dark red
    #         2: '#700C13',       # dark red
    #         3: '.5',            # mid-grey
    #         4: '#B02B0A',       # light dark red
    #         },
    #     }

    experiment.fcolors = fcolors
    return fcolors


def get_settings(experiment):
    """various plot specifications. 
        returns feature_dicts
    """
    fcolors = get_colors_dict(experiment)
    plot_settings_dict = {

                        # AS features
                        'ASP':  
                            {
                            'name': 'Active State Probability',
                            'unit': '[-]',
                            'color': fcolors['AS'][1]     
                            },

                        'ASN':    
                            {
                            'name': 'Active State Number',
                            'unit': '[-]',
                            'color': fcolors['AS'][1]     
                            },

                        'ASD':
                            {
                            'name': 'Active State Duration',
                            'unit': '[min]',
                            'color': fcolors['AS'][1],
                            }, 

                        # Totals
                        'TF':    
                            {
                            'name': 'Total Food',
                            'unit': '[g]',
                            'color': fcolors['F'][2]     
                            },

                        'TW':    
                            {
                            'name': 'Total Water',
                            'unit': '[g]',
                            'color': fcolors['W'][2]
                            },

                        'TM':
                            {
                            'name': 'Total Distance',
                            'unit': '[m]',
                            'color': fcolors['M'][2]
                            },
                            
                        # AS Intensity
                        'FASInt': 
                            {
                            'name': 'Food AS Intensity',
                            'unit': '[mg/AS.s]',
                            'color': fcolors['F'][2]
                            },

                        'WASInt': 
                            {
                            'name': 'Water AS Intensity',
                            'unit': '[mg/AS.s]',
                            'color': fcolors['W'][2]
                            },

                        'MASInt': 
                            {
                            'name': 'Move AS Intensity',
                            'unit': '[cm/AS.s]',
                            'color': fcolors['M'][2]
                            },


                        # Bout features
                        'FBASR':
                            {
                            'name': 'Feeding AS Bout Rate',
                            'unit': '[1/AS.hr]',
                            'color': fcolors['F'][2],
                            'bins' : range(0, 81, 2),
                            },

                        'FBN':
                            {
                            'name': 'Feeding Bout Numbers',
                            'unit': '[-]',
                            'color': fcolors['F'][2],
                            'bins' : range(0, 401, 5),
                            },

                        'FBS':
                            {
                            'name': 'Feeding Bout Avg Size',
                            'unit': '[mg]',
                            'color': fcolors['F'][2],
                            'bins' : range(61),
                            },

                        'FBD':
                            {
                            'name': 'Feeding Bout Avg Duration',
                            'unit': '[s]',
                            'color': fcolors['F'][2],
                            'bins' : range(61),
                            },

                        'FBI':
                            {
                            'name': 'Feeding Bout Avg Intensity',
                            'unit': '[mg/s]',
                            'color': fcolors['F'][0],
                            'bins' : np.linspace(0, 4, .1),
                            },

                        'WBASR':
                            {
                            'name': 'Drinking AS Bout Rate',
                            'unit': '[1/AS.hr]',
                            'color': fcolors['W'][2],
                            'bins' : range(0, 41, 10),
                            },

                        'WBN':
                            {
                            'name': 'Drinking Bout Numbers',
                            'unit': '[-]',
                            'color': fcolors['W'][2],
                            'bins' : range(0, 401, 5),
                            },

                        'WBS':
                            {
                            'name': 'Drinking Bout Avg Size',
                            'unit': '[mg]',
                            'color': fcolors['W'][2],
                            'bins' : range(0, 201, 2),
                            },

                        'WBD':
                            {
                            'name': 'Drinking Bout Avg Duration',
                            'unit': '[s]',
                            'color': fcolors['W'][2],
                            'bins' : range(61),
                            },

                        'WBI':
                            {
                            'name': 'Drinking Bout Avg Intensity',
                            'unit': '[mg/s]',
                            'color': fcolors['W'][2],
                            'bins' : np.linspace(0, 4, .1),
                            },

                        'MBASR':
                            {
                            'name': 'Move AS Bout Rate',
                            'unit': '[1/AS.hr]',
                            'color': fcolors['M'][2],
                            'bins' : range(0, 301, 10),
                            },

                        'MBN':
                            {
                            'name': 'Move Bout Numbers',
                            'unit': '[-]',
                            'color': fcolors['M'][2],
                            'bins' : np.linspace(0, 4, .1),
                            },

                        'MBD':
                            {
                            'name': 'Move Bout Avg Duration',
                            'unit': '[s]',
                            'color': fcolors['M'][2],
                            },
                        'MBS':
                            {
                            'name': 'Move Bout Avg Size',
                            'unit': '[cm]',
                            'color': fcolors['M'][2],
                            },

                        'MBI':
                            {
                            'name': 'Move Bout Avg Velocity',
                            'unit': '[cm/s]',
                            'color': fcolors['M'][2],
                            },

                        # events
                        'FEN':
                            {
                            'name': 'Feeding Event Numbers',
                            'unit': '[-]',
                            'color': fcolors['F'][0],
                            },

                        'FETD':
                            {
                            'name': 'Feeding Event Total Duration',
                            'unit': '[min]',
                            'color': fcolors['F'][0],
                            },

                        'FEAD':
                            {
                            'name': 'Feeding Event Average Duration',
                            'unit': '[s]',
                            'color': fcolors['F'][0],
                            },

                        'WEN':
                            {
                            'name': 'Drinking Event Numbers',
                            'unit': '[-]',
                            'color': fcolors['W'][0],
                            },

                        'WETD':
                            {
                            'name': 'Drinking Event Total Duration',
                            'unit': '[min]',
                            'color': fcolors['W'][0],
                            },

                        'WEAD':
                            {
                            'name': 'Drinking Event Average Duration',
                            'unit': 's',
                            'color': fcolors['W'][0],
                            },

                        'FC':
                            {
                            'name': 'Feeding Coefficient',
                            'unit': 'mg/s',
                            'color': fcolors['F'][0],
                            'bins' : np.arange(0, 10, 0.5),
                            },

                        'LC':
                            {
                            'name': 'Drinking Coefficient',
                            'unit': 'mg/s',
                            'color': fcolors['W'][0],
                            'bins' : range(0, 175, 5),
                            },

                        'FETS':
                            {
                            'name': 'Total Feeding Events Size',
                            'unit': 'g',
                            'color': fcolors['F'][0],
                            'bins' : np.arange(0, 10, 0.5),
                            },

                        'WETS':
                            {
                            'name': 'Total Drinking Events Size',
                            'unit': 'g',
                            'color': fcolors['W'][0],
                            'bins' : np.arange(0, 10, 0.5),
                            },

        }

    experiment.plot_settings_dict = plot_settings_dict
    return plot_settings_dict





        # # the old colors
        # features_RGBA=[           # don't change the order. rasters, time budgets and other plots are involved.
        #   '#605AA2',          # some_other_violet
        #   # (0.4, 0.2, 1., 1.),       # 0 active state: violet
        #   # (0.4, 0.0, 0.8, 1.0), # 0 a darker violet
        #   # (0.3, 0.0, 0.6, 1.0),     # 0 another one
        #   (0.8, 0.4, 0., 1.),     # 1 feed: orange
        #   (0., 0., 1., 1.),       # 2 drink
        #   (0., 0.4, 0., 1.),      # 3 loco: darker green 
        #   (0.8, 0.4, 0., 1.),     # 4 feedASInt: same as feed
        #   (0., 0., 1., 1.),       # 5 drinkASInt: same as drink
        #   (0., 0.3, 0., 1.),      # 6 locoASInt: even darker green
        #   # (0.6, 0.1, 0.6, 1.0),     # feed and drink. purple
        #   # (0.0, 0.0, .6, 1.0),      # darker blue 
        #   '0.3',                  # grey
        #   ]   
    
        # old settings
        # # #plot dictionaries for ylims and ticks. this will overwrite those in _logic
        # plot_dicts = {
        #   'PNASFig4A':    #ASProb
        #       {
        #           'ymin': 0.0,
        #           'ymax': 1.0,
        #           'yticks': np.linspace(0,1,5+1)
        #       },

        #   'PNASFig4B':    #ASRate
        #       {
        #           'ymin': 0.0,
        #           'ymax': 4.0,    
        #           'yticks': np.linspace(0, 4, 4+1)  
        #       },

        #   'PNASFig4C':    #ASdur
        #       {
        #           'ymin': 0.0,
        #           # 'ymax': 30.0,   
        #           # 'ymax_': 60.0,                                # if large y is the case
        #           # 'yticks': np.linspace(0, 30, 6+1),
        #           # 'yticks_': np.linspace(0, 60, 6+1)  # if large y is the case
        #           'ymax': 120.0,   
        #           'ymax_': 300.0,                             # if large y is the case
        #           'yticks': np.linspace(0, 120, 4+1),
        #           'yticks_': np.linspace(0, 300, 5+1)   # if large y is the case
        #       },

        #   'PNASFig6A_food':   #totalFood
        #       {
        #           'ymin': 0.0,
        #           'ymax': 1.0,    
        #           'yticks': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        #       },

        #   'PNASFig6A_water':  #totalWater
        #       {
        #           'ymin': 0.0,
        #           'ymax': 1.0,    
        #           'yticks': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        #       },

        #   'PNASFig6A_distance':   #totalDistance
        #       {
        #           'ymin': 0.0,
        #           'ymax': 150.0,  
        #           'ymax_': 600.0,                                     # if large y is the case
        #           'yticks': [0.0, 50.0, 100.0, 150.0],  
        #           'yticks_': np.linspace(0, 600, 6+1)           # if large y is the case
        #       },

        #   # 'PNASFig6B_food':   #feedASBoutRate
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 30.0,    
        #   #       'yticks': np.linspace(0, 30, 6+1)
        #   #   },

        #   # 'PNASFig6B_water':  #drinkASBoutRate
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 20.0,    
        #   #       'yticks': np.linspace(0, 20, 4+1)
        #   #   },

        #   # 'ASBoutRate_loco':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 120.0,    
        #   #       'ymax_': 240.0, 
        #   #       'yticks': np.linspace(0, 120, 12+1),
        #   #       'yticks_': np.linspace(0, 240, 12+1) 
        #   #   },

        #   # 'BoutRate_food':   #feedBoutRate
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 30.0,    # default 40
        #   #       'yticks': np.linspace(0, 30, 6+1)
        #   #   },


        #   # 'BoutRate_water':   #feedBoutRate
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 20.0,    
        #   #       'yticks': np.linspace(0, 20, 4+1)
        #   #   },

        #   # 'BoutRate_loco':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 250.0,    
        #   #       'ymax_': 500.0, 
        #   #       'yticks': np.linspace(0, 250, 10+1),
        #   #       'yticks_': np.linspace(0, 500, 10+1)
        #   #   },

        #   # 'PNASFig6C_food':   #feedBoutSize
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 200.0,    
        #   #       'ymax_': 400.0,
        #   #       'yticks': np.linspace(0, 200, 4+1),
        #   #       'yticks_': np.linspace(0, 400, 4+1)
        #   #   },

        #   # 'PNASFig6C_water':  #drinkBoutSize
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 200.0,    
        #   #       'ymax_': 400.0,
        #   #       'yticks': np.linspace(0, 200, 4+1),
        #   #       'yticks_': np.linspace(0, 400, 4+1)
        #   #   },

        #   # 'BoutLength_loco':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 40.0,
        #   #       'ymax_': 120.0,    
        #   #       'yticks': np.linspace(0,40.0,8+1),
        #   #       'yticks_': np.linspace(0,120.0,6+1)
        #   #   },

        #   # 'BoutIntensity_food':   
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 2.0,    
        #   #       'ymax_': 3.0,
        #   #       'yticks': [0.0, 0.5, 1.0, 1.5, 2.0],
        #   #       'yticks_': np.linspace(0, 3.0, 3+1)
        #   #   },

        #   # 'BoutIntensity_water':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 20.0,    
        #   #       'ymax_': 40.0,
        #   #       'yticks': [0.0, 5.0, 10.0, 15.0, 20.0],
        #   #       'yticks_': np.linspace(0, 40., 4+1)
        #   #   },

        #   # 'BoutSpeed_loco':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 25.0, 
        #   #       'ymax_': 50.0, 
        #   #       'yticks': np.linspace(0, 25, 5+1),
        #   #       'yticks_': np.linspace(0, 50, 5+1)
        #   #   },

        #   # 'BoutDuration_food':   
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 250.0,    
        #   #       'ymax_': 500.0,
        #   #       'yticks': np.linspace(0, 250, 5+1),
        #   #       'yticks_': np.linspace(0, 500, 5+1)
        #   #   },

        #   # 'BoutDuration_water':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 40.0,
        #   #       'ymax_': 200.0,
        #   #       'yticks': np.linspace(0, 40, 4+1),
        #   #       'yticks_': np.linspace(0, 200, 4+1) 
        #   #   },

        #   # 'BoutDuration_loco':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 6.0,    
        #   #       'yticks': np.linspace(0,6.0,6+1)
        #   #   },

        #   # 'LocoEntropy':  
        #   #   {
        #   #       'ymin': 2.0,
        #   #       'ymax': 7.0,    # default 7
        #   #       'yticks': range(2, 7+1, 1)
        #   #   },     

        #   # 'LocoDiversity':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 200.0,    # default 200
        #   #       'yticks': range(0, 200+20, 20)
        #   #   }, 

        #   # 'LocoMostCommon':  
        #   #   {
        #   #       'ymin': 0.0,
        #   #       'ymax': 1.0,    # default 1
        #   #       'yticks': [i / 10. for i in xrange(10+1)]
        #   #   },  

        # } 
