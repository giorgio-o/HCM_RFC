"""
G.A.Onnis, 01.2017

Tecott Lab UCSF
"""


def add_variables_dict(experiment):
    """
    """
    # attributes/features to save as npy
    HCM_variables = {
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


                        'position_data': [
                            'bin_times_24h_xbins12_ybins24',    # total times, cage grid: xbins, ybins
                            'bin_times_24h_xbins2_ybins4'
                            ],

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

    HCM_derived = {
                    'active_states': ['AS_timeSet', 'IS_timeSet'],

                    'bouts': [
                            'FB_timeSet', 'WB_timeSet', 'MB_timeSet', 
                            'MB_idx', 
                            ],

                    'events': {
                        'M': [
                            'delta_t',
                            'distance',
                            'velocity',
                            'angle',
                            'turning_angle'
                            ],
                        },

                    # 'totals': ['TF', 'TW', 'TM'],
                    }   

    features_by_type = {
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
    
    features = [
                'ASP', 'ASN', 'ASD',
                'TF', 'TW', 'TM', 
                'FASInt', 'WASInt', 'MASInt',
                'FBASR', 'WBASR', 'MBASR',
                'FBN', 'WBN', 'MBN', 
                'FBS', 'WBS', 'MBS', 
                'FBD', 'WBD', 'MBD',
                'FBI', 'WBI', 'MBI'
                ]
    
    features_by_activity = [
                        'ASP', 'ASN', 'ASD',
                        'TF', 'FASInt', 'FBASR', 'FBN', 'FBS', 'FBD', 'FBI', 
                        'TW', 'WASInt', 'WBASR', 'WBN', 'WBS', 'WBD', 'WBI', 
                        'TM', 'MASInt', 'MBASR', 'MBN', 'MBS', 'MBD', 'MBI'
                        ]

    feature_pairs = [
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


    levels = ['strain', 'mouse', 'mouseday']

    experiment.HCM_variables = HCM_variables
    experiment.HCM_derived = HCM_derived
    experiment.features = features
    experiment.features_by_type = features_by_type
    experiment.features_by_activity = features_by_activity
    experiment.feature_pairs = feature_pairs
    experiment.levels = levels
        # 'coeff': ['FC', 'LC']
        # 'ingestion_totals' : ['FETS', 'WETS'],


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