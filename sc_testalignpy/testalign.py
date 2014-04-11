"""
testalign.py for hsfet met5 m1
script for solving for system alighment values using Sensitivity matrix

Importand convention for names used in script
    
Amat<2darray>  MxN Sensitivity or Design matrix contianing
            the independent variables for each N Perturbation.
            M is the number of measured variable(data points)
            N is the number of a N-dimensional parameter vector
            of the regression coefficients (number of terms being solved for)
                    
meas_variables<1darray>  Vector length M Measured or Dependent variables(data points) or terms

weights<1darray>  Vector length M containg weights for each M measured
                   variable(data points).
                   
force<list> of force values to apply N-dimensional parameter vector.

p<1darray>  N-dimensional parameter vector(compensator values).

Other commen names used
    usedperts<list> list of strings of pert names to be useded
    allterms<list> of strings of names of Measured Variables  ie. z9
    amounts<list> of amounts for each pert in sensitivity matrix
    units<list> of units for each amount

Method:
Weighted least squares is used to solve for p
Solves:
z = Ap (more persicley solves z = Ap + e where are e are random unknows
            varitions measured values of z)

The solution method:
W = diag(weights) #converts weights into a NxN diagonal matrix
p = inv((At.W.A)).At.W.z   (. is matrix dot multiply, At is transform of A)
matrix inv fuction done with singular-value decomposition (SVD).
"""
__version__='1.4.0'
__owner__ = 'bkestner'
'''
History:
8/22/13 1.4.0 bk added move_solve2()
before 8/13 bk Luc copied to Surdirs\MET5\SC_M1\R1\sc_testalignpy folder
5/30/13 bk copied from met5\m1\tstalignpy
3/13/13 1.3.0 bk added nocgh
3/11/13 1.2.2 cchen bug fixes in set_weights()
3/11/13 1.2.1 bk bug fixes added set_force()
3/9/13 1.2.0 bk new class TestAlign() version
3/7/13 1.1.0 bk changes
3/5/13 1.0.0 bk changed name to testalign.py added perts
3/4/13 b.0.1 bk fixed bugs in get_z()
3/3/13 b.0.0 bk created took basic code from met5 pob align2.py
'''
from ompy import *
import os
import sys
import numpy
import ompy.calcfuncs as calcfuncs


