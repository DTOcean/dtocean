# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Francesco Ferri, Rui Duarte
#    Copyright (C) 2017-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division

import operator
from decimal import Decimal

import numpy as np


def make_tide_statistics(dictinput,
                         ds=0.01):
    
    '''
     Function that selects the subset of current fields to be run, based on the
     statistical analysis described in Deliverable 2.4
     Written by JF Filipot and M Peray, October 1st, 2015
     Fixed by Mathew Topper (mathew.topper@dataonlygreater.com)
     contact: jean.francois.filipot@france-energies-marines.org
    
     function input:
     dictinput = { 'U':U, 'V':V, 'TI':TI, 'SSH':SSH, 't':t, 'xc':xc, 'yc':yc,
                   'x':x, 'y':y, 'ns':ns}
         U: east-west current fields (np.shape(U)=[nx,ny,nt])
         V: north-south current fields (np.shape(V)=[nx,ny,nt])
         x: east-west coordinate (len(x)=nx)
         y: north-south coordinate (len(y)=ny)
         t: time vector (len(t)=nt)
         xc: east-west coordinate of the location of interest (where the time
         series for the statistical analysis will be extracted, len(xc)=1).
         yc: north-east coordinate of the location of interest (where the time
         series for the statistical analysis will be extracted, len(xc)=1).
         ns number of scenarii to be played (len(ns)=1).
    ds: 2D PDF bin width for secondary component velocity
    
     function output:
    
     dictoutput = {'V': V, 'U':U, 'p':p, 'TI':TI, 'x':x, 'y':y, 'SSH':SSH}
         U: east-west current fields (np.shape(U)=[ny,nx,ns])
         V: north-south current fields (np.shape(V)=[ny,nx,ns])
         p: probability of occurence of each scenario (len(p)=ns)
         x: east-west coordinate (len(x)=nx)
         y: north-south coordinate (len(y)=ny)
         t: time vector (len(t)=ns)
    '''
    
    uf = dictinput['U']
    vf = dictinput['V']
    TI = dictinput['TI']
    SSH = dictinput['SSH']
    t = dictinput['t']
    x = dictinput['x']
    y = dictinput['y']
    xc = dictinput['xc']
    yc = dictinput['yc']
    ns = dictinput['ns']
    
    if ns < 1:
        err_str = "The number of scenarii must be at least one"
        raise ValueError(err_str)
    
    nearest_x_idx, nearest_y_idx = _get_nearest_xy_idx(x, y, xc, yc)
    
    u = uf[nearest_x_idx, nearest_y_idx, :]
    v = vf[nearest_x_idx, nearest_y_idx, :]
    
    if np.isnan(u).any() or np.isnan(v).any():
        
        errStr = ("Time series at extraction point is not valid. Does the "
                  "given point lie within the lease area?")
        raise ValueError(errStr)
    
    u_range = u.max() - u.min()
    v_range = v.max() - v.min()
    
    if u_range > v_range:
        
        principal = u
        secondary = v
    
    else:
        
        principal = v
        secondary = u
    
    pmin, pmax = principal.min(), principal.max()
    smin, smax = _get_range_at_interval(secondary, ds)
    
    p_samples = ns + 1
    s_samples = _get_n_samples(smin, smax, ds)
    
    p_bins = np.linspace(pmin, pmax, p_samples)
    s_bins = np.linspace(smin, smax, s_samples)
    p_bin_centers = _get_bin_centers(p_bins)
    s_bin_centers = _get_bin_centers(s_bins)
    
    ps_pdf = _get_ps_pdf(principal,
                         secondary,
                         p_samples,
                         s_samples,
                         p_bins,
                         s_bins)
    
    (sample_secondary_value,
     sample_probability) = _get_samples(s_bin_centers,
                                        ps_pdf,
                                        ns)
    
    if u_range > v_range:
        
        sample_u_values = p_bin_centers
        sample_v_values = sample_secondary_value
    
    else:
        
        sample_u_values = sample_secondary_value
        sample_v_values = p_bin_centers
    
    inds = _get_time_series_indexes(u,
                                    v,
                                    sample_u_values,
                                    sample_v_values)
    
    V = vf[:, :, inds]
    U = uf[:, :, inds]
    t = t[inds]
    p = sample_probability
    TI = TI[:, :, inds]
    SSH = SSH[:, :, inds]
    
    # remove 0 probability bins
    zero_pb = np.where(p == 0.)
    U = np.delete(U, zero_pb, 2)
    V = np.delete(V, zero_pb, 2)
    SSH = np.delete(SSH, zero_pb, 2)
    TI = np.delete(TI, zero_pb, 2)
    p = np.delete(p, zero_pb)
    t = np.delete(t, zero_pb)
    ns = ns - np.array(zero_pb).size
    
    # output
    dictoutput = {'U': U,
                  'V': V,
                  'SSH': SSH,
                  'TI': TI,
                  'x': x,
                  'y': y,
                  'p': p,
                  't': t,
                  'ns': ns
                  }
    
    return dictoutput


