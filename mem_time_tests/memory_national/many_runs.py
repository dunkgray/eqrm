"""
Run multipe EQRM simulations, to get time and memory metrics. 
"""

import subprocess 
import os

from scipy import arange
import eqrm_code.util
from eqrm_code import util
from eqrm_code.parse_in_parameters import eqrm_data_home, get_time_user, \
     ParameterData, create_parameter_data, eqrm_flags_to_control_file

from eqrm_code.multiple_runs import multi_run, mpi_command, create_sites_list

from eqrm_code.analysis import main

def create_base():
    """
    Set up for 19 events, 5 gmpe_max, 7 periods, 11 spawning, 3 rec mod. 
    2 Surfaces.
    
    17277 sites
    """
    sdp = ParameterData()
    
    # Operation Mode
    sdp.run_type = "hazard" 
    sdp.is_scenario = False
    sdp.site_tag = "bench"
    sdp.return_periods = [100.75, 200.0, 300.0, 400.0, 500.0, 
    600.0, 700.0, 800.0, 900]
    
    sdp.input_dir = os.path.join(eqrm_data_home(), 'test_national',
                      'memory_input')
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','trial_matrix')
    
    sdp.use_site_indexes = True #False 
    sdp.site_indexes = [1]
    sdp.event_control_tag = "use" 
    sdp.zone_source_tag = ""
    
    # Probabilistic input
    sdp.prob_number_of_events_in_zones = [5,5,5,4]
    
    # Attenuation
    sdp.atten_collapse_Sa_of_atten_models = False #True
    sdp.atten_variability_method = 1
    sdp.atten_spawn_bins = 11
    sdp.atten_periods = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
    sdp.atten_threshold_distance = 400
    sdp.atten_override_RSA_shape = None
    sdp.atten_cutoff_max_spectral_displacement = False
    sdp.atten_pga_scaling_cutoff = 2
    sdp.atten_smooth_spectral_acceleration = None
    
    # Amplification
    sdp.use_amplification = False #True
    sdp.amp_variability_method = None
    sdp.amp_min_factor = 0.6
    sdp.amp_max_factor = 10000
    
    # Save
    sdp.save_hazard_map = True
    sdp.save_motion = False
    
    return sdp

    
def create_base_risk():
    """
    Using newcastle data.
    
    """
    
    sdp = ParameterData()
    
    # Operation Mode
    sdp.run_type = "risk_csm" 
    sdp.is_scenario = False
    sdp.site_tag = "newc"
    sdp.atten_periods =  [0.1, 0.2, 1.0]
    
    sdp.return_periods = [100.75, 200.0, 300.0, 400.0, 500.0, 
    600.0, 700.0, 800.0, 900]
    
    sdp.input_dir = os.path.join(eqrm_data_home(), 'test_national',
                      'memory_input')
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','trial_matrix')
    
    sdp.use_site_indexes = True #False 
    sdp.site_indexes = [1]
    sdp.event_control_tag = "use" 
    sdp.zone_source_tag = ""
    
    # Probabilistic input
    sdp.prob_number_of_events_in_zones = [5,5,5,4]
    
    # Attenuation
    sdp.atten_collapse_Sa_of_atten_models = False #True
    sdp.atten_variability_method = 1
    sdp.atten_spawn_bins = 11
    sdp.atten_periods = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]
    sdp.atten_threshold_distance = 400
    sdp.atten_override_RSA_shape = None
    sdp.atten_cutoff_max_spectral_displacement = False
    sdp.atten_pga_scaling_cutoff = 2
    sdp.atten_smooth_spectral_acceleration = None
    
    # Amplification
    sdp.use_amplification = False #True
    sdp.amp_variability_method = None
    sdp.amp_min_factor = 0.6
    sdp.amp_max_factor = 10000
    
    # Buildings
    sdp.buildings_usage_classification = "FCB" 
    sdp.buildings_set_damping_Be_to_5_percent = False

    # Capacity Spectrum Method
    sdp.csm_use_variability = False
    sdp.csm_variability_method = None
    sdp.csm_standard_deviation = 0.3
    sdp.csm_damping_regimes = 0
    sdp.csm_damping_modify_Tav = True
    sdp.csm_damping_use_smoothing = True
    sdp.csm_hysteretic_damping = "curve" 
    sdp.csm_SDcr_tolerance_percentage = 1
    sdp.csm_damping_max_iterations = 7

    # Loss
    sdp.loss_min_pga = 0.05
    sdp.loss_regional_cost_index_multiplier = 1.4516
    sdp.loss_aus_contents = 0

    # Save
    sdp.save_hazard_map = True
    sdp.save_total_financial_loss = True
    sdp.save_hazard_map = True
    
    return sdp


