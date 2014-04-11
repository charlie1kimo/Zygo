"""
script for solving for met5 system alighment values

Importand convention for names used in script
    
A<2darray>  MxN Sensitivity or Design matrix contianing
            the independent variables for each N Perturbation.
            M is the number of measured variable(data points)
            N is the number of a N-dimensional parameter vector
            of the regression coefficients (number of terms being solved for)
                    
z<1darray>  Vector lenght M Measured or Dependent variables(data points) or terms

weights<1darray>  Vector length M containg weights for each M measured
                   variable(data points). 

p<1darray>  N-dimensional parameter vector(compensator values).


Method:
Weighted least squares is used to solve for p
Solves:
z = Ap (more persicley solves z = Ap + e where are e are random unkown
            varitions measured values of z)

The solution method:
W = diag(weights) #converts wights into a NxN diagonal matrix
p = inv((At.W.A)).At.W.z   (. is matrix dot multiply, At is transform of A)
matrix inv fuction done with singular-value decomposition (SVD).
"""
'''
History:
12/2/12  bk modified make_z_from_GntSet() to take 'root','ext'
11/29/12 bk converted tuples to list types in _start()
11/26/12 bk added make_z_from_GntSet()
11/25/12 adding comments to align2.py pre saved align2.py as align2_arc.py
            upgraded many docs added get_GntSet() other small changes.
before 11/25/12:
align2.py came from align.py
align.py came from met5_plot_sens<int>.py devopment series
'''
import numpy
import math
import ompysys
import ompy.calcfuncs as calcfuncs
from numpy.linalg import lstsq
__version__ = '0.2.2'
__owner__ = 'bkestner'

