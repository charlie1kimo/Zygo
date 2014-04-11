"""
align.py
8/24/13 this is the master version bk
Script for solving for met5 system alighment values

Importand convention for names used in script

self.A    
A<2darray>  MxN Sensitivity or Design matrix contianing
            the independent variables for each N Perturbation.
            M is the number of measured variable(data points)
            N is the number of a N-dimensional parameter vector
            of the regression coefficients (number of terms being solved for)

self.z                    
z<1darray>  Vector length M, Measured or Dependent variables data points
            also known as measured values for the list allterms

self.weights
weights<1darray>  Vector length M containg weights for each M measured
                   variable(data points). 
self.p
p<1darray>  N-dimensional parameter vector(compensator values also known as
              perturbation values or independent variables).


Method:
Weighted least squares is used to solve for p
Solves for p:
z = A*p (more persicley solves z = A*p + e where are e are random unknown
            varitions measured values of z)

The solution method:
W = diag(weights) #converts weights into a NxN diagonal matrix
p = inv((At.W.A)).At.W.z   (. is matrix dot multiply, At is transform of A)
matrix inv fuction done with singular-value decomposition (SVD).
"""
'''
When reading code in this module after the passage of time I find it difficult
to remember what all the names of items or terms used all mean. To help with
this problem I added these notes. bk 8/24/2013

The solution methods used are based on sensitivity values for given
compensators. The solution values are the amounts to adjust compensators needed
to match the observed measured condition or error. Luc Girard choose to us the
name Perturbations to refer to the parameters being adjusted or perturbed in the
raytrace sensitivity analysis. So Compensator and Perturbation are the same
thing. The Sensitivity analysis may contain many perturbations that are not used
so we have the term usedperts to mean perturbations used in the solution
analysis. So usedperts simply means the perturbations used in the current
solution analysis. 
Examples of perturbation names:
xtilt_m1       -> tilt of m1 mirror (small mirror) later changed to yrot_m1
xtrans_m1

A perturbation causes a measurable effect of the system (Dependent Variables)
and these are called terms in this module and I named this list allterms. 
Example of terms:
field_0_z4   -> measured Z4 value in center field
field_0_z7
field_0_z8

The algorithms used assumes that the sensitivity values are not linear. An
iteration process is used to bracket and interprete the used sensitivity
amounts to best fit solution compensator values.   

Track Length control:
Track Length control is achieved by forcing the solved difference between
ztrans_obj and ztrans_retro to meet a value. This is done by adding to the
self.z array
z<1darray>  Vector length M, Measured or Dependent variables data points
            also known as measured values for the list allterms
a target difference value for ztrans_obj - ztrans_retro and also by added
to the perturbations a entry for 'ztrans_obj and ztrans_retro' Invoking is
done by setting the weight to 1. or greater. Weight of 0. for
ztrans_obj - ztrans_retro will cause the solver to ignore this item.

ztrans_obj - ztrans_retro is not a measured item it is a value that will force
the solver to make zero if weight not set to 0 therefore causing the tracklengh
to change

More Notes:
The CV sensitivity files are expected to be effect of the change in a perameter 
(independent variable) on the terms(dependent variables).
The solved N-dimensional parameter vector(compensator values also known as
              perturbation values or independent variables are the best fit
              of the parameter errors that caused the measured dependent
              variables or terms. In other works to correct the system
              one most adjust the compensator in the opposite direction.

'''
__version__ = '0.11.0'
__owner__ = 'bkestner'