def _get_nearest_xy_idx(x, y, xc, yc):
    
    nearest_x_idx = (np.abs(x - xc)).argmin()
    nearest_y_idx = (np.abs(y - yc)).argmin()
    
    return nearest_x_idx, nearest_y_idx


def _get_range_at_interval(v, interval):
    
    """Adjust the range of the data to fit a given interval"""
    
    range_max = np.max(v)
    range_min = np.min(v)
    
    numerator = Decimal(str(range_max - range_min))
    denominator = Decimal(str(interval))
    
    remainder = numerator % denominator
    adjust = float(denominator - remainder)
    
    range_max = range_max + 0.5 * adjust
    range_min = range_min - 0.5 * adjust
    
    return range_min, range_max


def _get_n_samples(range_min, range_max, interval):
    
    numerator = Decimal(str(range_max - range_min))
    denominator = Decimal(str(interval))
    
    quotient, remainder = divmod(numerator, denominator)
    
    if remainder != 0:
        
        err_msg = ("Given interval does not divide range exactly. Remainder "
                   "of {} detected.").format(remainder)
        raise ValueError(err_msg)
    
    n_samples = int(quotient) + 1
    
    return n_samples


def _get_bin_centers(bins):
    
    delta = (bins[1:] - bins[:-1]) / 2
    bin_centers = bins[:-1] + delta
    
    return bin_centers


def _get_ps_pdf(p, s, p_samples, s_samples, p_bins, s_bins):
    
    pdf = np.zeros((p_samples - 1, s_samples - 1))
    
    for idxp in range(p_samples - 1):
        for idxs in range(s_samples - 1):
            
            if idxp == p_samples - 2:
                p_upper_op = operator.le
            else:
                p_upper_op = operator.lt
            
            if idxs == s_samples - 2:
                s_upper_op = operator.le
            else:
                s_upper_op = operator.lt
            
            ps_in_bin = ((p >= p_bins[idxp]) &
                         (p_upper_op(p, p_bins[idxp + 1])) & 
                         (s >= s_bins[idxs]) & 
                         (s_upper_op(s, s_bins[idxs + 1])))
            
            n_in_bin = ps_in_bin.astype(int)
            pdf[idxp, idxs] = np.sum(n_in_bin)
    
    pdf = pdf / len(p)
    
    assert np.isclose(np.sum(pdf), 1)
    
    return pdf


def _get_samples(secondary_bin_centers,
                 pdf,
                 ns):
    
    sample_secondary_value = np.zeros(ns)
    sample_probability = np.zeros(ns)
    
    for i in range(ns):
        
        secondary_pdf = pdf.take(indices=i, axis=0)
        
        # Avoid division by 0
        if np.sum(secondary_pdf) == 0.:
            
            secondary_value = 0.
            denominator = 0.
        
        else:
            
            numerator = np.sum(secondary_bin_centers * secondary_pdf)
            denominator = np.sum(secondary_pdf)
            
            secondary_value = numerator / denominator
        
        sample_secondary_value[i] = secondary_value
        sample_probability[i] = denominator
    
    assert np.isclose(np.sum(sample_probability), 1)
    
    return sample_secondary_value, sample_probability


def _get_time_series_indexes(u,
                             v,
                             sample_u_values,
                             sample_v_values):
    
    ns = len(sample_u_values)
    itmin = np.zeros(ns)
    
    for i in range(ns):
        itmin[i] = np.argmin(abs(sample_u_values[i] - u) +
                                             abs(sample_v_values[i] - v))
    
    # convert itmin to integer
    ind = itmin.astype(int)
    inds = ind.tolist()
    
    return inds