class Align(object):
    """
    Class to create and manage methods for solving for
    MET5 system alignment ajustments.
    """
    def __init__(self):
        allterms,weights,usedperts,sens_filename,\
        sens_filenames,force = _start()
        self.allterms = allterms
        self.weights = weights
        self.usedperts = usedperts #compensators
        self.force = force
        self.trialfilename = None
        self.trail_colum = None
        self.z = None
        self.p = None
        self.res = None
        self.fields_sens = self.read_cv_file(sens_filename)
        amounts,units = self.get_amounts_units(self.fields_sens)
        self.amounts = amounts
        self.units = units
        self.sens_filenames = sens_filenames
        self.set_sens_coeffs()
        self.set_A()
        self.zt_obj_zt_ret = 0.0
        
    def set_zt_obj_zt_ret(self,value):
        """
        Set attribute self.zt_obj_zt_ret = value
        after set need to do or redo make_z_from...()
        """
        self.zt_obj_zt_ret = value
        self.z = None # need to do or redo make_z_from...()

    def set_trial_colum(self,colum_name='scenario4'):
        self.trial_colum = colum_name

    def set_sens_coeffs(self,plot=False,minrms=.001):
        """
        Solves for coeffs sen values that can be used to create sensitivity
        value for any amount to take care of non linear proplem.
        Takes a list of Luc's .csv file names that each have differant amount of
        for each Perturbation. Runs Make_A functoin to read all the
        resulting sensitivites then can make plot showing the results.

        Inputs:
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
        result_namel = list(plots['xtilt_m1'])
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
                #write,Print,dialog = pltfuncs.wPd_start(plt)
                #fig = plt.figure(figsize=((10.8,8)))
                fig = plt.figure(figsize=((16,10)))
                fig.suptitle('Sensitivity Result For:   %s   (nm RMS dbl pass WFE)' % result_name.upper(),fontsize=18)
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
                if term == 'astigx': #astig xy stuff does not work not used
                    for p,pert in enumerate(usedperts):
                        astigx = _get_astigs(field,pert)[0]
                        A[k,p] = astigx 
                elif term == 'astigy':
                    for p,pert in enumerate(usedperts):
                        astigy = _get_astigs(field,pert)[1]
                        A[k,p] = astigy                     
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

    def get_fieldnames(self):
        """
        Returns sorted <list> of feild names in self.fields_sens
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
        made from feild_# data from z4,5,6,7,8,9,16
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
        zlist = ['z4','z5','z6','z7','z8','z9','z16']
        dfterms={}
        for fname in fieldnames:
            dfterms[fname]= {}
        #field_0_z4 134.854064
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
        zlist = ['z4','z5','z6','z7','z8','z9','z16']
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

    def make_z_from_GntSet(self,*gs):
        """
        Returns z M Measured variables vector to solve
        parameter vector(compensator values) using sensitivity matrix self.A
        
        Inputs:
        gs<GntSet> or 'root','ext' Gnts croped to ca ready to have fitzern run
                if gs gs.original2 list must be names of
                feilds pattern -> feild_#
        allterms<list> of strings of names of row terms ie. field_0_z9
        """
        if len(gs) == 1:
            gs = gs[0]
        elif len(gs) == 2 and  isinstance(gs[0],basestring):
            import ompy
            gs = ompy.GntSet(gs[0],gs[1])
            #make original2 list of fieldnames
            org2 = []
            for i in xrange(len(gs)):
                org2.append('field_%s' % i)
            gs.original2 = org2[:]
        else:
            raise ValueError, 'gs argument not correct'
        allterms = self.allterms
        fields = {}
        for i in xrange(len(gs)):
            fieldname = gs.original2[i]
            gobj = gs[i]
            gz16 = gobj.fitzern(16,xterms=[10,11,12,13,14,15]).int * 1e6 
            fields[fieldname]= {'gz16':gz16}
        m = len(allterms)
        z = numpy.zeros(m,dtype='float64')
        for k,allterm in enumerate(allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                tnum = int(term[1:])
                field = fields[fieldname]
                if term == 'astigx': #astigxy stuff does not work, not used
                    pass
                    #if someday astigx y is made to work will need to
                    #update this code
##                    astigx = _get_astigs(field,colum)[0]
##                    z[k] = astigx 
                elif term == 'astigy':
                    pass
##                    astigy = _get_astigs(field,colum)[1]
##                    z[k] = astigy                     
                else:
                    z[k] = field['gz16'][tnum]
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
                z[k] = float(fields[fieldname1]['gz16'][tnum1]) - \
                       float(fields[fieldname2]['gz16'][tnum2])
            elif allterm == 'ztrans_obj - ztrans_ret':
                z[k] = self.zt_obj_zt_ret
            else:
                raise ValueError,'item in allterms not correct'
        self.z = z
            
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
        self.trialfilename = trialfilename
        allterms = self.allterms
        colum = self.trial_colum
        fields = self.read_cv_file(trialfilename)
        m = len(allterms) 
        z = numpy.zeros(m,dtype='float64')
        for k,allterm in enumerate(allterms):
            if not '-' in allterm:
                fieldname,term = allterm.rsplit('_',1)
                field = fields[fieldname]
                if term == 'astigx': #astigxy stuff does not work, not used
                    astigx = _get_astigs(field,colum)[0]
                    z[k] = astigx 
                elif term == 'astigy':
                    astigy = _get_astigs(field,colum)[1]
                    z[k] = astigy                     
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
            units = 'Units Latter'
            pj =  v+'   %+0.5f     %+0.5f  ' % (p[i],amounts[i])
            pj = pj.rjust(39)
            print pj,units
          
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
    
    def plot_sens(self,minrms=.001):
        """
        Takes a list of Luc's .csv file names that each have differant amount of
        Perturbation for each Perturbation. Runs get_A() method to read all the
        resulting sensitivites then makes plot show the results.
        
        These plots are an important indacator that this process is working.

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
            fig.suptitle('Sensitivity Result For:   %s   (nm RMS dbl pass WFE)' % result_name.upper(),fontsize=18)
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
        self.res = res

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
        #adds keys at same level as perts, should add only one
         #should only add one new key 'not_pert' to hold other info like
         #'x' and 'y'
        maintags,blocks = ompysys.tagreader(filename)[:2]
        fieldnames = list(blocks)
            
        fieldlocs=[]#field locations
        fields_tags = []
        for fieldname in fieldnames:
            #turn fieldnames into field locations f_x_y
            x , y = fieldname.strip(',').split('_')[1:]
            fieldlocs.append({'x':float(x),'y':float(y)})
            fieldtags = ompysys.tagreader(blocks[fieldname])[0]
            #missing = in file needs following
            illtags    = ompysys.tagreader(blocks[fieldname])[3]
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
        for i,field in enumerate(fields):
            dfields['field_%i' % i] = field
        if sub_nomanil_colum:
            dfields = self._sub_nom(dfields,perts)
        if additem1:
            #not used
            dfields = self.add_pert_zt_obj_zt_retro(dfields)
        return  dfields

def _get_residiual(A,p,z):
    newz = numpy.dot(A,p)
    res = newz - z
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

def _get_astigs(field,pert):
    """
    not used
    returns astigx and astigy
    these are made up astig terms
    not sure if this is correct or usfull
    all values of astigx and astigy are positive???
    Input:
    field<dict> of a field data
    pert<str> name pert
    astigx,astigy = get_astigs(field,'ytrans_object')
    """
    z5 = float(field[pert]['z5'])
    z6 = float(field[pert]['z6'])
##    astigx = 0.
##    astigy = 0.
    root2 = math.sqrt(2) / 2.
    if z5 >= 0 and z6 >= 0:
        '+ +'
        astigx = z5 * 1
        astigx += z6 * root2
        astigy = z6 * root2
    elif z5 < 0 and z6 >= 0:
        '- +'
        astigy = z5 * -1
        astigx = z6 * root2
        astigy += z6 * root2
    elif z5 < 0 and z6 < 0:
        '- -'
        astigy = z5 * -1
        astigy += z6 * -root2
        astigx = z6 * -root2
    elif z5 >= 0 and z6 < 0:
        '+ -'
        astigx = z5 * 1
        astigx += z6 * -root2
        astigy = z6 * -root2
    return astigx,astigy

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
    
    sens_filenames =('systestdbl_sens_01-Aug-2012_cset2_m6.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_m4.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_m2.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_m1.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_0.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_1.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_2.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_4.csv',
                     'systestdbl_sens_01-Aug-2012_cset2_6.csv')
    sens_filename = sens_filenames[5]#5
    

#    print 'trialfilename', trialfilename
#    print 'sens_filename     ' ,sens_filename

    #usedperts are the perts to be used from sens_filename colums
    #usedperts are the compensators
    usedperts,force = zip(*[
                    #('ztrans_object-ztrans_retro',0),Not used see allterns/weights
                        #could be done here but that would require sens data more work
                    ('ztrans_object',None),
                    ('ztrans_m1',None),
                    ('ztrans_retro',None),
                    ('xtrans_object',None), 
                    ('xtrans_m1',None),
                   #('xtrans_retro',None),
                    ('ytrans_object',None),
                    ('ytrans_m1',None),
                   #('ytrans_retro',None),
                    ('xtilt_object',None),
                    ('xtilt_m1',None),
                    ('ytilt_object',None),
                    ('ytilt_m1',None)
                    ])

    #astigx and astigy simply do not work
    #field_0_z5 field_0_z6 weights must be set to 0 solution can not deal
    #with them.
    allterms, weights =  zip(*[
                 ('field_0_z4',1),
                 ('field_0_z5',0), #z5 and z6 must have zero weight
                 ('field_0_z6',0), #becouse they are not solveable directly 
                 ('field_0_z7',1),
                 ('field_0_z8',1),
                 ('field_0_z9',1),
                 ('field_0_z16',1),
                 #('field_0_astigx',0), #currety these terms don't work and 
                 #('field_0_astigy',0), #are not needed to solve
                 ('field_1_z4',1),
                 ('field_1_z5',0),
                 ('field_1_z6',0),
                 ('field_1_z7',1),
                 ('field_1_z8',1),
                 ('field_1_z9',1),
                 ('field_1_z16',1),
                 #('field_1_astigx',0),
                 #('field_1_astigy',0),
                 ('field_2_z4',1),
                 ('field_2_z5',0),
                 ('field_2_z6',0),
                 ('field_2_z7',1),
                 ('field_2_z8',1),
                 ('field_2_z9',1),
                 ('field_2_z16',1),
                 #('field_2_astigx',0),
                 #('field_2_astigy',0),
                 ('field_3_z4',1),
                 ('field_3_z5',0),
                 ('field_3_z6',0),
                 ('field_3_z7',1),
                 ('field_3_z8',1),
                 ('field_3_z9',1),
                 ('field_3_z16',1),
                 #('field_3_astigx',0),
                 #('field_3_astigy',0),
                 ('field_4_z4',1),
                 ('field_4_z5',0),
                 ('field_4_z6',0),
                 ('field_4_z7',1),
                 ('field_4_z8',1),
                 ('field_4_z9',1),
                 ('field_4_z16',1),
                 #('field_4_astigx',0),
                 #('field_4_astigy',0),
                 ('field_1_z5 - field_4_z5',1),
                 ('field_1_z5 - field_2_z5',1),
                 ('field_2_z5 - field_3_z5',1),
                 ('field_4_z5 - field_3_z5',1),
                 ('field_1_z6 - field_3_z6',1),
                 ('field_2_z6 - field_4_z6',1),
                 ('ztrans_obj - ztrans_ret',0), #track length control
                 ])
    
    force = list(force)
    weights = list(weights)
    return allterms,weights,usedperts,sens_filename,sens_filenames,force


#####################################
#trialfilename<str> name of CodeV csv file used to test solution algorithm.
#trialfilename='systestdbl_simulated_06-Aug-2012_cset2_special.csv'
trialfilename='systestdbl_simulated_01-Aug-2012_cset2_all.csv'
#trialfilename='systestdbl_simulated_01-Aug-2012_cset2_combination.csv'
#trialfilename= 'systestdbl_sens_01-Aug-2012_cset2_1.csv'



if __name__ == '__main__':
    mali = Align()
    mali.set_zt_obj_zt_ret(0)
    #mali.plot_sens()
    mali.set_trial_colum(colum_name='scenario4')
    mali.make_z_from_scenario(trialfilename)
##    gs = mali.get_GntSet()
##    gs.save('xdogs')
    
      #next save gs and run using gs without .make_z_from_scenario()
        #will  need to have .original2 have fieldnames
    #mali.make_z_from_GntSet(gs)
##    mali.make_z_from_GntSet('xdogs_','gnt')
##    gs = mali.get_GntSet()
   
##    gs.fitzern(8,xterms=[5,6])
##    gs.plot(suptitle='Trial Measured Error in fields Z4,7,8 Removed')
    mali.disp_varibles_matrix(title='Start',mode='z')
    mali.disp_varibles(mode='z')
    for i in [1,2,3]:
        mali.solve()
        mali.disp_varibles_matrix(title='After Solve',mode='res')
        mali.disp_trial_solve()
        mali.disp_solve()
        print i
        raw_input('pause')
        mali.update_A()
    print 'done'
    
    