class TestAlign(object):
    """
    More docs needed
    """
    writename = 'xtestalign.txt'
    def __init__(self,sensfname='.\\setup\\sens_b_2.csv',
                 force='b',usedperts=None,allterms=None,weights=None):
        """
        Inputs:
        force<'b', 'c', 'cghz','nocgh' or list> if list is list of force values
                                  if 'b' sets force values to b alignment
                                  if 'c' sets force values to c alignment
                                  if 'cghz' sets force values to cghz alignment
             if force is 'b', 'c', 'cghz' usedperts must be None
             if force is list usedperts must be a list
        """
        self.usedperts = usedperts
        self.allterms = allterms
        self.weights = weights
        self.sensfname = sensfname
        self.p = None
        self.gs = None


        usedperts_nocgh,force_nocgh = zip(*[
                           ('xtrans_asph',None),
                           ('ytrans_asph',None),
                           ('xtilt_asph',None),
                           ('ytilt_asph',None),
                           ('xroll_cgh',0),
                           ('yroll_cgh',0),
                           ('xtilt_cgh',0),#0
                           ('ytilt_cgh',0),#0
                           ('ztrans_cgh',0),
                           ('ztrans_asph',None),
                           ('xtrans_ts_b',None),
                           ('ytrans_ts_b',None)])

        usedperts_cghz,force_cghz = zip(*[
                           ('xtrans_asph',None),
                           ('ytrans_asph',None),
                           ('xtilt_asph',None),
                           ('ytilt_asph',None),
                           ('xroll_cgh',None),
                           ('yroll_cgh',None),
                           ('xtilt_cgh',0),#0
                           ('ytilt_cgh',0),#0
                           ('ztrans_cgh',None),
                           ('ztrans_asph',None),
                           ('xtrans_ts_b',None),
                           ('ytrans_ts_b',None)])

        usedperts_b,force_b = zip(*[
                           ('xtrans_asph',None),
                           ('ytrans_asph',None),
                           ('xtilt_asph',None),
                           ('ytilt_asph',None),
                           ('xroll_cgh',None),
                           ('yroll_cgh',None),
                           ('xtilt_cgh',0),#0
                           ('ytilt_cgh',0),#0
                           ('ztrans_cgh',0),
                           ('ztrans_asph',None),
                           ('xtrans_ts_b',None),
                           ('ytrans_ts_b',None)])


        usedperts_c,force_c = zip(*[
                           ('xtrans_asph',None),
                           ('ytrans_asph',None),
                           ('xtilt_asph',None),
                           ('ytilt_asph',None),
                           ('xroll_cgh',None),
                           ('yroll_cgh',None),
                           ('xtilt_cgh',0),# Normaly 0 becouse of alignment ring on CGH
                           ('ytilt_cgh',0),#0
                           ('ztrans_cgh',None),
                           ('ztrans_asph',None),
                           ('xtrans_ts_c',None),
                           ('ytrans_ts_c',None)])
            
        #static_ is gs averged P2P (pixel to pexel) no rotation
             #(static test error)
        #asph_ is gs averged with trfm to rotate npos back to first postion
             #(part error)
        allterms2, weights2 =  zip(*[
                         ('static_avgz2',.1),
                         ('static_avgz3',.1),
                         ('static_avgz4',1),
                         ('static_avgz7',1),
                         ('static_avgz8',1),
                         ('static_avgz9',1),
                         ('static_avgz14',1),
                         ('static_avgz15',1),
                         ('asph_avgz2',.1),
                         ('asph_avgz3',.1),
                         ('asph_avgz7',1),
                         ('asph_avgz8',1),
                         ('asph_avgz14',1),
                         ('asph_avgz15',1)])

        if weights is None:
            self.weights = list(weights2)
        else:
            self.weights = list(weights)
        if allterms is None:
            self.allterms = allterms2
        else:
            self.allterms = allterms
        if isinstance(force,(list,tuple)):
            self.force = list(force)
            self.usedperts = list(usedperts)
        elif force.lower() == 'b' and usedperts is None:
            self.usedperts,self.force = usedperts_b,list(force_b)
        elif force.lower() == 'c' and usedperts is None:
            self.usedperts,self.force = usedperts_c,list(force_c)
        elif force.lower() == 'cghz' and usedperts is None:
            self.usedperts,self.force = usedperts_cghz,list(force_cghz)
        elif force.lower() == 'nocgh' and usedperts is None:
            self.usedperts,self.force = usedperts_nocgh,list(force_nocgh)
        elif hasattr(force,'__iter__')  and hasattr(usedperts,'__iter__'):
            self.usedperts,self.force = usedperts,list(force)
        else:
            raise TypeError,'force=%s and usedperts=%s not correct \n%s' % (force,usedperts,TestAlign.__init__.__doc__)
        self.read_sens_file()
        self.ammonts,self.units = self.get_amounts_units()
        self.make_Amat()
          # sample of all perts:  