def risk_simulation():
    """
    
   
    """
    runs = []
    num_sources = 6  
    
    ### 
    
    
    sdp = create_base_risk()
    sdp.atten_collapse_Sa_of_atten_models = True 
    sdp.atten_variability_method = 2
    ###
    sites_needed = 1
    events = 80
    ###
    events_source = events/num_sources
    num_sites = 17278
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    dir_last  = 'initial_risk_' + str(events) + \
            "_sites" + str(sites_needed)
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output_riskB', dir_last)
    runs.append({"processes":1, "sdp":sdp})

 
    sdp = create_base_risk()   
    sdp.atten_collapse_Sa_of_atten_models = True 
    sdp.atten_variability_method = 2
    ###
    sites_needed = 2
    events = 80
    ###
    events_source = events/num_sources
    num_sites = 17278
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    dir_last  = 'initial_risk_' + str(events) + \
            "_sites" + str(sites_needed)
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output_riskB', dir_last)
    runs.append({"processes":1, "sdp":sdp})

    sdp = create_base_risk()  
    sdp.atten_collapse_Sa_of_atten_models = True 
    sdp.atten_variability_method = 2  
    ###
    sites_needed = 1
    events = 800
    ###
    events_source = events/num_sources
    num_sites = 17278
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    dir_last  = 'initial_risk_' + str(events) + \
            "_sites" + str(sites_needed)
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output_risk', dir_last)
    #runs.append({"processes":1, "sdp":sdp})
    
 
    sdp = create_base_risk()   
    sdp.atten_collapse_Sa_of_atten_models = True 
    sdp.atten_variability_method = 2
    ###
    sites_needed = 10
    events = 800
    ###
    events_source = events/num_sources
    num_sites = 17278
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    dir_last  = 'initial_risk_' + str(events) + \
            "_sites" + str(sites_needed)
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output_risk', dir_last)
    #runs.append({"processes":1, "sdp":sdp})
    

    sdp = create_base_risk()  
    sdp.atten_collapse_Sa_of_atten_models = True 
    sdp.atten_variability_method = 2  
    ###
    sites_needed = 1
    events = 80000
    ###
    events_source = events/num_sources
    num_sites = 17278
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    dir_last  = 'initial_risk_' + str(events) + \
            "_sites" + str(sites_needed)
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output_risk', dir_last)
    #runs.append({"processes":1, "sdp":sdp})

    
    return runs
    
def old_max_simulation():
    """
    attribute	#	JSON attribute
    events	8,000,000*	len_events
    Sites 	3,000,000	 len_block_sites
    periods	10	len_atten_periods
    return periods	10	len_return_periods
    source zones	150	len_source_zones
    SA surfaces (Sa soil and Sa bed rock)	2	len_SA_surfaces
# of GM models	5	len_max_GMPEs

   Note, i'm not doing 150 source zones.  The mem estimate's have been
   good, without taking it into account.
   """
    runs = []
    num_sources = 4
    sdp = create_base()
    
    ###
    sdp.site_indexes = range(1, 400)
    events = 80000  
    events = 800 
    events = 8000000 
    events = 80    
    sdp.return_periods = [100.75, 200.0, 300.0, 400.0, 500.0, 
    600.0, 700.0, 800.0, 900, 1000.]
    sdp.atten_periods =  [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sdp.use_amplification = True
    sdp.atten_spawn_bins = 1
    sites_needed = 17278
    sdp.file_parallel_log_level = 'debug'
    sdp.use_site_indexes = False
    ###
    num_sites = 17277
    events_source = events/num_sources
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.prob_number_of_events_in_zones[0] += events%num_sources
    sdp.use_site_indexes = True
    sdp.site_indexes = create_sites_list(num_sites, sites_needed)
    assert sum(sdp.prob_number_of_events_in_zones) == events
    assert len(sdp.site_indexes) == sites_needed
    sdp.event_control_tag = "4GMPE" 
    dir_last  = 'old_max_sim_again_' + str(sum(
            sdp.prob_number_of_events_in_zones)) + \
            "_sites" + str(len(sdp.site_indexes))
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output', dir_last)
    runs.append({"processes":1, "sdp":sdp})

    return runs

def build_runs_list_large_standard():
    runs = []
    num_sources = 4

    sdp = create_base()
    sdp.site_indexes = range(1, 400)
    sdp.prob_number_of_events_in_zones =  [20000] * 4
    sdp.atten_periods =  [0.0, 0.3, 1.0]
    sdp.atten_spawn_bins = 5
    sdp.event_control_tag = "4GMPE" 
    dir_last  = 'big_standard_' + str(sum(
            sdp.prob_number_of_events_in_zones)) + \
            "_sites" + str(len(sdp.site_indexes))
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                  'memory_output', dir_last)
    runs.append({"processes":1, "sdp":sdp})

    return runs