'''
History:
3/11/14 cc 0.11.0 fixed field coord bugs
3/9/14  bk 0.10.0 weeks work while in hawiiai
2/18/14 bk 0.9.0 terms converted to rms in make_z_from_gnts
2/16/14 bk 0.8.0 many changes
2/11/14 bk 0.7.0 changed sensitivty files that reflect better real needs
                    new files are scaled in single pass wfe
                    xtilt is now yrot
                    ytilt is now xrot
                    signs have changed
10/1/13 bk 0.6.0 added units to disp_solve()
9/7/113 bk 0.5.0 added make_z_zero() more track_length code
9/5/13 bk 0.4.0 changed name set_track_length()
8/25/13 bk 0.3.0 renamed from align2.py to align.py
8/24/13  bk added docs and fixed .index bug in disp_solve
12/2/12  bk modified make_z_from_GntSet() to take 'root','ext'
11/29/12 bk converted tuples to list types in _start()
11/26/12 bk added make_z_from_GntSet()
11/25/12 adding comments to align2.py pre saved align2.py as align2_arc.py
            upgraded many docs added get_GntSet() other small changes.
before 11/25/12:
align2.py came from align.py
align.py came from met5_plot_sens<int>.py devopment series
'''
import os
import numpy
import math
import ompysys
import ompy.calcfuncs as calcfuncs
from numpy.linalg import lstsq
packagePath = os.path.split(os.path.abspath(__file__))[0]
class Align(object):
    """
    Class to create and manage methods for solving for
    MET5 system compensator alignment ajustments.
    """
    def __init__(self,**kwds):
        """
        more docs needed
        Optinal kwds:
        field_coord=<list> default  [(0,0),(+.5,+.5),(+.5,-.5),(-.5,-.5),(-.5,+.5)]
                                detumins which fields to accept and there sort order
        """
        self.packagePath = os.path.split(os.path.abspath(__file__))[0]
        #raw_input('packagePath: %s' % self.packagePath)
        if not 'field_coord' in kwds:
            self.field_coord = [(0,0),(+1,+1),(+1,-1),(-1,-1),(-1,+1)]
        else:
            field_coord = kwds['field_coord']
            if not isinstance(field_coord,(basestring,list,float,int)):
                raise ValueError, 'field_coord not valid'
            if isinstance(field_coord,basestring):
                self.field_coord = eval(field_coord)
            elif isinstance(field_coord,(float,int)):
                float(field_coord)
                v = field_coord
                self.field_coord = [(0,0),(+v,+v),(+v,-v),(-v,-v),(-v,+v)]
            else:
                self.field_coord = kwds['field_coord']
                
        allterms,weights,usedperts,sens_filename,\
        sens_filenames,force,zlist = _start()
        self.zlist = zlist
        self.allterms = allterms  #items t measure
        self.weights = weights
        self.usedperts = usedperts #compensators
        self.force = force #values to force in solution
        self.sens_filenames = sens_filenames
        self.trialfilename = None
        self.trail_colum = None
        self.A = None  #sens matrix
        self.z = None  #measured items should have nominal design subbtracted
        self.z_with_nominal = None # measured terms b4 subtract nominal desgign

        self.p = None  #solution vetor for compensators
        self.res = None
        #self.fields_sens looks like the sensitivity used for the first solve
           #before the non linear is used.
           #keys are fieldnames so it is used to get fieldnames
        self.fields_sens= self.read_cv_file(sens_filename)
        amounts,units = self.get_amounts_units(self.fields_sens)
        self.amounts = amounts
        self.units = units
        self.set_sens_coeffs() # (True)will plot resdiusl fits
        self.set_A()
        self.tracklength = None
        self.dtarget_tracklength = None
        self.target_tracklength = None
        self.new_tracklength = None
        self.zt_obj_zt_ret = 0.0 # Value of ztrans_obj - ztrans_retro
        

    def set_tracklength(self,value):
        """
        sets self.tracklength
        This is the measured tracklength that goes with a measurment of the
         dependent variables.
        Its Value is not needed if the weight for term
         'ztrans_obj - ztrans_ret' is set to 0. Meaning tracklength is not
          being controled.
          
        Inputs:
        value<float> measured track length (mm)
        """
        self.tracklength = value
        

    def set_target_tracklength(self,value):
        """
        Sets attribute self.zt_obj_zt_ret such that
        resulting tracklength after solve and compensation adjustments
        will be correted to = value
        
        attribute self.tracklength must set and must be a number and not None.
        After set_target_tracklength() need to do or redo make_z_from...()
        
        If weight for term 'ztrans_obj - ztrans_ret' is set to 0.
        then the target will be ignored. A weight value of 1. or greater
        will cause the solition algorithm to force the best fit change
        for ztrans_obj and ztrans_ret in order to achive
        target tracklength.
        Input:
        value<float> (mm) target tracklength
        """
        if self.tracklength:   
            #self.zt_obj_zt_ret = value - self.tracklength #sign wrong 2/16/14
            self.zt_obj_zt_ret = self.tracklength - value #new 2/16/14
            #need to solve for cause of error makes it tracklength - value
            self.z = None # need to do or redo make_z_from...()
            self.target_tracklength = value
            self.dtarget_tracklength = None
        else:
            raise ValueError,'self.tracklength must be a number not None'
        
    def set_zt_obj_zt_ret(self,value):
        """
        Not sure if this needed???
        Set attribute self.zt_obj_zt_ret = value
        Value of ztrans_obj - ztrans_retro 
        after set need to do or redo make_z_from...() 
        """
        self.zt_obj_zt_ret = value
        self.z = None # need to do or redo make_z_from...()
        self.dtarget_tracklength = None

    def set_trial_colum(self,colum_name='scenario4'):
        self.trial_colum = colum_name

    def set_sens_coeffs(self,plot=False,minrms=.001):
        """
        Solves for polynomial coeffs values that can be used to create sensitivity
        value for any perturbations amount to take care of non linear proplem.
        Takes a list of Luc's .csv file names that each have differant amount of
        for each Perturbation. Calls Make_A functoin to read all the
        resulting sensitivites then can make plot showing the resdial fit error of
        the results.

        Inputs:
        plot<bool> if True will plot sensitivity polynomial resdial fit error
        minrms<float> units ? need more docs

        Used Attributes:
        self.sens_filenames<list> of csv filenames
        self.usedperts<list> of names of Perturbations
        self.allterms<list> of strings of names of row terms ie. field_0_z9

        Output:
        self.sens_coeffs <dict> with coeffs vaules to solve any sensitivey
             form of <dict>[pert][result_name][coeffs]
        """
        csvfiles = self.sens_filenames
        usedperts = self.usedperts[:]
        allterms  = self.allterms[:]
        result_sens = []
        plots={} # this will become self.sens_coeffs
        for pert in usedperts:
            plots[pert] = {}
            for allterm in allterms:
                plots[pert][allterm]={'amounts':[],'result_sens':[]}
        for filename in csvfiles:
            fields_sens = self.read_cv_file(filename)
            A = self.get_A(fields_sens)
            amounts,units = self.get_amounts_units(fields_sens)
            for i,allterm in enumerate(allterms):
                for j,pert in enumerate(usedperts):
                    plots[pert][allterm]['amounts'].append(amounts[j])
                    plots[pert][allterm]['result_sens'].append(A[i,j])
                    plots[pert][allterm]['units'] = units[j]
        pertl = list(plots)
        result_namel = list(plots['ztrans_object'])
        pertl.sort()
        result_namel.sort()
        for result_name in result_namel:
            for i,pert in enumerate(pertl):
                amounts     = plots[pert][result_name]['amounts']
                result_sens = plots[pert][result_name]['result_sens']
                #fit  coeffs
                coeffs = numpy.polyfit(amounts,result_sens,2)
                plots[pert][result_name]['coeffs'] = coeffs             
        if plot:
            import matplotlib.pyplot as plt
            import ompy.pltfuncs as pltfuncs
            for result_name in result_namel:
                write,Print,dialog = pltfuncs.wPd_start(plt)#this was rem out don't know why
                #fig = plt.figure(figsize=((10.8,8)))
                fig = plt.figure(figsize=((16,10)))
                fig.suptitle('Sensitivity Curve fit Resdiuals \n' \
                             '%s   (nm RMS Single pass WFE)' % result_name.upper(),fontsize=18)
                fig.subplots_adjust(top=.9)
                fig.subplots_adjust(left=.075)
                fig.subplots_adjust(right=.95)
                fig.subplots_adjust(bottom=.06)
                fig.subplots_adjust(hspace=.4)
                fig.subplots_adjust(wspace=.3)
                for i,pert in enumerate(pertl):
                    amounts     = plots[pert][result_name]['amounts']
                    result_sens = plots[pert][result_name]['result_sens']
                    units       = plots[pert][result_name]['units']
                    maxam = numpy.absolute(amounts).max() * 1.05 
                    maxre = numpy.absolute(result_sens).max() * 1.05 
                    if numpy.absolute(maxre).max() < minrms:
                        lowpv = True
                    else:
                        lowpv = False

                    #Remove coeffs
                    coeffs = plots[pert][result_name]['coeffs']
                    # calc best fit residuail from poly terms
                    fitres = result_sens - numpy.polyval(coeffs, amounts)
                    maxre = numpy.absolute(fitres).max() * 1.05
                    
                    ax = fig.add_subplot(3,4,i+1)
                    ax.set_xlim(-maxam, maxam)
                    ax.set_xlabel('Perturbation Amount(%s)' % (units))
                    if not lowpv:
                        ax.plot(amounts,fitres,'o-')
                        #ax.set_ylabel('RMS')
                        ax.grid('on')
                        ax.set_ylim(-maxre, maxre)
                    else:
                        ax.text(-maxam,0.5,'      RMS Values <%snm' % minrms,color='r')
                    ax.set_title('Pert: %s' % (pert),color='b')

                pok = pltfuncs.PlotOnKey(plt,fig)
                raw_input('Enter to Close and Continue:')
                plt.close(ax.figure)
        self.sens_coeffs = plots

    def _sub_nom(self,dfields,perts):
        """
        newdfields = self._sub_nom(dfields,perts)
        Subtracts values in nominal colum from perts
        returns newfields dict
        Does not subtract from nominal colum so do not run twice on
        same dfields<dict> or nominal values will be subtracted twice
        Inputs:
        dfields<dict> need more doc
        perts<> need more doc
        Output:
        newdfields<dict> need more doc
        """
        perts.remove('nominal')
        #turn dfields into list
        fnames = list(dfields)
        fnames.sort()
        #print fnames
        fields = []
        for fname in fnames:
            fields.append(dfields[fname])
        newfields = []
        for field in fields:
            if not 'nominal' in field:
                raise TypeError, 'No colum named nominal'
            nom = field['nominal']
            noml = list(nom)
            noml.remove('perturbation')
            noml.remove('units')
            #pertsl = list(field) remove later
            for pert in perts:
                for row in noml:
                    try:
                        real = float(field[pert][row])
                    except:
                        print 'Illegal value in sub_num; will skip it'
                        print pert,row
                        print field[pert][row]
                        continue
                    field[pert][row] = real - float(field['nominal'][row])
            newfields.append(field)
        #turn fields into dict
        dnewfields = {}
        for i,field in enumerate(newfields):
            dnewfields['field_%i' % i] = field
        return dnewfields

    def get_amounts_units(self,fields):
        """
        amounts,units = self.get_amounts_units(fields)
        Sorts out and returns amounts and units from codeV sens csv file
        Inputs:
        fields<dict> of fields sens data from codev csv file
        self.usedperts<list> list of strings of pert names to be useded
        Ouptut lists have matching index values to self.usedperts
        Output:
        amounts<1darray> of floats of pert amount for each used pert
        units<list> of strings unit lables to go with amounts
        """
        usedperts = self.usedperts[:]
        field = fields['field_0']
        amounts = []
        units = []
        for pert in usedperts:
            amounts.append(float(field[pert]['amount']))
            units.append(field[pert]['units'])
        amounts = numpy.array(amounts)
        return amounts,units
    
    def get_A(self,fields_arg):
        """
        A = get_A(fields_arg)
        wrapper for self.set_A()
        Input:
        fields_arg<dict> need more doc
        Output:
        A<ndarray> main mxn sensitivity array
        
        I thought it would be less confusing to use wrapper
        when using fields_arg
        see set_A for Docs
        """
        if fields_arg is None:
            raise ValueError,'get_A arg should be dict not None'
        return self.set_A(fields_arg)

    def set_A(self,fields_arg=None):
        """
        A = set_A(fields_arg=dfields) or set_A()
        Builds main m x n sensitivity matrix
        If fields_arg = None sets Attribute self.A
        if fields_arg=<dict> returns A

        Inputs:
        fields<dict> from read_cv_file()
            if None file get fields from self.fields_sens
            and will set self.A and not return A
            if fields is fields<dict> will do opisite
        Output:
        self.A<ndarray> m x n or Return A if fields is <dict>

        Method was named makeA()
        """
        #usedperts<list> of strings of perturbations to select from fields
        #aallterms<list> of strings of names of row terms ie. field_0_z9
        if fields_arg is None:
            fields = self.fields_sens.copy()
        else:
            fields = fields_arg
        usedperts = self.usedperts
        allterms = self.allterms
        n = len(usedperts)
        m = len(allterms) 
        A = numpy.zeros((m,n),dtype='float64')
        for k,allterm in enumerate(allterms):
            if not '-' in allterm:
                #not a subtraction term ie. field_1_z5 - field_4_z5
                fieldname,term = allterm.rsplit('_',1)
                field = fields[fieldname]
                if term == 'avectx': 
                    for p,pert in enumerate(usedperts):
                        avectx = self.get_astigs(field,pert)[0]
                        A[k,p] = avectx 
                elif term == 'avecty':
                    for p,pert in enumerate(usedperts):
                        avecty = self.get_astigs(field,pert)[1]
                        A[k,p] = avecty                     
                else:
                    for p,pert in enumerate(usedperts):
                        A[k,p] = float(field[pert][term]) 
            elif '- field' in allterm:
                #Is a subtraction term ie. field_1_z5 - field_4_z5
                allterm1,allterm2 = allterm.split('-')
                allterm1 = allterm1.strip()
                allterm2 = allterm2.strip()
                fieldname1,term1 = allterm1.rsplit('_',1)
                fieldname2,term2 = allterm2.rsplit('_',1)
                for p,pert in enumerate(usedperts):
                    A[k,p] = float(fields[fieldname1][pert][term1]) - \
                             float(fields[fieldname2][pert][term2])
            elif allterm == 'ztrans_obj - ztrans_ret':
                for p,pert in enumerate(usedperts):
                    if pert == 'ztrans_object':
                        try:
                            A[k,p] = float(fields['field_0']['ztrans_object']['amount'])
                        except:
                            A[k,p] = 0.
                    elif pert == 'ztrans_retro':
                        try:
                            A[k,p] = -float(fields['field_0']['ztrans_retro']['amount'])
                        except:
                            A[k,p] = 0.
                    else:
                        A[k,p] = 0.
            else:
                raise ValueError,'item in allterms not reconized'
        if fields_arg is None:
            self.A = A
        else:
            return A
        
    def disp_varibles(self,mode,title=''):
        """
        Print values of Measured Varibles next to values
        Inputs:
        title<str>
        mode= 'z' or 'res': 'z' will display the result values from self.z
                            these values are the measured errors z4,z9 etc.
                            'res' will display values from self.res resdiual
                            zernikes from solve.
        """
        if mode == 'res':
            values = self.res
        elif mode == 'z':
            values = self.z
        print '\n %s' % title
        print '      Measured Variable    Value Weight'
        for termname , v ,w in zip(self.allterms,values,self.weights):
            pri  ='%s  %7.2f   %.1f' % (termname , v,w)
            pri=pri.rjust(38)
            print pri
        print '              Measured Track Length' , self.tracklength
        print '                Target Track Length' , self.target_tracklength
        print '         Predicted New Track Length' , self.new_tracklength
        print 'Predicted Delta Target Track Length' , self.dtarget_tracklength

        print 'disp_varibles()'

    def get_fieldnames(self):
        """
        Returns sorted <list> of field names in self.fields_sens
        field names must have form field_<int> i.g. field_2
        """
        a = list(self.fields_sens)
        a.sort()
        #remove items in list if not starting with field_
        #not needed at this time but in future dict may get more keys
        for v in list(a[:]):
            if not v.startswith('field_'):
                a.remove(v)    
        return a
    
    def get_GntSet(self,mode='z'):
        """
        returns GntSet
        Made from self.z data or self.res
        made from field_# data from z4,5,6,7,8,9,14,15,16
        Input:
        mode= 'z' or 'res': only use 'z'
                            'z' will display the result values from self.z
                            these values are the measured errors z4,z9 etc.
                            'res' will display values from self.res resdiual
                            zernikes from solve
        """
        import ompy
        from ompy.intcoefs import Intcoefs
        if mode == 'z':
            results = self.z
        elif mode == 'res':
            raw_input("Don't use res here becouse the res z5,z6 values are not good")
            results = self.res
        fieldnames = self.get_fieldnames()
        zlist = self.zlist
        dfterms = {}
        for fname in fieldnames:
            dfterms[fname]= {}
        for termname , v in zip(self.allterms,results):
            if '-' in termname:
                #skip other terms with - in name
                continue
            fname,term = termname.rsplit('_',1)
            dfterms[fname][term] = v
        for fname in dfterms:
            intobj = Intcoefs('blankzernfit')
            intobj['normalization_radius'] = 50
            intobj[16] = 0.
            intobj = intobj.zero()
            for term in zlist:
                num = int(term[1:])
                intobj[num] = dfterms[fname][term]  * 1e-6             
            dfterms[fname]['gnt'] = intobj.tognt(size=110).crop(50)
        gsl = []
        names=[]
        for i,fname in enumerate(fieldnames):#why enumerate?
            gsl.append(dfterms[fname]['gnt'])
            names.append(fname)
        gs = ompy.GntSet(gsl)
        gs.original2 = names
        return gs
                                 
    def disp_varibles_matrix(self,mode,title=''):
        """
        Print values of allterms next to z
        mode= 'z' or 'res': 'z' will display the result values from self.z
                            these values are the measured errors z4,z9 etc.
                            'res' will display values from self.res resdiual
                            zernikes from solve.
        """
        if mode == 'z':
            results = self.z
        elif mode == 'res':
            results = self.res
        fieldnames = self.get_fieldnames()
        zlist = self.zlist
        dterms={}
        for termname , v in zip(self.allterms,results):
            dterms[termname] = v
        disp = {}
        for zern  in zlist:
            disp[zern] = {}
            for fieldname in fieldnames:
                disp[zern][fieldname] = dterms.pop('%s_%s' % (fieldname,zern))
        dlist = list(dterms)
        dlist.sort()
        print '\n',title
        print 'Item',
        for v in fieldnames:
            print v,
        for zern in zlist:
            print
            print '%s  ' % zern,
            for fieldname in fieldnames:
                print '%+0.2f  ' % disp[zern][fieldname],
        print
        keys = list(dterms)
        keys.sort()
        for key in keys:
            if key.startswith('ztrans_'):
                print key, ' %+0.5f' % dterms[key]
            else:
                print key, ' %+0.2f' % dterms[key]
        print '              Measured Track Length' , self.tracklength
        print '                Target Track Length' , self.target_tracklength
        print '         Predicted New Track Length' , self.new_tracklength
        print 'Predicted Delta Target Track Length' , self.dtarget_tracklength


    def make_z_zero(self):
        """
        sets self.z to all 0.
        sets self.weights z5 and z6 to 0.
        """
        m = len(self.allterms)
        z = numpy.zeros(m,dtype='float64')
        self.z = z
        if self.allterms[-1] == 'ztrans_obj - ztrans_ret':
                self.z[-1] = self.zt_obj_zt_ret
        self.weights = [1]*m
        for i,v in enumerate(self.allterms):
            if len(v) < 12:
                if v.lower().endswith('z5') or v.lower().endswith('z6'):
                    self.weights[i] = 0
        self.z_with_nominal = None#
        self.plus_nominal()

    def make_z_from_GntSet(self,*gs,**kwds):
        """
        Returns z M Measured variables vector to solve
        parameter vector(compensator values) using sensitivity matrix self.A
        
        Inputs:
        gs<GntSet> or 'root','ext' Gnts croped to ca ready to have fitzern run
                if gs gs.original2 list must be names of
                fields pattern -> field_#
        Optional:
        regrid= interger regricd ngc amount defalut = 256
        remove_nominal<bool> defualt True
                            removes nominal design resdiual zernikes from
                            each field point
        """
        self.z_with_nominal = None
        if len(gs) == 1:
            #gs[0] is a GntSet
            gs = gs[0]
        elif len(gs) == 2 and  isinstance(gs[0],basestring):
            import ompy
            gs = ompy.GntSet(gs[0],gs[1])
        else:
            raise ValueError, 'gs argument not correct'
        #make original2 list of fieldnames
        org2 = []
        for i in xrange(len(gs)):
            org2.append('field_%s' % i)
        gs.original2 = org2[:]
        if 'regrid' in kwds:
            gs.regrid(ngc=kwds['regrid'])
        else:
            gs.regrid(ngc=256)
        if 'remove_nominal' in kwds:
            remove_nominal = kwds['remove_nominal']
        else:
            remove_nominal = True
        allterms = self.allterms
        fields = {}
        for i in xrange(len(gs)):
            fieldname = gs.original2[i]
            gobj = gs[i]
            gz16 = gobj.fitzern(16,xterms=[10,11,12,13]).int * 1e6
            gz16[4]  = gz16[4]  / math.sqrt(3)
            gz16[5]  = gz16[5]  / math.sqrt(6)  
            gz16[6]  = gz16[6]  / math.sqrt(6) 
            gz16[7]  = gz16[7]  / math.sqrt(8) 
            gz16[8]  = gz16[8]  / math.sqrt(8) 
            gz16[9]  = gz16[9]  / math.sqrt(5) 
            gz16[14] = gz16[14] / math.sqrt(12)  
            gz16[15] = gz16[15] / math.sqrt(12) 
            gz16[16] = gz16[16] / math.sqrt(7)  
            for j in [4,5,6,7,8,9,14,15,16]:
