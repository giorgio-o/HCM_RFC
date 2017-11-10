"""
G.Onnis, 01.2017

Tecott Lab UCSF
"""


def add_variables_to_experiment(experiment):
    """
    """
    E = experiment

    E.xy_bins = [
                [2, 4],
                [12, 24], 
                ]

    E.levels = [
                'group',
                'mouse',
                'mouseday'
                ]

    E.bin_types = [
                '3cycles',      #24H,DC,LC
                '12bins',
                '24bins',
                'AS12bins'
                ]

    E.err_types = [
                'sd', 
                'sem'
                ]

    E.cycles = [
                    '24H', 
                    'DC', 
                    'LC'
                ]
    E.cycles_expanded = [
                        '24Hours', 
                        'Inactive State', 
                        'Dark Cycle', 
                        'Light Cycle', 
                        'AS 24Hours', 
                        'AS Dark Cycle', 
                        'AS Light Cycle'
                        ]

    E.all_cycles = [
                    '24H', 
                    'IS', 
                    'DC', 
                    'LC', 
                    'AS24H', 
                    'ASDC', 
                    'ASLC'
                    ]

    # attributes/features to save as npy
    E.HCM_variables = {
                       'txy_data': [
                                    'CT',       # corrected X, Y, T: this is = backwardX so far. holds at_HB and non_HB Move
                                    'CX', 
                                    'CY',    
                                    'recording_start_stop_time',
                                    ],

                        'timeSets': [ 
                                    'F_timeSet',             # corrected by 'at_device' spatial constraint
                                    'W_timeSet',
                                    'at_F_timeSet',         # at feeder
                                    'at_W_timeSet', 
                                    'F_timeSet_uncorrected', # raw photobeam/lickometer data
                                    'W_timeSet_uncorrected',
                                    'device_F_position_error_timeSet',   # photobeam when not at feeder
                                    'device_W_position_error_timeSet',
                                    'devices_overlap_error_timeSet',     # devices firing at the same time
                                    ],

                        'idxs': [
                                'idx_at_F',         # bool, Move at Feeder CT timestamps index
                                'idx_at_W',
                                'idx_at_HB',        # bool, at HomeBase
                                ],

                        # 'position_data': ['bin_times_24H_xbins%d_ybins%d' %(x, y) for (x, y) in E.xy_bins],

                        'homebase': [ 
                                    'rect_HB',      # nest/homebase rectangle, cage grid: (2,4)                
                                    'obs_HB'      # obs by Ethel
                                    ],

                        'qc': [
                            'flagged',              # possibly ignored
                            'flagged_msgs',            # reason
                            ], 

                        'to_compute': [
                                        'CT_at_HB', 'CT_out_HB', 
                                        'at_HB_timeSet',
                                        'idx_out_HB',
                                        'AS_idx'                
                                        ],


                    }

    E.HCM_derived = {
                    'position_data': ['bin_times_%s_xbins2_ybins4' %x for x in E.all_cycles] + \
                                    ['bin_times_%s_xbins12_ybins24' %x for x in E.all_cycles] + \
                                    ['bin_times_%s12bins_xbins2_ybins4' %x for x in ['', 'AS']] + \
                                    ['bin_times_%s12bins_xbins12_ybins24' %x for x in ['', 'AS']],
                                        

                    'active_states': [
                                    'AS_timeSet', 
                                    'IS_timeSet'
                                    ],

                    'bouts': [
                            'FB_timeSet', 
                            'WB_timeSet', 
                            'MB_timeSet', 
                            'MB_idx',
                            ],

                    'events': {
                                'ingestion':{
                                    'coeffs' : [
                                                'FC', 
                                                'LC'
                                                ],
                                    'tots' : [
                                            'FT', 
                                            'WT'
                                            ],
                                    'durs': ['FD','WD'],
                                    },

                                'M': [
                                    'delta_t',
                                    'distance',
                                    'velocity',
                                    'angle',
                                    'turning_angle'
                                    ],
                        },
                    }  

    E.features_by_type = {
                'active_states': ['ASP', 'ASN', 'ASD'],

                'totals': ['TF', 'TW', 'TM'], 
                
                'AS_intensities': ['FASInt', 'WASInt', 'MASInt'],

                'bouts' : [
                        'FBASR', 'FBN', 'FBS', 'FBD', 'FBI',
                        'WBASR', 'WBN', 'WBS', 'WBD', 'WBI',
                        'MBASR', 'MBN', 'MBS', 'MBD', 'MBI'
                        ],

                # 'events': [
                #         'FEN', 'FETD', 'FEAD',
                #         'WEN', 'WETD', 'WEAD'
                #         #move
                #         ]
                }
    
    E.features = [
                'ASP', 'ASN', 'ASD',
                'TF', 'TW', 'TM', 
                'FASInt', 'WASInt', 'MASInt',
                'FBASR', 'WBASR', 'MBASR',
                'FBN', 'WBN', 'MBN', 
                'FBS', 'WBS', 'MBS', 
                'FBD', 'WBD', 'MBD',
                'FBI', 'WBI', 'MBI'
                ]
    
    E.features_by_activity = [
                        'ASP', 'ASN', 'ASD',
                        'TF', 'FASInt', 'FBASR', 'FBN', 'FBS', 'FBD', 'FBI', 
                        'TW', 'WASInt', 'WBASR', 'WBN', 'WBS', 'WBD', 'WBI', 
                        'TM', 'MASInt', 'MBASR', 'MBN', 'MBS', 'MBD', 'MBI'
                        ]

    E.features_by_activity_dict = {
                        'AS' : ['ASP', 'ASN', 'ASD'],
                        'F' : ['TF', 'FASInt', 'FBASR', 'FBN', 'FBS', 'FBD', 'FBI'], 
                        'W' : ['TW', 'WASInt', 'WBASR', 'WBN', 'WBS', 'WBD', 'WBI'], 
                        'M' : ['TM', 'MASInt', 'MBASR', 'MBN', 'MBS', 'MBD', 'MBI']
                        }

    E.feature_pairs = [
        ['ASN', 'ASP'],
        ['ASD', 'ASP'],
        ['ASN', 'ASD'],

        ['ASP', 'TF'],
        ['ASP', 'TW'],
        ['ASP', 'TM'],

        ['ASP', 'FASInt'],
        ['ASP', 'WASInt'],
        ['ASP', 'MASInt'],

        ['TF', 'TW'],
        ['TF', 'TM'],
        ['TW', 'TM'],

        ['FASInt', 'WASInt'],
        ['FASInt', 'MASInt'],
        ['WASInt', 'MASInt'],

        ['FASInt', 'FBASR'],
        ['FASInt', 'FBS'],
        ['WASInt', 'WBASR'],
        ['WASInt', 'WBS'],
        ['MASInt', 'MBASR'],
        ['MASInt', 'MBS'],

        ['FBS', 'FBASR'],
        ['FBS', 'FBI'],
        ['FBS', 'FBD'],
        ['FBD', 'FBI'],

        ['WBS', 'WBASR'],
        ['WBS', 'WBI'],
        ['WBS', 'WBD'],
        ['WBD', 'WBI'],

        ['MBS', 'MBASR'],
        ['MBS', 'MBI'],
        ['MBS', 'MBD'],
        ['MBD', 'MBI'],
        ]



    # ordered_features = [
    #                     'TF', 'TW', 'TM', 
    #                     'ASP', 'ASN', 'ASD',
    #                     'FASInt', 'WASInt', 'MASInt',
    #                     'FBASR', 'WBASR', 'MBASR',
    #                     'FBN', 'WBN', 'MBN', 
    #                     'FBS', 'WBS', 'MBS', 
    #                     'FBD', 'WBD', 'MBD',
    #                     'FBI', 'WBI', 'MBI'
    #                     ]