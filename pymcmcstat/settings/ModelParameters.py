#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 09:13:03 2018

@author: prmiles
"""
# import required packages
import numpy as np
import math
import sys

class ModelParameters:
    '''
    MCMC Model Parameters.
    
    Example:
    ::
        
        mcstat = MCMC()

        mcstat.parameters.add_model_parameter(name = 'm', theta0 = 1., minimum = -10, maximum = 10)
        mcstat.parameters.add_model_parameter(name = 'b', theta0 = -5., minimum = -10, maximum = 100)
        
        mcstat.parameters.display_model_parameter_settings()
        
    This will display to screen:
    ::
        
        Sampling these parameters:
        name         start [   min,    max] N(  mu, sigma^2)
        m         :   1.00 [-10.00,  10.00] N(0.00, inf)
        b         :  -5.00 [-10.00, 100.00] N(0.00, inf)
    
    :Attributes:
        * :meth:`~add_model_parameter`
        * :meth:`~display_parameter_settings`
        * :meth:`~generate_default_name`
        
    '''
    def __init__(self):
        self.parameters = [] # initialize list
        self.description = 'MCMC model parameters'
        
    def add_model_parameter(self, name = None, theta0 = None, minimum = -np.inf,
                      maximum = np.inf, prior_mu = np.zeros([1]), prior_sigma = np.inf,
                      sample = True, local = 0):
        '''
        Add model parameter to MCMC simulation.
        
        :Args:
            * name (:py:class:`str`): Parameter name
            * theta0 (:py:class:`float`): Initial value
            * minimum (:py:class:`float`): Lower parameter bound
            * maximum (:py:class:`float`): Upper parameter bound
            * prior_mu (:py:class:`float`): Mean value of prior distribution
            * prior_sigma (:py:class:`float`): Standard deviation of prior distribution
            * sample (:py:class:`bool`): Flag to turn sampling on (True) or off (False)
            * local (:py:class:`int`): Local flag - still testing.
            
        The default prior is a uniform distribution from minimum to maximum parameter value.
        
        '''
        
        if name is None:
            name = self.generate_default_name(len(self.parameters))
            
        if theta0 is None:
            theta0 = 1.0
        
        # append dictionary element
        self.parameters.append({'name': name, 'theta0': theta0, 'minimum': minimum,
                                'maximum': maximum, 'prior_mu': prior_mu, 'prior_sigma': prior_sigma,
                                'sample': sample, 'local': local})
    
#    def default_parameter_settings(self):
#        
#        settings = {'name': self.generate_default_name(len(self.parameters)),
#                    'theta0': 1.0, 'minimum': -np.inf, 'maximum': np.inf, 'prior_mu': np.zeros([1]),
#                    'prior_sigma': np.inf, 'sample': True, 'local': 0}
#        
#        return settings
    
    def generate_default_name(self, nparam):
        '''
        Generate generic parameter name.
        For example, if :code:`nparam = 4`, then the generated name are::
        
            names = 'p_{3}'
        
        :Args:
            * **nparam** (:py:class:`int`): Number of parameter names to generate

        \\
        
        :Returns:
            * **name** (:py:class:`str`): Name based on size of parameter list
            
        '''
        return (str('$p_{{{}}}$'.format(nparam)))

    def _openparameterstructure(self, nbatch):
        
        # unpack input object
        parameters = self.parameters
        npar = len(parameters)
        
        # initialize arrays - as lists and numpy arrays (improved functionality)
        self._names = []
        self._initial_value = np.zeros(npar)
        self._value = np.zeros(npar)
        self._parind = np.ones(npar, dtype = int)
        self._local = np.zeros(npar)
        self._upper_limits = np.ones(npar)*np.inf
        self._lower_limits = -np.ones(npar)*np.inf
        self._thetamu = np.zeros(npar)
        self._thetasigma = np.ones(npar)*np.inf
                
        # scan for local variables
        ii = 0
        for kk in range(npar):
            if parameters[kk]['sample'] == 0:
                if parameters[kk]['local'] != 0:
                    self._local[ii:(ii+nbatch-1)] = range(0,nbatch)
                    npar = npar + nbatch - 1
                    ii = ii + nbatch - 1

            ii += 1 # update counter
            
        ii = 0
        for kk in range(npar):
            if self._local[ii] == 0:
                self._names.append(parameters[kk]['name'])
                self._initial_value[ii] = parameters[kk]['theta0']
                self._value[ii] = parameters[kk]['theta0']
                # default values defined in "Parameters" class in classes.py
                # define lower limits
                self._lower_limits[ii] = parameters[kk]['minimum']
                # define upper limits
                self._upper_limits[ii] = parameters[kk]['maximum']
                # define prior mean
                self._thetamu[ii] = parameters[kk]['prior_mu']
                if np.isnan(self._thetamu[ii]):
                    self._thetamu[ii] = self.value[ii]
                # define prior standard deviation
                self._thetasigma[ii] = parameters[kk]['prior_sigma']
                if self._thetasigma[ii] == 0:
                    self._thetasigma[ii] = np.inf
                # turn sampling on/off
                self._parind[ii] = parameters[kk]['sample']
            ii += 1 # update counter
            
        # make parind list of nonzero elements
        self._parind = np.flatnonzero(self._parind)
        
        self.npar = len(self._parind) # append number of parameters to structure
                
    def _results_to_params(self, results, use_local = 1):
    
        # unpack results dictionary
        parind = results['parind']
        names = results['names']
        local = results['local']
        theta = results['theta']

        for ii in range(len(parind)):
            if use_local == 1 and local[parind[ii]] == 1:
                name = names[ii] # unclear usage
            else:
                name = names[ii]
    
            for kk in range(len(self.parameters)):
                if name == self.parameters[kk]['name']:
                    # change NaN prior mu (=use initial) to the original initial value
                    if np.isnan(self.parameters[kk]['prior_mu']):
                        self.parameters[kk]['prior_mu'] = self.parameters[kk]['theta0']
                        
                    # only change if parind = 1 in params (1 is the default)
                    if self.parameters[kk]['sample'] == 1 or self.parameters[kk]['sample'] is None:
                        self.parameters[kk]['theta0'] = theta[parind[ii]]
                        
    
    def _check_initial_values_wrt_parameter_limits(self):
        # check initial parameter values are inside range
        if (self._initial_value[np.ix_(self._parind)] < self._lower_limits[np.ix_(self._parind)]).any() or (self._initial_value[np.ix_(self._parind)] > self._upper_limits[np.ix_(self._parind)]).any():
            # proposed value outside parameter limits
            sys.exit('Proposed value outside parameter limits - select new initial parameter values')
            
    def _check_prior_sigma(self, verbosity):
        self.__message(verbosity, 2, 'If prior variance <= 0, setting to Inf\n')
        self._thetasigma = self.__replace_list_elements(self._thetasigma, self.__less_than_or_equal_to_zero, float('Inf'))
        
    def __less_than_or_equal_to_zero(self, x):
        return (x<=0)

    def __replace_list_elements(self, x, testfunction, value):
        for ii in range(len(x)):
            if testfunction(x[ii]):
                x[ii] = value
        return x
    
    def __message(self, verbosity, level, printthis):
        printed = False
        if verbosity >= level:
            print(printthis)
            printed = True
        return printed
    
    def display_parameter_settings(self, verbosity = None, noadaptind = None):
        '''
        Display parameter settings
        
        :Args:
            * **verbosity** (:py:class:`int`): Verbosity of display output. :code:`0`
            * **noadaptind** (:py:class:`int`): Indices not to be adapted in covariance matrix. :code:`[]`
            
        '''
        parind = self._parind
        names = self._names
        value = self._initial_value
        lower_limits = self._lower_limits
        upper_limits = self._upper_limits
        theta_mu = self._thetamu
        theta_sigma = self._thetasigma
        
        if verbosity is None:
            verbosity = 0
            
        if noadaptind is None:
            noadaptind = []
        
        if verbosity > 0:
            print('\nSampling these parameters:')
            print('{:10s} {:>7s} [{:>6s}, {:>6s}] N({:>4s}, {:>4s})'.format('name',
                  'start', 'min', 'max', 'mu', 'sigma^2'))
            nprint = len(parind)
            for ii in range(nprint):
                if ii in noadaptind: # THIS PARAMETER IS FIXED
                    st = ' (*)'
                else:
                    st = ''
                if math.isinf(theta_sigma[parind[ii]]):
                    h2 = ''
                else:
                    h2 = '^2'
                    
                if value[parind[ii]] > 1e4:
                    print('{:10}: {:6.2g} [{:6.2g}, {:6.2g}] N({:4.2g},{:4.2f}{:s}){:s}'.format(names[parind[ii]], 
                      value[parind[ii]], lower_limits[parind[ii]], upper_limits[parind[ii]],
                      theta_mu[parind[ii]], theta_sigma[parind[ii]], h2, st))
                else:
                    print('{:10}: {:6.2f} [{:6.2f}, {:6.2f}] N({:4.2f},{:4.2f}{:s}){:s}'.format(names[parind[ii]], 
                      value[parind[ii]], lower_limits[parind[ii]], upper_limits[parind[ii]],
                      theta_mu[parind[ii]], theta_sigma[parind[ii]], h2, st))