##                gz16[j] *= 0 #debug
                pass
##            gz16[5] +=0 #degub
##            gz16[6] -=0 #debug
            fields[fieldname]= {'gz16':gz16}
            if remove_nominal:
                for tnum in [4,5,6,7,8,9,14,15,16]:
                    znom = float(self.fields_sens[fieldname]['nominal']['z%i' % tnum])
                    fields[fieldname]['gz16'][tnum] -= znom
        m = len(allterms)
        z = numpy.zeros(m,dtype='float64')
        for k,allterm in enumerate(allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                field = fields[fieldname]
                try:
                    #try needed becuse of avectx y 
                    tnum = int(term[1:])
                    z[k] = field['gz16'][tnum]
                except ValueError:
                    if term == 'avectx':
                        z5 = field['gz16'][5]
                        z6 = field['gz16'][6]
                        avectx = self.get_astig_vector(z5,z6)[0]
                        z[k] = avectx 
                    elif term == 'avecty':
                        z5 = field['gz16'][5]
                        z6 = field['gz16'][6]
                        avecty = self.get_astig_vector(z5,z6)[1]
                        z[k] = avecty                     
                    else:
                        raise ValueError,'Term should have been avectx or avecty here'
                    
            elif '- field' in allterm:
                #astig corner subtractions
                field = fields[fieldname]
                allterm1,allterm2 = allterm.split('-')
                allterm1 = allterm1.strip()
                allterm2 = allterm2.strip()
                fieldname1,term1 = allterm1.rsplit('_',1)
                fieldname2,term2 = allterm2.rsplit('_',1)
                tnum1 = int(term1[1:])
                tnum2 = int(term2[1:])
                '''
                f1z5 - f4z5
                f1z5 - f2z5
                f2z5 - f3z5
                f4z5 - f3z5
                f1z6 - f3z6
                f2z6 - f4z6
                '''
                #corner astig differances
                z[k] = float(fields[fieldname1]['gz16'][tnum1]) - \
                       float(fields[fieldname2]['gz16'][tnum2])
            elif allterm == 'ztrans_obj - ztrans_ret':
                z[k] = self.zt_obj_zt_ret
            else:
                raise ValueError,'item in allterms not correct'
        self.z = z
        if remove_nominal:
            self.plus_nominal()
        else:
            self.z_with_nominal = None
##        self.z_with_nominal = z #debug


    def plus_nominal(self):
        """
        this method does add nominal avectx and avecty values it leaves
        This should be corrected sometime but for now I think it does not
        effect arror field center methods
        from self.z adds nominal design field error and saves
        to self.z_with_nominal
        adds the the nominal design residual Zernikes from each field point
        why vector analysis of field center requires measured error without
        nominal subtraced this function add bad nominal error to data that has
        has it removed to create data for vector analysis
        """
        if self.z_with_nominal is None:
            self.z_with_nominal = self.z.copy()
        else:
            raw_input('setting self.z_with_nominal twice??? Enter to Continue:')
        for k,allterm in enumerate(self.allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                #fieldname should be 'field_#'
                try:
                    #try needed becouse terms avectx and y don't end with int
                    tnum = int(term[1:])
                    self.z_with_nominal[k] += float(self.fields_sens[fieldname]['nominal']['z%i' % tnum])
                except ValueError:
                    pass

    def make_z_from_scenario(self,trialfilename):
        """
        Sets self.z  The M Measured variables vector used to solve for the
        parameter vector(compensator values) using sensitivity matrix self.A
        Input:
        trialfilename<str> name of CodeV csv file used to test solution algorithm.
                                Luc's scenario file to be read by read_cv_file
        
        Used Attributes:
        self.fields<dict> scenario fields data from read_cv_file()
        self.allterms<list> of strings of names of row terms ie. field_0_z9
        self.colum<str> name of colum in Luc's spreed sheet exp: scenario2
        """
        self.trialfilename = os.path.join(self.packagePath,trialfilename)
        allterms = self.allterms
        colum = self.trial_colum
        fields = self.read_cv_file(self.trialfilename)
        m = len(allterms) 
        z = numpy.zeros(m,dtype='float64')
        for k,allterm in enumerate(allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                field = fields[fieldname]
                if term == 'avectx': #avectxy stuff does not work, not used
                    avectx = self.get_astigs(field,colum)[0]
                    z[k] = avectx 
                elif term == 'avecty':
                    avecty = self.get_astigs(field,colum)[1]
                    z[k] = avecty                     
                else:
                    z[k] = float(field[colum][term]) 
            elif '- field' in allterm:
                #astig corner subtractions
                field = fields[fieldname]
                allterm1,allterm2 = allterm.split('-')
                allterm1 = allterm1.strip()
                allterm2 = allterm2.strip()
                fieldname1,term1 = allterm1.rsplit('_',1)
                fieldname2,term2 = allterm2.rsplit('_',1)
                '''
                f1z5 - f4z5
                f1z5 - f2z5
                f2z5 - f3z5
                f4z5 - f3z5
                f1z6 - f3z6
                f2z6 - f4z6
                '''
                z[k] = float(fields[fieldname1][colum][term1]) - float(fields[fieldname2][colum][term2])
            elif allterm == 'ztrans_obj - ztrans_ret':
                z[k] = self.zt_obj_zt_ret
            else:
                raise ValueError,'item in allterms not correct'
        self.z = z
        self.z_with_nominal = True # scenario should have nominal aready removed
        
    def update_A(self):
        """
        Creats new main sensitivty array A and re-asigns it to self.A
        Becouse sensitivties are not all linear at a new sensitivity matrix
        is made for each solution interation.
        
        Used Attributes:
        self.p<1darray> scaled solition values
        self.A<2darray> A array from makeA()
        self.sens_coeffs<dict> from get_sens_coeffs()
        self.usedperts<list>
        self.allterms<list> of strings of names of row terms ie. field_0_z9
        Output:
        self.A<2darray>
        amounts<1darray> of new amounts to go with A. copy of p
        """
        p = self.p
        old_A = self.A
        sens_coeffs = self.sens_coeffs
        usedperts = self.usedperts
        allterms = self.allterms
        #I think a new amount should be defined here?
        p1 = p.copy()
        for i,v in enumerate(p):
            #provent seed from being near zero
            if abs(v) < .0001:
                v = float(v)
                sign = (v > 0) - (v < 0)
                if sign == 0:
                    sign = 1
                p1[i] = .0001 * sign
        newA = numpy.zeros(old_A.shape,dtype='float64')
        for j,allterm in enumerate(allterms):
            for k,pert in enumerate(usedperts):
                coeffs = sens_coeffs[pert][allterm]['coeffs']
                # calc best fit residuail from poly terms
                newsen = numpy.polyval(coeffs,p1[k] )
    ##            if abs((A[j,k] - newsen)) > .001:
    ##                print
    ##                print A[j,k]
    ##                print A[j,k] - newsen,allterm,pert
                newA[j,k] = newsen
                amounts = p1.copy()
        self.amounts = amounts
        self.A = newA
 
    def get_new_tracklength(self):
        """
        Return new track length if the system is adjusted with the inverse
        os the solve amounts.
        
        tracklength logic may seem backwards. It must be remebered that
        the solver is solving for the peramaters the cause the defects in
        the system. 
        """
        #fields = self.read_cv_file(self.trialfilename)
        #colum = self.trial_colum
        p = self.p
        usedperts = self.usedperts
        amounts = self.amounts
        if self.tracklength:
            objindex   = list(usedperts).index('ztrans_object')#list needed. T.index not in py2.5
            retroindex = list(usedperts).index('ztrans_retro')
            objz = p[objindex]
            retroz = p[retroindex]
            #newtrack = self.tracklength + (objz - retroz)
            newtrack = self.tracklength - (objz - retroz)#new 2/16/14
            return  newtrack
        else:
            return None


    def disp_solve(self):
        """
        print results of solve
        fields dict from Luc's simulated scenario results
        colum<str> name of colum in simulated result fields list
        usedperts<list> of used perts
        p array of solved valeus
        amounts<1darray> 
        """
        #fields = self.read_cv_file(self.trialfilename)
        #colum = self.trial_colum
        p = self.p
        usedperts = self.usedperts
        amounts = self.amounts
        print  '\n  Compensator  Solve_Amount  Sens_Seed   Units'
        for i,v in enumerate(usedperts):
            units = self.units[i]#'Units Later'
            pj =  v+'   %+0.5f     %+0.5f  ' % (p[i],amounts[i])
            pj = pj.rjust(39)
            print pj,units
        if self.new_tracklength:
            print 'New Track Length: %.3f' % self.new_tracklength

        print '              Measured Track Length' , self.tracklength
        print '                Target Track Length' , self.target_tracklength
        print '         Predicted New Track Length' , self.new_tracklength
        print 'Predicted Delta Target Track Length' , self.dtarget_tracklength

        print 'disp_solve()'
          
    def disp_trial_solve(self):
        """
        print results of solve
        fields dict from Luc's simulated scenario results
        colum<str> name of colum in simulated result fields list
        usedperts<list> of used perts
        p array of solved valeus
        amounts<1darray> 
        """
        fields = self.read_cv_file(self.trialfilename)
        colum = self.trial_colum
        p = self.p
        usedperts = self.usedperts
        amounts = self.amounts
        print  '\n  Perturbation    Amount  Solve_Amount  Sens_Seed'
        for i,v in enumerate(usedperts):
            try:
                #checks to see if row exits
                pert_amount = float(fields['field_0'][colum][v])
                if 'tilt' in v:
                    pert_amount = math.radians(pert_amount)
                    units = 'rad'
                else:
                    units = 'mm'
                pj =  v+'  %+0.5f  %+0.5f %+0.5f' % (pert_amount,p[i],amounts[i])
                pj = pj.rjust(45)
                print pj,units
            except:
                units = 'may be rad'
                pj = v+'    None    %+0.5f %+0.5f' %(p[i],amounts[i])           
                pj = pj.rjust(45)
                print pj#,units
        print 'Pert Amount None means no row with Pert Amount must be zero'
        print 'disp_trial_solve()'
        
    def plot_sens(self,minrms=.001):
        """
        Takes a list of Luc's .csv file names that each have differant amount of
        Perturbation for each Perturbation. Runs get_A() method to read all the
        resulting sensitivites then makes plot show the results.
        
        Inputs:
        minrms<float> units ? must be nm? ptv of plot < minrms will not plot
        Used Attributes:
        self.sens_filenames<list> of codeV csv filenames
        self.usedperts<list> of names of Perturbations
        self.allterms<list> of strings of names of row terms ie. field_0_z9
        Output:
        None, just makes plots
        """
        import matplotlib.pyplot as plt
        import ompy.pltfuncs as pltfuncs
        csvfiles = self.sens_filenames
        usedperts = self.usedperts
        allterms = self.allterms
        result_sens = []
        plots={}
        for pert in usedperts:
            plots[pert] = {}
            for allterm in allterms:
                plots[pert][allterm]={'amounts':[],'result_sens':[]}
        
        for filename in csvfiles:
            fields_sens = self.read_cv_file(filename)
            A = self.get_A(fields_sens)
            amounts,units = self.get_amounts_units(fields_sens)
            for i,allterm in enumerate(allterms):
                for j,pert in enumerate(usedperts):
                    plots[pert][allterm]['amounts'].append(amounts[j])
                    plots[pert][allterm]['result_sens'].append(A[i,j])
                    plots[pert][allterm]['units'] = units[j]

        pertl = list(plots)
        result_namel = list(plots['ztrans_object'])
        pertl.sort()
        result_namel.sort()
        for result_name in result_namel:
            write,Print,dialog = pltfuncs.wPd_start(plt)
            #fig = plt.figure(figsize=((10.8,8)))
            fig = plt.figure(figsize=((16,10)))
            fig.suptitle('Sensitivity Result For:   %s   (nm RMS Single pass WFE)' % result_name.upper(),fontsize=18)
            fig.subplots_adjust(top=.9)
            fig.subplots_adjust(left=.075)
            fig.subplots_adjust(right=.95)
            fig.subplots_adjust(bottom=.06)
            fig.subplots_adjust(hspace=.4)
            fig.subplots_adjust(wspace=.3)
            for i,pert in enumerate(pertl):
                amounts     = plots[pert][result_name]['amounts']
                result_sens = plots[pert][result_name]['result_sens']
                units       = plots[pert][result_name]['units']
    ##            print amounts
    ##            print result_sens
                maxam = numpy.absolute(amounts).max() * 1.05 
                maxre = numpy.absolute(result_sens).max() * 1.05 
                if numpy.absolute(maxre).max() < minrms:
                    lowpv = True
                else:
                    lowpv = False
                ax = fig.add_subplot(3,4,i+1)
                ax.set_xlim(-maxam, maxam)
                ax.set_xlabel('Perturbation Amount(%s)' % (units))
                if not lowpv:
                    ax.plot(amounts,result_sens,'o-')
                    #ax.set_ylabel('RMS')
                    ax.grid('on')
                    ax.set_ylim(-maxre, maxre)
                else:
                    ax.text(-maxam,0.5,'      RMS Values <%snm' % minrms,color='r')
                ax.set_title('Pert: %s' % (pert),color='b')

            pok = pltfuncs.PlotOnKey(plt,fig)
            raw_input('Enter to Close and Continue:')
            plt.close(ax.figure)    

    def solve(self):
        """
        Solves for the the parameter vector p in z = Ap using
        weighted least squares. Main solution engine of align.
        
        Note: returned self.p values are scaled by values in self.amounts

        Used Attributes:
        self.A<2darray> M x N sensitivty matrix
        self.z<1darray> measured results M variable(data points)
        self.amounts<list> of amounts for each pert in sensitivity matrix
        self.weights<list> Vector length M containg weights for each M measured
            variable(data points)
        self.force<list> of force values to apply N-dimensional parameter vector.
                    if value in list is None no force is applied
        Output:
        self.p<1darray> parameter vector scaled by amounts
        self.res<1darray> resdiual values of z after removing solition values
        #iforce<list> of tuples [(index,force value),...]
        """
        def get_radians(values,units):
            values_radians = values.copy()
            units_radians = units[:]
            for i in xrange(len(p)):
                if units[i].lower().strip() in ['deg','degrees']:
                    values_radians[i] = math.radians(p[i])
                    units_radians[i] = 'rad'
            return values_radians, units_radians
                    
        A = self.A.copy()
        z = self.z.copy()
        amounts = self.amounts
        weights = self.weights
        force = self.force
        iforce = []
        for i,v in enumerate(force):
            if not v is None:
                v /= amounts[i]
                iforce.append((i,v))
                A,z = calcfuncs.force(A,z,i,v)
        #(p, r, rank, s) = lstsq(A,z)
        p_unscaled = calcfuncs.wleast_squares(A,z,weights)
        res = _get_residiual(A,p_unscaled,z)
        for t in  iforce:
            p_unscaled[t[0]] = t[1]
        p = p_unscaled * amounts
        self.p = p
        self.p_radians, self.units_radians = get_radians(self.p,self.units)
        self.amounts_radians, _            = get_radians(self.amounts,self.units)
        self.res = res
        self.new_tracklength = self.get_new_tracklength()
        if self.target_tracklength:
            self.dtarget_tracklength = self.target_tracklength - self.new_tracklength

    def _add_pert_zt_obj_zt_retro(self,dfields):
        """
        Not used
        #if used this should be part of codev sens not made up here
        #if made up here would need to sens_coeffs to get sens values
  
        newfields  = add_pert_zt_obj_zt_retro(dfields)
        adds to defield ztrans_obj - ztrans_ret
        Returns newdfields
 
        dfields['field_0']['ztrans_m1']['z4'] -> senitivity result from
                                            field 0 colum 'ztrans_m1' row 'z4'
        dfields['field_0']['ztrans_m1']['amount'] -> amount of perturbation
        dfields['field_0']['ztrans_m1']['units'] -> unit of perturbation
        """
        nkey = 'ztrans_object-ztrans_retro'
        fields = dfields.copy()
        fieldnames = list(fields)
        for fieldname in fieldnames:
            fields[fieldname][nkey]={}
            for row in (dfields[fieldname]['xtilt_m1']):
                if row in ['units','perturbation']:
                    continue
                try:
                    #if used this should be part of codev sens not made up here
                    #if made up here would need to sens_coeffs to get sens values
                    fields[fieldname][nkey][row] = \
                                      dfields[fieldname]['ztrans_object'][row] + \
                                        dfields[fieldname]['ztrans_retro' ][row]
                except:
                    print 'failed row in add_pert_zt_obj_zt_retro',row
            fields[fieldname][nkey]['units'] = dfields[fieldname]['ztrans_object']['units']
            
        return fields        

    def get_perts(self):
        """
        Return list of perturbation names from self.fields_sens
        """
        perts =  []
        for row,v in self.fields_sens['field_0'].items():
            if isinstance(v,dict):
                if not row == 'nominal':
                    perts.append(row)
        return perts

    def optimize_astig(self):
        """
        minimizes distance between vector found field center pos by
        optimizing static system asitig amount
        """
        import scipy.optimize
        import copy
        numpy.set_printoptions(precision=3,suppress=True)
        # copy data in self.astig_vectors
        # was using copy.deepcopy was not sure about ref issues changed to this
        vectors = []
        signs = []
        for i in xrange(len(self.astig_vectors)):
            vectors.append(self.astig_vectors[i][0].copy())
            signs.append(self.astig_vectors[i][2])
        vectors = numpy.array(vectors)
        print self.astig_vectors
        pause('Starting')
        def error(z5z6):
            z5 = z5z6[0]
            z6 = z5z6[1]
            # copy original data back into self.astig_vectors
            for i in xrange(len(self.astig_vectors)):
                self.astig_vectors[i][0] = vectors[i].copy()
                self.astig_vectors[i][2] = signs[i]
            angle = self.get_angle(z5,z6)
            mag = math.hypot(z5,z6)
            uv = numpy.array([math.cos(angle),math.sin(angle)])
            field_distance = self.get_field_distance(mag)
            v = uv * field_distance
            for i in xrange(len(self.astig_vectors)):
                self.astig_vectors[i][0] -= v
            print self.astig_vectors
            #pause('vector in error')
            self.vector_best_center()
            #self.plot_vectors()
            print '\nz5,z6',z5z6
            print 'center_seps',self.center_seps
            print 'center_seps_rms',self.center_seps.std() + self.center_seps.mean()
            return self.center_seps

        astig_ang_mag = scipy.optimize.leastsq(error,[0.1,0.1])[0]
        print 'final---------------'
        error(astig_ang_mag)
        print '\n\n\n\n'
        self.plot_vectors()
        
        
    def vector_best_center(self):
        """
        """
        centers = []
        k=0
        for vs in self.astig_vectors[1:]:
            k+=1
            p = vs[1]
            p1 = p + vs[0]
            p2 = p + vs[0] * -1
            vL1 = math.hypot(p1[0],p1[1])
            vL2 = math.hypot(p2[0],p2[1])
            if vL1 <= vL2:
                self.astig_vectors[k][2]= 1
                centers.append(p1)
            else:
                self.astig_vectors[k][2]= -1
                centers.append(p2)
        center = numpy.array(centers).mean(0)
        vs = self.astig_vectors[0]
        k=0
        p = vs[1]
        p1 = -center + p + vs[0]
        p2 = -center + p + vs[0] * -1
        vL1 = math.hypot(p1[0],p1[1])
        vL2 = math.hypot(p2[0],p2[1])
        if vL1 <= vL2:
            self.astig_vectors[k][2]= 1
            centers.append(p + vs[0])
        else:
            self.astig_vectors[k][2]= -1
            centers.append(p + vs[0]*-1)
        center = numpy.array(centers).mean(0)
        self.field_cen_vectors = center

        center_seps = []
        for vs in self.astig_vectors:
            p = -center + vs[1]+ vs[0] * vs[2]
            vL = math.hypot(p[0],p[1])
            center_seps.append(vL)
        self.center_seps = numpy.array(center_seps)


    def plot_vectors(self,title='Field Points And Field Center Analysis'):
        """
        plots astig vectors from each field point with arrows pointing toward
        field center and away from field center
        """
        import matplotlib.pyplot as plt
        from ompy.pltfuncs import DrawFig
        df = DrawFig(plt,{})
        fig = plt.figure(figsize=(10.,8.))
        #              left, bottom, width, height
        ax = fig.add_axes([.1,.1,.8,.8])
        color = ['r','g','b','m','c'] * 2
        for astig in self.astig_vectors:
            co = color.pop()
            p = astig[1]
            p1 = p + astig[0]
            p2 = p + astig[0] * -1
            ax.plot(p[0],p[1],'o',ms=8,color=co,mew=0)
            ax.plot([p1[0],p2[0]],[p1[1],p2[1]],'-',ms=1,color=co,mew=0,lw=1)
            if math.hypot(astig[0][0],astig[0][1]) > .05: #fails if 0
                ax.arrow(p[0],p[1], astig[0][0]*astig[2],astig[0][1]*astig[2], head_width=0.1,
                         head_length=0.1, fc=co, ec=co,
                         length_includes_head=True,lw=1)
##                    ax.arrow(p[0],p[1], astig[0][0]*-1,astig[0][1]*-1, head_width=0.1,
##                             head_length=0.1, fc=co, ec=co,
##                             length_includes_head=True,lw=1)
        ax.plot(self.field_cen_vectors[0],self.field_cen_vectors[1],'k*',ms=10)
        title += '\n Center from Vectors X:%.3f Y:%.3f' % (self.field_cen_vectors[0],
                                                           self.field_cen_vectors[1])
        ax.set_aspect('equal')
        lim = 3
        ax.set_xlim(-lim,lim)
        ax.set_ylim(-lim,lim)
        ax.set_title(title)
        ax.grid()
        pm = df.draw(fig)
            
    def get_mag(self,field_distance):
        """
        mag = self.get_mag(field_distance)
        Input:
        field_distance<float> distance from field center
        Output:
        mag<float> magnatude = astig_mag/2. or mag=sqrt(z5**2+z6**6)
        """
        z5coeffs = self.sens_coeffs['xtrans_object']['field_0_z5']['coeffs']
        mag = numpy.polyval(z5coeffs,field_distance)
        return mag

    def get_field_distance(self,mag):
        """
        returns distance (length) from center of field that causes astig term value mag
        mag is magnitude of astig / 2.
        mag = sqrt(z5**2+z6**2)
        Method and notes:
        optimizes length from function mag=f(distance) becouse of the difficutly of
        finding a fuction distance = f(mag). Need to work that out some day. Next try
        fitting directly to points distance to mag rather then using linspace values.
        """
        import scipy.optimize
        middle = self.get_mag(0) 
        def error(p):
            diff = abs(mag - self.get_mag(p[0])+middle)
            #print 'p,diff',p,diff
            return diff
        field_distance = scipy.optimize.fmin(error,[0],disp=False)[0]
        return field_distance

    def optimize_z5_z6(self,vector):
        """
        Returns z5 and z6 given astig_vector (x,y)
        minor testing done
        """
        import scipy.optimize
        def error(z5z6):
            print '\nz5 z6',z5z6
            astig_vector = self.get_astig_vector(z5z6[0],z5z6[1])           
            diff = vector - astig_vector
            print 'diff',diff
            return diff
        z5z6 = scipy.optimize.leastsq(error,[0,0])[0]
        print 'final\n',error(z5z6)
        return z5z6[0],z5z6[1]
            
    def get_angle(self,z5,z6):
        """
        get angle in radians of high side of astig
        +x is 0 +y is pi/2(-90deg) +x is pi(180deg)
        """
        if abs(z5) < 1e-6:
            z5 = 1e-6
        angle = math.atan(z6/float(z5))/2.        
        sign = (float(z5) > 0) - (float(z5) < 0)
        if sign < 0:
            angle += math.pi/2.
        angle = angle % math.pi
        #angle *= -1 # why make all neg???
        return angle


    def get_astigs(self,field,pert):
        """
        returns vector avectx and avecty
        
        Input:
        field<dict> of a field data
        pert<str> name pert
        avectx,avecty = _get_astigs(field,'ytrans_object')
        xxx
        """
        z5 = float(field[pert]['z5'])
        z6 = float(field[pert]['z6'])
        return  self.get_astig_vector(z5,z6)

    def get_astig_vector(self,z5,z6a):
        """
        Calculaters vector (x,y) repersenting astigmitism
        where the length of the vector (sqrt(x*2+y**2)) is half the
        ptv of the astig form z5,z6 and the direction cossine
        or unit vector is = vector / length
        Angle being represented as 0 degrees when high side of astig is along
        the x axis and 90 degrees when toward the y axis

        the length of this output vector is not distace on focal plane as
        is the case with other methods in this class
        
        Input:
        z5<float> Zernike term 5
        z6<float> Zernike term 6
        Output:
        astig_vector<array> (x,y)
        """
        if abs(z6a) < .000000001:
            z6 = .00001
        else:
            z6 = z6a #debug
        mag = math.hypot(z5,z6)# term magnitude is 1/2 p-v
        #print 'astig mag' ,mag , fieldname
        # get angle in radians of high side of astig
        #+x is 0 +y is pi/2(90deg) -x is pi(180deg)
        angle = self.get_angle(z5,z6)
        # calc unit vector (length = 1)
        uv = numpy.array([math.cos(angle),math.sin(angle)])
        #get length of vector using non linear sens data for astig
        astig_vector = uv * mag
        return astig_vector
        
            
    def set_astig_vectors(self):
        """
        sets:               
        self.astig_vectors<array> [((v0x,v0y),(field_x,field_y),sign),((v2x,v2y,),...]
        (v0x,v0y) astig vector for each field 0..n
        (field_x,field_y) coordinates of field
        sign -1 or 1 best guess as to sign of vector pointing toward center
        astig vector x,y is a vector pointed in the direction of the astig
        The length of the vector is the magnitude of the vector scaled into
        distance on the object plane that causes that amount of astig
        
        Astig must be from measured data without nominal subtracted, this causes each
        field point to point to center of field. 
    
        """                    
        # ----------------------------
        astig_vectors = []
        astig = {}
        fieldnames = list(self.fields_sens) 
        fieldnames.sort() 
        for fieldname in fieldnames:
            astig[fieldname] = [None,None]
        for k,allterm in enumerate(self.allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                #fieldname should be 'field_#'
                if term == 'z5':
                    astig[fieldname][0] = self.z_with_nominal[k]
                    #self.z_with_nominal is measured value without subtracting
                    #nominal design error for that field point
                if term == 'z6':
                    astig[fieldname][1] = self.z_with_nominal[k]
            
        for fieldname in fieldnames: #fieldnames are sorted
            z5 = astig[fieldname][0]
            z6 = astig[fieldname][1]
            mag = math.hypot(z5,z6)# term magnitude is 1/2 p-v
            #print 'astig mag' ,mag , fieldname
            # get angle in radians of high side of astig
            #+x is 0 +y is pi/2(90deg) -x is pi(180deg)
            angle = self.get_angle(z5,z6)
            # calc unit vector (length = 1)
            uv = numpy.array([math.cos(angle),math.sin(angle)])
            #get length of vector using non linear sens data for astig
            field_distance = self.get_field_distance(mag)
            vector = uv * field_distance
            field_x = self.fields_sens[fieldname]['field_x']
            field_y = self.fields_sens[fieldname]['field_y']
            astig_vectors.append([vector,(field_x,field_y),None])
        self.astig_vectors = astig_vectors
        self.vector_best_center()
        self.plot_vectors()
        self.optimize_astig()


    def read_cv_file(self,filename,sub_nomanil_colum=True,additem1=False):
        """
        Reads lucs codeV csv file
        Returns dict of dict's for each field point
        {field_number:{perturbations_field1:results_f1},?{_f2:results_f2},...}}
        Each results_f# is a dict {results_f#:value} value is a string not a
        float.

        Usage Example:
        dfields = self.read_cv_file(name)
        dfields['field_0']['ztrans_m1']['z4'] -> senitivity result from
                                            field 0 colum 'ztrans_m1' row 'z4'
        dfields['field_0']['ztrans_m1']['amount'] -> amount of perturbation
        dfields['field_0']['ztrans_m1']['units'] -> unit of perturbation
        """
        def get_order_number(f_x,f_y,field_coord,tol=.005):
            """
            Returns<int> field number that matches with field_coord
            from blocks ie. f_.5_-.5
            f_x<float> field x position
            f_y<float> field y position
            field_coord=<list> example  [(0,0),(+.5,+.5),(+.5,-.5),(-.5,-.5),(-.5,+.5)]
            """
            for ind,fc in enumerate(field_coord):
                if fc[0]-tol < f_x < fc[0]+tol and  fc[1]-tol < f_y < fc[1]+tol:
                    return ind
            return None

        #adds keys at same level as perts, should add only one
         #should only add one new key 'not_pert' to hold other info like
         #'x' and 'y'
        maintags,blocks = ompysys.tagreader(filename)[:2]
        #print '\nReading Sensitivty file: %s' % filename
        n_s = maintags['nominal_subtracted'].strip().strip(',').lower()
        if  n_s == 'true':
            nominal_subtracted = True
        elif n_s == 'false':
            nominal_subtracted = False
        else:
            raw_input('No tag nominal_subtracted so setting to False')
            nominal_subtracted = False
        fieldnames = list(blocks)
        fieldlocs=[]#field locations
        fields_tags = []
        for fieldname in fieldnames:
            fieldtags = ompysys.tagreader(blocks[fieldname])[0]
            #missing = in file needs following
            illtags    = ompysys.tagreader(blocks[fieldname])[3]

            #turn fieldnames into field locations f_x_y
            if fieldname.lower().startswith('f'):
                fieldname1 = fieldname
            else:
                # if does not start with f remove first two charaters
                fieldname1 = fieldname[2:]
            x , y = fieldname1.strip(',').split('_')[-2:]
            fieldlocs.append({'field_x':float(x),'field_y':float(y),
                              'field_block':fieldname1})            
            for v in illtags:
                print 'Illegal tags *******'
                c = v.strip(',').split(',')
                fieldtags[c[0]] = c[1:] #this puts list in fieldtags where most are still strings
            fields_tags.append(fieldtags)

        #make list of perturbations 
        perts = fields_tags[0]['perturbation'].strip(',').split(',')
        for i in xrange(len(perts[:])):
            perts[i] = perts[i].strip()                    
        pertlen =len(perts)

        for field_tags in fields_tags:
            for resultkey in list(field_tags):
                try:
                    #needed becouse some items are list a ready becouse of illegal tags
                    field_tags[resultkey] = field_tags[resultkey].strip(',').split(',')
                except: AttributeError
        fields = []
        for field_tags in fields_tags:
            fperts = {}              
            for i,pertv in enumerate(perts):
##                exec ('%s = {}' % pertv)#this works but I think I don't really need exec
##                exec ('pertd = %s' % pertv)
                tmpd = {}#i think this will replace exec commands above
                for resultkey in field_tags:
                    if _isresultrow(field_tags[resultkey],pertlen):
##                        pertd[resultkey] = field_tags[resultkey][i]
                        tmpd[resultkey] = field_tags[resultkey][i]
                    else:
                        #non row results to dict such as comment
                        fperts[resultkey] = field_tags[resultkey]
##                fperts[pertv] = pertd.copy()
                fperts[pertv] = tmpd.copy()
            fields.append(fperts)
            #need to add field location pertv dict
            #need to file tags somewhere
        #put in field locations x and y tags from maintags
        for i,d in enumerate(fields[:]):
            d.update(fieldlocs[i])
            for key,value in maintags.items():
                d[key]= value
        #turn fields into dict
        dfields = {}
        for field in fields:
            ind = get_order_number(field['field_x'],field['field_y'],
                                   field_coord = self.field_coord)
            if not ind is None:
                dfields['field_%i' % ind] = field
        if sub_nomanil_colum and not nominal_subtracted:
            dfields = self._sub_nom(dfields,perts)
        if additem1:
            raise ValueError, 'additem1 not supported'
            #not used
            dfields = self.add_pert_zt_obj_zt_retro(dfields)
        return  dfields

def _get_residiual(A,p,z):
    newz = numpy.dot(A,p)
    res =  z -newz #was newz - z
    return res

def _isresultrow(row,pertlen):
    """
    checks if row is a result row in the field block
    or just a tag like comment
    Inputs:
    row<list>
    pertlen<int>
    Output:
    <bool>
    """
    row1 = False
    if  isinstance(row,list):
        if len(row) == pertlen:
            row1 = True
    return row1



def pause(comment=''):
    raw_input('Pause %s' % comment)

def _start():
    """
    Colects data to start process
    Output:
    allterms<list> of terms used to solve alignment e.g. 'field_0_z4'
    weights<list> of floats. Used to weight solution algorithm
    usedperts<list> of names of used pertabation e.g. 'ztrans_m1'
    sens_filename<str> name of CodeV csv file used to seed sensitivity matrix
    sens_filenames<list> of strings of CodeV csv files containn sensitivty data
                            used to update sensitivity matrix during solution
                            interations.
    force<list> of numbers or None. If not None number is forced and fixed into
                align solution. If None usedpert is varible in align solution. 
    """
    #        older sens files not checked for coordinate oriention
##    sens_filenames =['systestdbl_sens_01-Aug-2012_cset2_m6.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_m4.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_m2.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_m1.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_0.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_1.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_2.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_4.csv',
##                     'systestdbl_sens_01-Aug-2012_cset2_6.csv']

    # Thes sens files have been checked by luc for coordinate oriention
##    sens_filenames =['systestdbl_sens_07-Dec-2013_cset2_m6.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_m4.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_m2.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_m1.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_0.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_1.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_2.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_4.csv',
##                     'systestdbl_sens_07-Dec-2013_cset2_6.csv']


    sens_filenames =[#'systestdbl_sens_24-Feb-2014_cset2_m50.csv',
                     #'systestdbl_sens_24-Feb-2014_cset2_m20.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_m6.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_m4.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_m2.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_m1.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_0.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_1.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_2.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_4.csv',
                     'systestdbl_sens_24-Feb-2014_cset2_6.csv',
                     #'systestdbl_sens_24-Feb-2014_cset2_20.csv',
                     #'systestdbl_sens_24-Feb-2014_cset2_50.csv'
                     ]


    
    for i,v in enumerate(sens_filenames):
        sens_filenames[i] = os.path.join(packagePath,v)
    #sens_filename looks like the sensitivity used for the first solve
           #before the non linear is used also used to get fieldnames
    sens_filename = sens_filenames[5]#5
    

#    print 'trialfilename', trialfilename
#    print 'sens_filename     ' ,sens_filename

    #usedperts are the perts to be used from sens_filename colums
    #usedperts are the compensators
    #old usedperts with tilts rather than rot
##    usedperts,force = zip(*[
##                    #('ztrans_object-ztrans_retro',0),Not used see allterns/weights
##                        #could be done here but that would require sens data more work
##                    ('ztrans_object',None),
##                    ('ztrans_m1',None),
##                    ('ztrans_retro',None),
##                    ('xtrans_object',None), 
##                    ('xtrans_m1',None),
##                   #('xtrans_retro',None),
##                    ('ytrans_object',None),
##                    ('ytrans_m1',None),
##                   #('ytrans_retro',None),
##                    ('xtilt_object',None),
##                    ('xtilt_m1',None),
##                    ('ytilt_object',None),
##                    ('ytilt_m1',None)
##                    ])
##
##
##    usedperts,force = zip(*[
##                    #('ztrans_object-ztrans_retro',0),Not used see allterns/weights
##                        #could be done here but that would require sens data more work
##                    ('ztrans_object',None),
##                    ('ztrans_m1',None),
##                    ('ztrans_retro',None),
##                    ('xtrans_object',None), 
##                    ('xtrans_m1',None),
##                                           #('xtrans_retro',None),
##                    ('ytrans_object',None),
##                    ('ytrans_m1',None),
##                                           #('ytrans_retro',None),
##                    ('xrot_object',None),
##                    ('xrot_m1',None),
##                    ('yrot_object',None),
##                    ('yrot_m1',None)
##                    ])
    usedperts,force = zip(*[
                    #('ztrans_object-ztrans_retro',0),Not used see allterns/weights
                        #could be done here but that would require sens data more work
                    ('ztrans_m1',None),
                    ('ztrans_retro',None),
                    ('ztrans_object',None),
                    ('xtrans_object',None), 
                    ('ytrans_object',None),
                                           #('xtrans_retro',None),
                    ('xrot_object',None),
                    ('yrot_object',None),
                                           #('ytrans_retro',None),
                    ('xtrans_m1',None),
                    ('ytrans_m1',None),
                    ('xrot_m1',None),
                    ('yrot_m1',None)
                    ])

    #field_0_z5 field_0_z6 weights must be set to 0 solution can not deal
    #with them.
    allterms, weights =  zip(*[
                 ('field_0_z4',1),
                 ('field_0_z5',0), #z5 and z6 must have zero weight
                 ('field_0_z6',0), #becouse they are not solveable directly 
                 ('field_0_z7',1),
                 ('field_0_z8',1),
                 ('field_0_z9',1),
                 ('field_0_z14',1),
                 ('field_0_z15',1),
                 ('field_0_z16',1),
                 ('field_0_avectx',0), #currety these terms don't work and 
                 ('field_0_avecty',0), #are not needed to solve
                 ('field_1_z4',1),
                 ('field_1_z5',0),
                 ('field_1_z6',0),
                 ('field_1_z7',1),
                 ('field_1_z8',1),
                 ('field_1_z9',1),
                 ('field_1_z14',1),
                 ('field_1_z15',1),
                 ('field_1_z16',1),
                 ('field_1_avectx',0),
                 ('field_1_avecty',0),
                 ('field_2_z4',1),
                 ('field_2_z5',0),
                 ('field_2_z6',0),
                 ('field_2_z7',1),
                 ('field_2_z8',1),
                 ('field_2_z9',1),
                 ('field_2_z14',1),
                 ('field_2_z15',1),
                 ('field_2_z16',1),
                 ('field_2_avectx',0),
                 ('field_2_avecty',0),
                 ('field_3_z4',1),
                 ('field_3_z5',0),
                 ('field_3_z6',0),
                 ('field_3_z7',1),
                 ('field_3_z8',1),
                 ('field_3_z9',1),
                 ('field_3_z14',1),
                 ('field_3_z15',1),
                 ('field_3_z16',1),
                 ('field_3_avectx',0),
                 ('field_3_avecty',0),
                 ('field_4_z4',1),
                 ('field_4_z5',0),
                 ('field_4_z6',0),
                 ('field_4_z7',1),
                 ('field_4_z8',1),
                 ('field_4_z9',1),
                 ('field_4_z14',1),
                 ('field_4_z15',1),
                 ('field_4_z16',1),
                 ('field_4_avectx',0),
                 ('field_4_avecty',0),
                 ('field_1_z5 - field_4_z5',1),
                 ('field_1_z5 - field_2_z5',1),
                 ('field_2_z5 - field_3_z5',1),
                 ('field_4_z5 - field_3_z5',1),
                 ('field_1_z6 - field_3_z6',1),
                 ('field_2_z6 - field_4_z6',1),
                 ('ztrans_obj - ztrans_ret',1000), #track length control
                 ])
    zlist = ['z4','z5','z6','z7','z8','z9','z14','z15','z16']
    force = list(force)
    weights = list(weights)
    return allterms,weights,usedperts,sens_filename,sens_filenames,force,zlist


#####################################
#trialfilename='systestdbl_simulated_01-Aug-2012_cset2_combination.csv'
#trialfilename= 'systestdbl_sens_01-Aug-2012_cset2_1.csv'
#trialfilename<str> name of CodeV csv file used to test solution algorithm.
#trialfilename='systestdbl_simulated_06-Aug-2012_cset2_special.csv'
#trialfilename = 'systestdbl_simulated_01-Aug-2012_cset2_all_v2.csv'
trialfilename = 'systestdbl_simulated_18-Feb-2014_cset2_all.csv'


if __name__ == '__main__':
    mali = Align(field_coord=1.)
    #mali.set_zt_obj_zt_ret(0)
    mali.set_tracklength(474)
    mali.set_target_tracklength(474)
    mali.plot_sens()
##    mali.set_trial_colum(colum_name='scenario4')
##    mali.make_z_from_scenario(trialfilename)
##    mali.make_z_zero()
    mali.make_z_from_GntSet('ap2n_field_','gnt')
##    gs = mali.get_GntSet()
    mali.set_astig_vectors()
   
##    gs.fitzern(8,xterms=[5,6])
##    gs.plot(suptitle='Trial Measured Error in fields Z4,7,8 Removed')
    mali.disp_varibles_matrix(title='Start',mode='z')
    mali.disp_varibles(mode='z')
    for i in [1,2,3,4,5]:
        mali.solve()
        mali.disp_varibles_matrix(title='After Solve',mode='res')
        #mali.disp_trial_solve()
        mali.disp_solve()
        print i
        raw_input('pause')
        mali.update_A()
    print 'done'
    
    
 