def build_runs_list():
    runs = []
    num_sources = 4

    # The base run
    sdp = create_base()
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','trial_matrix')
    runs.append({"processes":1, "sdp":sdp})

    # Testing parallel
    sdp = create_base()
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','trial_parallel')
    sdp.site_indexes = [1, 2]
    runs.append({"processes":2, "sdp":sdp})

    # Test more events 
    sdp = create_base()
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','more_events')
    sdp.site_indexes = [1, 2,3,4]
    sdp.prob_number_of_events_in_zones = \
        [x*4 for x in sdp.prob_number_of_events_in_zones]
    runs.append({"processes":2, "sdp":sdp})

    # Test small and larger event set
    base = [5,5,5,4]
    event_lists = [base, [x*200 for x in base]]
    for event_list in event_lists:

        # Test more rec mod
        sdp = create_base()
        dir_last  = 'more_rec_mod_events' + str(sum(event_list))
        sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                      'memory_output', dir_last)
        sdp.site_indexes = [1]
        sdp.prob_number_of_events_in_zones = event_list       
        sdp.zone_source_tag = "rec_mod"
        runs.append({"processes":1, "sdp":sdp})

        # Testing more GMPE's
        sdp = create_base()
        dir_last  = 'more_gmpe_events' + str(sum(event_list))
        sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                      'memory_output', dir_last)
        sdp.site_indexes = [1]
        sdp.prob_number_of_events_in_zones = event_list
        sdp.event_control_tag = "GMPE" 
        runs.append({"processes":1, "sdp":sdp})
        
        # Testing more periods's
        sdp = create_base()
        dir_last  = 'more_periods_events' + str(sum(event_list))
        sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                      'memory_output', dir_last)
        sdp.site_indexes = [1] 
        sdp.prob_number_of_events_in_zones = event_list
        sdp.atten_periods = arange(0,2.1, 0.1)
        runs.append({"processes":1, "sdp":sdp})
        
        # Test more spawning 
        sdp = create_base()
        dir_last  = 'more_spawning_events' + str(sum(event_list))
        sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                      'memory_output', dir_last)
        sdp.site_indexes = [1]
        sdp.prob_number_of_events_in_zones = event_list
        sdp.atten_variability_method = 1
        sdp.atten_spawn_bins = 44
        runs.append({"processes":1, "sdp":sdp})


    # spawning all sites
    sdp = create_base()
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','bigger_spawning')
    events = 50
    events_source = events/num_sources
    sdp.prob_number_of_events_in_zones = [events_source]*num_sources
    sdp.atten_variability_method = 1
    sdp.atten_spawn_bins = 100
    sdp.use_site_indexes = False 
    runs.append({"processes":1, "sdp":sdp})

    # increasing events, 2 sites
    for events in [1000, 10000, 100000]:
        sdp = create_base()
        sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                      'memory_output','events_' + str(events))
        events_source = events/num_sources
        sdp.prob_number_of_events_in_zones = [events_source]*num_sources
        sdp.site_indexes = [1, 2]
        runs.append({"processes":1, "sdp":sdp})

    
    # Testing all sites
    sdp = create_base()
    sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                      'memory_output','trial_all_sites')
    sdp.use_site_indexes = False 
    runs.append({"processes":2, "sdp":sdp})
    
    # increasing events, all sites
    for events in [1000, 5000]: #, 100000]:
        for proc in [1]:
            sdp = create_base()
            sdp.site_indexes = range(1, 500)
            dir_name = 'sites_' + str(len(sdp.site_indexes)) + '_events_' + \
                str(events) + \
                '_' + 'proc_'+ \
                str(proc)
            sdp.output_dir = os.path.join(eqrm_data_home(), 'test_national', 
                                          'memory_output',
                                          dir_name)
            events_source = events/num_sources
            sdp.prob_number_of_events_in_zones = [events_source]*num_sources
            runs.append({"processes":proc, "sdp":sdp})

    return runs

    
def test_run():
    runs = risk_simulation()
    multi_run(runs)
    #multi_run(old_max_simulation())
    #multi_run(build_runs_list())
    #multi_run(build_runs_list_large_standard())
    
    
#-------------------------------------------------------------
if __name__ == "__main__":
    test_run()