##        usedperts_c,force_c = zip(*[
##                           ('xtrans_asph',None),
##                           ('ytrans_asph',None),
##                           ('xtilt_asph',None),
##                           ('ytilt_asph',None),
##                           ('xroll_cgh',None),
##                           ('yroll_cgh',None),
##                           ('xtilt_cgh',0),#0
##                           ('ytilt_cgh',0),#0
##                           ('ztrans_cgh',None),
##                           ('ztrans_asph',None),
##                           ('xtrans_ts_b',0),
##                           ('ytrans_ts_b',0),
##                           ('xtrans_ts_c',None),
##                           ('ytrans_ts_c',None)])
        

    def _sub_nom(self):
        """
        self._sub_nom()
        Subtracts values from nominal pert colums to all other colums in self.sens
        
        self.sens<dict> from read_sens_file()

        Output:
        No return Mutates self.sens 
        """
        perts = list(self.sens)
        if not 'nominal' in perts:
            print 'No nominal colum to subtract from pertubations'
            return 
        nom = self.sens['nominal']
        noml = list(nom)
        noml.remove('perturbation')
        noml.remove('units')
        noml.remove('amount')
        for pert in perts:
            for row in noml:
                try:
                    real = float(self.sens[pert][row])
                    self.sens[pert][row] = real - float(self.sens['nominal'][row])
                except:
                    print '\n Warning:Subtraction error in sub_num; will skip it\n'+\
                          'This is do to row or colum in sens not being a number\n'+\
                          'This is probebly not a problem.'
                    print 'pert',pert,'row',row
                    print 'sens[pert][row]',self.sens[pert][row]
                    continue
                
    def read_sens_file(self):
        """
        Reads sensitivty csv file
        
        Usage Example:
        self.read_sens_file()

        Output:
        self.sens<dict> contains data from senitivity file. Format:
            sens['pert ie xtrans_asph']['z4'] -> senitivity 
            sens['pert']['amount'] -> amount of perturbation
            sens['pert']['units'] -> unit of perturbation
        self.senstags<dict> all tags from read from file (currently not used)
        """
        tags = omsys.tagreader(self.sensfname)[0]
        sens = {}
        #make list of perturbations 
        perts = tags['perturbation'].strip(',').split(',')
        for i in xrange(len(perts[:])):
            perts[i] = perts[i].strip()
            sens[perts[i]]={}
        pertlen =len(perts)
        for key in tags:
            senvs = tags[key].strip(',').split(',')
            if len(senvs) == pertlen: # only items with correct len are results rows
                for i in xrange(pertlen):
                    sens[perts[i]][key] = senvs[i].strip()
        self.sens = sens
        self._sub_nom()
        self.senstags = tags
        self.p = None
        
    def set_force(self,force):
        """
        Sets self.force
        Input:
        force<list> of float values len must = len(self.usedperts)
        """
        if not len(force) == len(self.usedperts):
            raise ValueError, 'force list does not have same lenght as self.usedperts'
        self.force = force
        self.p = None
        self.res = None

    def set_weights(self,weights):
        """
        Sets self.weights
        Input:
        weights<list> of float values len must = len(self.allterms)
        """
        if not len(weights) == len(self.allterms):
            raise ValueError, 'weights list does not have same lenght as self.allterms'
        self.weights = weights
        self.p = None
        self.res = None


    def make_Amat(self):
        """
        Make the main sensitivity matrix
        self.Amat<2darray>  MxN Sensitivity or Design matrix contianing
                the independent variables for each N Perturbation.
                M is the number of measured variable(data points)
                N is the number of a N-dimensional parameter vector
                of the regression coefficients (number of terms being solved for)
        Uses:
        self.sens<dict> sensitivty data
        self.usedperts<list> list of strings of pert names to be useded
        self.allterms<list> of strings of names of Measured Variables  ie. z9
        """
        sens = self.sens
        usedperts = self.usedperts
        allterms = self.allterms
        n = len(usedperts)
        m = len(allterms) 
        A = numpy.zeros((m,n),dtype='float64')
        for k,term in enumerate(allterms):
            for p,pert in enumerate(usedperts):
                #print pert,term ,sens[pert][term]
                A[k,p] = float(sens[pert][term]) 
        self.Amat = A
        self.p = None

    def get_amounts_units(self):
        """
        Sorts out and returns amounts and units from codeV sens csv file
        uses:
        self.sens<dict> sens data from codev csv file
        self.usedperts<list> list of strings of pert names to be useded
        Ouptut lists have matching index values to usedperts
        Output:
        amounts<1darray> of floats of pert amount for each used pert
        units<list> of strings unit lables to go with amounts
        """
        amounts = []
        units = []
        for pert in self.usedperts:
            amounts.append(float(self.sens[pert]['amount']))
            units.append(self.sens[pert]['units'])
        amounts = numpy.array(amounts)
        return amounts,units


    def solve(self):
        """
        Solves for the the parameter vector p in z = Ap using
        weighted least squares. Main solution engine of align.
        
        Note: returned p values are scaled by values in sens amounts

        Used Attributes:
        Amat<2darray> M x N sensitivty matrix
        meas_variables<1darray> measured results M variable(data points)
        weights<list> Vector length M containg weights for each M measured
            variable(data points)
        force<list> of force values to apply N-dimensional parameter vector.
                    if value in list is None no force is applied
        Output:
        self.p<1darray> parameter vector scaled by amounts
        self.res<1darray> resdiual values of z after removing solition values
        self.iforce<list> of tuples [(index,force value),...] not used?
        """
        amounts = self.get_amounts_units()[0]
        A = self.Amat.copy()
        z = self.meas_variables.copy()
        iforce = []
        for i,v in enumerate(self.force):
            if not v is None:
                v /= amounts[i]
                iforce.append((i,v))
                A,z = calcfuncs.force(A,z,i,v)
        #(p, r, rank, s) = lstsq(A,z)
        p_unscaled = calcfuncs.wleast_squares(A,z,self.weights)
        self.res = self._get_residiual(A,p_unscaled,z)
        for t in  iforce:
            p_unscaled[t[0]] = t[1]
        self.p = p_unscaled * amounts
        self.iforce = iforce #not used?
    
    def _get_residiual(self,A,p,z):
        newz = numpy.dot(A,p)
        res = newz - z
        return res

    def set_z_from_scenario(self,trialfilename,column):
        """
        The M Measured variables vector used to solve for the
        parameter vector(compensator values) using sensitivity matrix
        z is self.meas_variables
        Input:
        trialfilename<str> name of CodeV csv file used to test solution algorithm.
                                scenario file to be read by read_sens_file()
        self.allterms<list> of strings of names of Measured Variables  ie. z9
        column<str> name of colum in Luc's spreed sheet exp: scenario2
        """
        data = read_sens_file(trialfilename)[0]
        m = len(self.allterms) 
        z = numpy.zeros(m,dtype='float64')
        for k,term in enumerate(self.allterms):
            z[k] = float(data[column][term])
        self.meas_variables = z
        self.trialdata  = data
        self.trialcolum = column
        self.trialfilename = trialfilename

    def get_gsmeas_variables(self,*gset,**kwds):
        """
        ge_gsmeas_variables('root','ext')
        self.meas_varibles = list of values of Measured Variables(units nm)
        Transform using fids to first data map.
        First data map must be aligned with y axis
        If needed xflip applied to data
        Input:
        gset<GntSet> or 'root','ext'
        fid=<str> fid name to use in tranform operation default fid='a'
        regrid=<int> regrid amount defualt is ngc=256, regrid = None->no regrid
        bnd=<Bnd> if present will crop GS
        Output:
        self.meas_variables<1darray> values of Measured Variables
        """
        if not 'fid' in kwds:
            fid='a'
        else:
            fid = kwds['fid']
        gs = GntSet(*gset)
        if 'regrid' in kwds and not kwds['regrid'] is None:
            gs.regrid(ngc=kwds['regrid'])
        elif not 'regrid' in kwds:
            gs.regrid(ngc=256)
        if 'bnd' in kwds:
            gs.crop(kwds['bnd'])
        flip =  gs[0].isstationflip()
        if flip is None:
            ask = raw_input(
                "Can't tell map flip statis. Do you want to X flip maps y/n")
            if ask.lower().startswith('y'):
                flip = True
            elif ask.lower().startswith('n'):
                flip = False
            else:
                raise ValueError,'you did not enter y or n'
        if flip:
            for i in range(len(gs)):
                gs[i] = gs[i].flip()
        avg_p2p = gs.avg(mode='p2p')
        avg_trfm = gs.avg(mode='trfm',fid=fid)
        avg_p2pz15  = avg_p2p.fitzern(15)
        avg_trfmz15 = avg_trfm.fitzern(15)
        z = []
        terms = [2,3,4,7,8,9,14,15]
        for term in [2,3,4,7,8,9,14,15]:
            z.append(avg_p2pz15.int[term] * 1e6)
        for term in [2,3,7,8,14,15]:
            z.append(avg_trfmz15.int[term] * 1e6)
        self.meas_variables = numpy.array(z)
        try:
            self.root = root
        except:
            self.root = 'unknown'
        self.p = None
        self.res = None
        self.gs = gs
        return 

    def set_meas_variables(self,values):
        """
        Output:
        self.meas_variables<1darray> values of Measured Variables
        """
        self.meas_variables = numpy.array(values)
        self.root = 'unknown'
        self.p = None
        self.res = None
        self.gs = None
        
    def disp_values(self,title=''):
        """
        Print values of Measured Variables
        Inputs:
        title<str>
        Output:
        rpt<Report>
        """
        rpt = Report()
        if self.p is None:
            self.disp_values2('input')
            return
        values_res  = self.res

        values_meas = self.meas_variables
        rpt += '\n   %s' % title
        rpt += 'Data From: %s' % self.root
        rpt += '                       Input      Residual'
        rpt += '        Variables     Values(nm)  Values(nm) Weights'
        for termname , v_m, v_r ,w in zip(self.allterms,values_meas,
                                   values_res,self.weights):
            pri  ='%s     %+9.2f   %+7.2f     %.1f' % (termname,v_m,v_r,w)
            pri=pri.rjust(48)
            rpt += pri
        rpt.disp()
        return rpt
    
    def disp_values2(self,mode,title=''):
        """
        Print values of Measured Variables
        Inputs:
        mode<'res' or 'input'>:
            'input'  Measured Measured Variables Values or
            'res'    Residual Measured Variables Values after solve
        title<str>
        """
        if mode == 'res':
            msg = 'Resdiual of'
            values = self.res
        elif mode == 'input':
            msg = '      Input'
            values = self.meas_variables
        print '\n   %s' % title
        print 'Data From: %s' % self.root
        print '%s Measured Variables    Value(nm) Weight' % msg
        for termname , v ,w in zip(self.allterms,values,self.weights):
            pri  ='%s  %7.2f     %.1f' % (termname , v,w)
            pri=pri.rjust(48)
            print pri

    def disp_solve(self,title=''):
        """
        print results of solve
        Used Attrabutes:
        usedperts<list> of used perts
        p<1darray> array of solved valeus
        force<1darray> force values None means no force
        Output:
        rpt<Report>
        """
        rpt = Report()
        units = self.get_amounts_units()[1]
        rpt += '\nData From: %s' % self.root
        rpt += title
        rpt +=  '\n   Compensator     Force  Solve_Amount  Units'
        for i,v in enumerate(self.usedperts):
            try:
                pj =  v+'   %+0.5f   %+0.5f  ' % (self.force[i],self.p[i])
            except TypeError:
                pj =  v+'     %s     %+0.5f  ' % (self.force[i],self.p[i])
            pj = pj.rjust(39)
            rpt += '%s %s' % (pj,units[i])
        rpt += '--------------------------------------------------'
        rpt.disp()
        return rpt
    
    def write(self,filename=None,mode='a'):
        """
        Writes results to file
        Inputs:
        filename<str> name of file to save to
        mode<str> file open mode 'a' or 'w'
                    'a' for file append
                    'w' not append
        """
        if self.p is None:
            print 'Must solve before Write'
            return
        if filename is None:
            filename = self.writename
        comment = raw_input('Add Comment to Write: ')
        rpt = self.disp_values()
        rpt += self.disp_solve(title=comment)
        rpt.save(filename,mode=mode)

    def disp_trial_solve(self):
        """
        print results of solve
        simulated scenario results
        """
        amounts,units = self.get_amounts_units()
        print  '\n  Perturbation    Amount  Solve_Amount  Sens_Seed'
        for i,v in enumerate(self.usedperts):
            try:
                #checks to see if row exits
                pert_amount = float(self.trialdata[self.trialcolum][v])
    ##            if 'tilt' in v:
    ##                pert_amount = math.radians(pert_amount)
    ##                units = 'rad'
    ##            else:
    ##                units = 'mm'
                pj =  v+'  %+0.5f  %+0.5f %+0.5f' % (pert_amount,p[i],amounts[i])
                pj = pj.rjust(45)
                print pj,units[i]
            except KeyError:
                units = '?'
                pj = v+'    None    %+0.5f %+0.5f' %(self.p[i],amounts[i])           
                pj = pj.rjust(45)
                print pj#,units
        print 'Pert Amount None means no row with Pert Amount must be zero'

    def move_solve(self,exclude=[],look=False,asktol=.2):
        """
        Creates move<dict> and runs self.move()
        Makes moves = -1 * self.p
        Inputs:
        exclude<list> perts to be excluded from moves exp:['ztrans_asph','ztrans_cgh']
        asktol<float> tolerance for asking to confirm move
        look<boo> if True will not move motors only print moves
        """
        #print '\n------ Planned Alignment Moves ----------'
        moves = {}
        perts = list(self.usedperts)
        for pert,value in zip(perts,self.p):
            if pert in exclude:
                continue
            if abs(value) > asktol:
                msg ='\n%s move value is %.5f\n Do you want to make this move?' % \
                    (pert,-value)
                if not omsys.ask_yn(msg,default=None):
                    continue               
            moves[pert] = -value
        #print '-------------------------------------------\n'
        self.move(moves,look=look)

    def move_solve2(self,move_amounts,look=False,asktol=.2):
        """
        Creates move<dict> and runs self.move()
        This method differs from move_solve() in that it taks a list
        move_amounts rather than exclude list to apply to self.p.
        Inputs:
        move_amounts<list> list of move amounts(mm) typicaly -1 * self.p
                        list index's must match self.usedperts item for item
        asktol<float> tolerance for asking to confirm move
        look<boo> if True will not move motors only print moves
        """
        moves = {}
        perts = list(self.usedperts)
        if not len(perts) == len(move_amounts):
            raise ValueError, 'list move_amounts not the same length as usedperts'
        for pert,value in zip(perts,move_amounts):
            if  abs(value) < 1e-8: # skip near zero numbers
                continue
            if abs(value) > asktol:
                msg ='\n%s move value is %.5f\n Do you want to make this move?' % \
                    (pert,value)
                if not omsys.ask_yn(msg,default=None):
                    continue               
            moves[pert] = value
        self.move(moves,look=look)

    def move(self,moves,tol=.000010,look=False):
        """
        Moves motors
        Inputs:
        moves<dict>  pert:moveAmount
        tol<float> if move amount < tol move is not performed
        look<boo> if True will not move motor 
        """

        #test.partobjects.movez.move( ' amount' )
