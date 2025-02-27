#!/usr/bin/env python

"""
A plot module to draw contoured XYZ data onto a GMT map.
 
Copyright 2007 by Geoscience Australia

Usage: plot_gmt_xyz_contour.py <data_file>

"""


import os
import tempfile
import shutil
import numpy as num

import eqrm_code.plotting.plot_config as cfg
import eqrm_code.plotting.util_get_xyz_extent as ugxe
import eqrm_code.plotting.util_gmt_placement as ugp
import eqrm_code.plotting.util_gmt_annotation as uga
import eqrm_code.plotting.utilities as util


# default colour map
ColourMap = 'hazmap'


def plot_gmt_xyz_contour(data, output_file, title=None,
                         np_posn=None, s_posn=None,
                         cb_label=None, cb_steps=None,
                         colourmap=None, annotate=[], linewidth=1.0,
                         show_graph=False, map_extent=None, 
                         annot_lat = '30m', grid_lat = '30m',
                         annot_lon = '30m', grid_lon = '30m'):
    """A function to take XYZ data and plot contours onto a GMT map.
    
    data         an iterable of values in xyz format (lon, lat, val)
    output_file  path to file that should be generated (*.png, *.eps, etc)
    title        string used to title the plot
    np_posn      code string for north pointer placement, one of:
                     'C'   - centre of plot
                     'NE'  - inside plot, northeast corner
                     'CE'  - inside plot, centre of east edge
                     'NNE' - outside plot, north of NE corner
                     'ENE' - outside plot, east of NE corner
                      etc (see the documentation for 'placement')
    s_posn       code string for scale placement
                     see examples for 'np_posn' above
    cb_label     string containing the label text for the colorbar
                 (if not supplied, no colourbar)
    cb_steps     if supplied is a sequence of discrete values at
                 the colour changes
    colourmap    string containing name of required colormap
                 this could be a GMT name or a local name
    annotate     list of user annotations:
                     if None, no user or system annotations
                     if [],   only system annotations
                     else system and user annotations
    linewidth    width of countour lines in pixels
    show_graph   if True try to display final image in system-independant way
    map_extent   set the extent of the displayed map if supplied
                 (get extent from data if not supplied)
    annot_lat    Spacing in minutes for latitude annotations (e.g. 30m = 0.5 degress) 
    grid_lat     Spacing in minutes for latitude grid lines (e.g. 30m = 0.5 degress) 
    annot_lon    Spacing in minutes for longitude annotations (e.g. 30m = 0.5 degress) 
    grid_lon     Spacing in minutes for longitude grid lines (e.g. 30m = 0.5 degress) 
    """

    # create a scratch directory for ephemeral files
    tmp_dir = tempfile.mkdtemp(prefix='plot_gmt_xyz_contour_')

    # set up the GMT default values
    util.set_gmt_defaults(tmp_dir)

    # handle optional parameters
    if title is None:
        title = ''

    # if no colourmap supplied, use default
    c_map = ColourMap
    if colourmap is not None:
        c_map = colourmap
    if not os.path.exists(c_map):
        c_map = util.get_colourmap(c_map)
    

    # get maximum and minimum values
    max_val = util.max_nan(data[:,2])
    min_val = util.min_nan(data[:,2])

    # get extent of data
    if map_extent:
        extent = map_extent
    else:
        extent = ugxe.get_extent(data, margin=0)
    (ll_lat, ll_lon, ur_lat, ur_lon) = extent
    r_opt = '-R%f/%f/%f/%f' % (ll_lon, ur_lon, ll_lat, ur_lat)

    # set the -J option for Mercator projection
    j_opt = '-JM%fc' % cfg.MapWidthCentimetres

    # write a GMT XYZ file (required by GMT)
    my_xyz_file = os.path.join(tmp_dir, 'data.xyz')
    num.savetxt(my_xyz_file, data)

    # generate CPT file
    my_cpt_file = os.path.join(tmp_dir, 'data.cpt')
    if cb_steps is None:
        cb_steps = []
    if len(cb_steps) > 0:
        util.make_discrete_cpt(my_cpt_file, c_map, cb_steps)
    else:
        (start, stop, step) = util.get_scale_min_max_step(max_val, min_val)
        if os.path.exists(c_map):
            cm = c_map
        else:
            cm = util.get_colourmap(c_map)
        util.do_cmd('makecpt -C%s.cpt -T%f/%f/%f > %s'
                    % (cm, start, stop, step, my_cpt_file))

    # think of a postscript filename for plot output
    my_ps_file = os.path.join(tmp_dir, 'data.ps')

    # linewidth checking - if width < 1.0, no lines
    w_opt = '-W%.1f/0' % linewidth
    if linewidth < 1.0:
        w_opt = '-W+1'

    
    #Apply blockmean to avoid aliasing short wavelengths
    my_grd_file = os.path.join(tmp_dir, 'temp.grd')
    my_grd_file2 = os.path.join(tmp_dir, 'temp2.grd')
    my_grd_file3 = os.path.join(tmp_dir, 'temp3.grd')
    my_mask_file = os.path.join(tmp_dir, 'mask.grd')
    my_hzd_file = os.path.join(tmp_dir, 'hazard.grd')
    print my_grd_file    
    print my_grd_file2 
    
    
    util.do_cmd('surface %s -G%s %s -I0.001 -T0.5'
                % (my_xyz_file, my_grd_file,r_opt))
    util.do_cmd('grdimage %s -K -Q -C%s %s %s > %s'
                % (my_grd_file, my_cpt_file, r_opt, j_opt,
                   my_ps_file))
    
    """
    # METHOD 1
    util.do_cmd('surface %s -G%s %s -I0.001 -T0.5'
                % (my_xyz_file, my_grd_file,r_opt))
    
    util.do_cmd('grdmask %s %s -I0.001 -G%s -NNaN/NaN/1'
                % (my_xyz_file,r_opt,my_mask_file))
    
    util.do_cmd('grdmath %s %s MUL = %s'
                % (my_mask_file, my_grd_file,my_hzd_file))
    
    util.do_cmd('grdimage %s -K -Q -C%s %s %s > %s'
                % (my_hzd_file, my_cpt_file, r_opt, j_opt,
                   my_ps_file))
    """
    
    """
    # METHOD 2
    
    util.do_cmd('xyz2grd %s %s -I0.001 -G%s'
                % (my_xyz_file,r_opt,my_grd_file))
    
    util.do_cmd('grdsample %s %s -I0.005 -G%s'
                % (my_grd_file,r_opt,my_grd_file2))
    
    util.do_cmd('grdmask %s %s -I0.005 -G%s -NNaN/NaN/1'
                % (my_xyz_file,r_opt,my_mask_file))
    
    util.do_cmd('grdmath %s %s MUL = %s'
                % (my_mask_file, my_grd_file2,my_hzd_file))
    
    util.do_cmd('grdimage %s -K -Q -C%s %s %s > %s'
                % (my_hzd_file, my_cpt_file, r_opt, j_opt,
                   my_ps_file))
    """
    
    """
    # METHOD 3
    util.do_cmd('xyz2grd %s %s -I0.001 -G%s'
                % (my_xyz_file,r_opt,my_grd_file))
                
    util.do_cmd('grdmask %s %s -I0.001 -G%s -NNaN/NaN/1'
                % (my_xyz_file,r_opt,my_mask_file))
    
    util.do_cmd('grdmath %s %s MUL = %s'
                % (my_mask_file, my_grd_file,my_hzd_file))
    
    util.do_cmd('psxy %s %s %s -W0.5p/100 -G200 -O -K -M >%s'
                % (my_xyz_file, r_opt,j_opt,my_ps_file)) 
    
    util.do_cmd('grdimage %s -K -Q -C%s %s %s > %s'
                % (my_hzd_file, my_cpt_file, r_opt, j_opt,
                   my_ps_file))
    """
    
    """
    # METHOD 4
    util.do_cmd('xyz2grd %s %s -I0.001 -G%s'
                % (my_xyz_file,r_opt,my_grd_file))
                
    util.do_cmd('grdmask %s %s -I0.001 -G%s -NNaN/NaN/1'
                % (my_xyz_file,r_opt,my_mask_file))
    
    util.do_cmd('grdmath %s %s MUL = %s'
                % (my_mask_file, my_grd_file,my_hzd_file))
    
    util.do_cmd('psxy %s %s %s -W0.5p/100 -K >%s'
                % (my_xyz_file, r_opt,j_opt,my_ps_file)) 
    
    util.do_cmd('grdimage %s -K -Q -C%s %s -O %s > %s'
                % (my_hzd_file, my_cpt_file, r_opt, j_opt,
                   my_ps_file))
    util.do_cmd('psxy %s %s %s -W0.5p/100 -M -O -K >%s'
                % (my_xyz_file, r_opt,j_opt,my_ps_file))                          
     """
               
    
   
    # draw the coast
    util.do_cmd('pscoast %s -K -O %s -Df -W -S192/216/255 >> %s'
                % (r_opt, j_opt, my_ps_file))

    # do annotations
    if annotate is not None:
        ok_opt = '-K -O'
        jok_opt = '%s %s' % (ok_opt, j_opt)
        uga.generated_annotation(tmp_dir, my_ps_file, extent,
                                 cfg.MapWidthCentimetres, jok_opt)
        uga.user_annotation(tmp_dir, my_ps_file, extent, j_opt, ok_opt, annotate)

    # draw the colorbar
    if cb_label:
        x_offset = cfg.MapWidthCentimetres + 0.5 
        y_offset = cfg.MapHeightCentimetres/2.0 - 1.75
        util.do_cmd('psscale -K -O -E -C%s -D%.1fc/%.1fc/9.0c/0.8c "-B:%s:" >> %s'
                    % (my_cpt_file, x_offset, y_offset, cb_label, my_ps_file))

    # draw the rest of the map
    t_opt = ''
    if np_posn:
        t_opt = ugp.get_northpointer_placement(np_posn, extent)
    l_opt = ''
    if s_posn:
        l_opt = ugp.get_scale_placement(s_posn, extent)

    util.do_cmd('psbasemap %s -O %s "-Ba%s/a%s:.%s:WSen" -Bg%s/g%s %s %s >> %s'
                % (r_opt, j_opt, annot_lon, annot_lat, title, grid_lon, grid_lat, t_opt, l_opt, my_ps_file))

    # convert PS to required type
    (_, file_extension) = output_file.rsplit('.', 1)
    try:
        t_opt = util.Extension2TOpt[file_extension.lower()]
    except KeyError:
        raise RuntimeError("Can't handle plot outputfile type: %s" %
                           file_extension)

    util.do_cmd('ps2raster %s -A -T%s' % (my_ps_file, t_opt))
    (my_output_file, _) = my_ps_file.rsplit('.', 1)
    my_output_file += '.' + file_extension
    shutil.copyfile(my_output_file, output_file)

    # if it's required to show the graph ...
    # TODO: Experimental - leave?
    if show_graph:
        import sys
        if sys.platform == 'win32':
            os.startfile(my_output_file)
        else:
            import subprocess
            try:
                subprocess.Popen(['xdg-open', my_output_file])
            except OSError:
                print("Sorry, the 'xdg-open' application is required to "
                      "automatically display images.\nYou can see the image "
                      "in file %s." % output_file)

    # remove the temp directory
    shutil.rmtree(tmp_dir)