##        alias=[('xtrans_asph', 'test.partobjects.movex.move'),# Debuging version
##              ('ytrans_asph', 'test.partobjects.movey.move' ),
##              ('ztrans_asph', 'test.partobjects.movez.move' ),
##              ('xtilt_asph' , 'test.partobjects.tiltx.move' ),
##              ('ytilt_asph' , 'test.partobjects.tilty.move' ),
##              ('xroll_cgh'  , 'test.cghobjects.movex.move ' ),
##              ('yroll_cgh'  , 'test.cghobjects.movey.move ' ),
##              ('xtilt_cgh'  , 'test.cghobjects.tiltx.move ' ),
##              ('ytilt_cgh'  , 'test.cghobjects.tilty.move ' ),
##              ('ztrans_cgh' , 'test.cghobjects.movez.move  ' )];look = True
        


        rnd = omsys.rndfilename(Extension='',length=4)[1:]
        raw_input('\n       ****** Shut Down Motors GUI Program******\nEnter to Continue:')
        ans = raw_input('Confirm Motors GUI Program is Shut Down by Entering %s: '% rnd)
        if ans.lower() == rnd.lower():
            sys.path.append('c:\\motions\\reorganized')
            if not look:
                os.chdir('c:\\motions\\reorganized')
                import m1test as test
        else:
            print "Can't Run Motors without confirmation Motor GUI is Shut Down"
            print "\n   *** Back to GUI ***\n"
            return
        alias=[('xtrans_asph', test.partobjects.movex.move ) ,
              ('ytrans_asph',  test.partobjects.movey.move ),
              ('ztrans_asph',  test.partobjects.movez.move ),
              ('xtilt_asph' ,  test.partobjects.tiltx.move ),
              ('ytilt_asph' ,  test.partobjects.tilty.move ),
              ('xroll_cgh'  ,  test.cghobjects.movex.move  ),
              ('yroll_cgh'  ,  test.cghobjects.movey.move  ),
              ('xtilt_cgh'  ,  test.cghobjects.tiltx.move  ),
              ('ytilt_cgh'  ,  test.cghobjects.tilty.move  ),
              ('ztrans_cgh' ,  test.cghobjects.movez.move  )]
        if not look:
            test.partobjects.movez.use_position_sensors(True)
            test.partobjects.movez.report_position_sensors(True)
            test.cghobjects.movez.use_position_sensors(True)
            test.cghobjects.movez.report_position_sensors(True)
        for key,func in alias:
            if key in moves:
                if abs(moves[key]) < tol:
                    continue
                msg =  'Moving: %s %s: %+0.5f' % (key,func,moves[key])
                print msg
                if not look:
                    func(moves[key])
                    print 'Move Finished'
        print '\n   *** Back to GUI ***\n'
    
    ##    axislist = [cghobjects.movex,
    ##            cghobjects.movey,
    ##            cghobjects.movez,
    ##            cghobjects.tiltx,
    ##            cghobjects.tilty,
    ##            partobjects.movex,
    ##            partobjects.movey,
    ##            partobjects.movez,
    ##            partobjects.tiltx,
    ##            partobjects.tilty,
    ##            partobjects.rotate,
    ##            reference.urmotor,
    ##            reference.goniometer] 
    ##    


##################################################################
##################################################################

if __name__ == '__main__':
        
    if len(sys.argv) < 3:
        root = raw_input('Enter Root for GntSet file names: ').lower()
        force = raw_input('       Enter Align mode; b, c, or cghz: ').lower()
    else:
        root = sys.argv[1]
        force = sys.argv[2]

    if not force in ['b','c', 'cghz','nocgh']:
        print ' Align mode not b, c ,cghz or nocgh'
        sys.exit()
    #udataarc()
    ta = TestAlign(force=force)
    #ta.make_Amat()
    ta.get_gsmeas_variables(root,'dat')
    #gs.plot(color='fringe')
    ta.solve()
    ta.disp_values()
    ta.disp_solve()
    ta.write()
    if omsys.ask_yn('\nDo you want to move motors?',default=False):
        ta.move_solve()

