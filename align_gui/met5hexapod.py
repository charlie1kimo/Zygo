
"""
met5hexapod.py
Calculate sensitivity table for MET5\HSFET POB hexapod
Calculate leg length changes needed for optical alignment
Classes:
Hexsens()   Methods to create sensitivity table
Hexalign()  Methods to create sensitivity matrix and alignment algorithms
"""
__version__ = '0.7.0'
__owner__ = 'bkestner'
'''
History:
11/25/13 0.7.0 bk fixed bugs in save_capGauge_readings() and added comment= arg
11/22/13 BK Rem out save gage readings
9/30/13 bk added leg change function and renamed cap change function
9/20/13 added numpy.NaN
9//18/2013 bk 0.3.0 new vector methods for capGauge changes new Node coord from Matt
9/15/2013 bk 0.2.0 added leg legnth matrix solve items
9/7/2013 bk 0.1.0 minor changes
9/2/2013 BK created
'''
from ompy import *
import math
import numpy
import datetime


class Hexsens(object):
    """
    Methods to create sensitivity table for MET5\HSFET POB hexapod.
        The sensitivity table is a dictionary of sensitivities not the final
        matrix
        
    Construction:
    self.nodesM1<arr> xyz coordinates of hexapod legs nodes on motion side
    self.nodesM2<arr> xyz coordinates of hexapod legs nodes on static side
    self.leginds<list> indexes for node arrays to create leg order 1,2,3,...
    self.capGauges<arr> xyz coordinates of hexapod legs capGauges locations
    self.capindes<list> indexes to match capGauges array to legs in order 
    self.legseps<arr> Nominal leg lengths Node to Node
    #self.capseps<arr> Nominal Cap Gauge reading length
    
    self.senscaps<dict> of sens info for cap gauges changes
    self.senslegs<dict> of sens info for leg length changes
    self.perts<list> Names of known variables each a single m1 move
                        i.e. xrot,ytrans etc.
    self.terms<list> Names of unknown variables cap gauge names for
                        reading changes needed to compensate.
                        i.e. cap1,cap2 etc.
    self.amounts<list> perturbation amounts for each pert in perts in senscaps
    self.pertunits<list> units for each pert mm or radians

    No save method becouse recalculating each time is fast

    Important Note about Cap Gauges:
    The motions of the hexapod is monitored by Cap Gauges looking at the
    relative length of each leg. The Cap Gauges do not directly measure a
    single leg length change because they are offset from the nodes. The
    regression methods used are calculating required relative cap gauge
    reading changes which is slightly different the single leg length changes.
    """
    #cord of hex legs on M1 side x    ,    y   ,    z
    nodesM1 =  numpy.array([[-42.500, +73.612, 38.000],
                            [+85.000,  0.000 , 38.000],
                            [-42.500, -73.612, 38.000]])
    #cord of hex legs on M2 side x    ,    y   ,    z
    nodesM2 =  numpy.array([[+85.000 , -147.224, 185.224],
                            [+85.000 , +147.224, 185.224],
                            [-170.000,    0.000, 185.224]])    
    #    nodesm2,nodesm1 index of node cord per each leg
    legind1 = [1,0]
    legind2 = [2,0]
    legind3 = [2,2]
    legind4 = [0,2]
    legind5 = [0,1]
    legind6 = [1,1]
    leginds = [legind1,legind2,legind3,legind4,legind5,legind6]
    # [row,col]

    #cap gauge location for each leg 1 through 6
    capGauges = numpy.array([[ -50.493 ,+74.771 , 55.657 ],
                            [ -39.507 , 81.114 , 55.657 ],
                            [ -39.507 ,-81.114 , 55.657 ],
                            [ -50.493 ,-74.771 , 55.657 ],
                            [ +90.000 , +6.343 , 55.657 ],
                            [ +90.000 , -6.343 , 55.657 ]])
    #cap node index to match up with cap gauge on each leg
    #not used
    capinds = [legind1[0],legind2[0],legind3[0],legind4[0],legind5[0],legind6[0]]

    def __init__(self):
        #staring un perturbed leg lengths node to node
        self.legseps = self.get_legseps(self.nodesM1)
        #print 'Leg Lengths:\n',self.legseps
        #staring un perturbed cap gauge lengths M1 node to leg
        self.capvectors = self.get_capvectors()
        
        senscaps,senslegs,perts,terms,amounts,units = self.get_sensdict(.1,.001)
        self.senscaps = senscaps
        self.senslegs = senslegs
        self.perts = perts
        self.terms = terms
        self.amounts = amounts
        self.pertunits = units


    def vect_proj(node_xyz1,node_xyz2,cg_xyz1,cg_xyz2):

        '''
        not used
        chg_along_vector = H.vect_proj(node_xyz1,node_xyz2,cg_xyz1,cg_xyz2)

        Function to determine the absolute distance, projected along a vector
        direction.
        The distance is determined from the two cg_xyz coordinates, and the
        unit direction vector is determined from the two node_xyz coordinates.

        Returns the magnitude of the distance.    

        node_xyz1 <tuple>   (x,y,z) coordinates of hexapod leg node 1
                                for met5 make node 1 the m1 nodes
        node_xyz2 <tuple>   (x,y,z) coordinates of hexapod leg node 2
                                for met5 make node 2 the m2 nodes
            end points forming a line used to determine the direction of a
            unit vector.

        cg_xyz1 <tuple>     (x,y,z) coord. of hexapod cap-gauge target point 1
                                for met5 point 1 is the static point
        cg_xzy2 <tuple>     (x,y,z) coord. of hexapod cap-gauge target point 2
                                for met5 point 2 is on the leg and it moves
            position of two points in space (or before/after move) used to
            determine move/change between two points, projected along a
            direction    
        '''
        # legvect [dx,dy,dz] d = 2 - 1
        legvect = nunpy.array(node_xyz2) - numpy.array(node_xyz1)
        # unitvect unit vector dicrection cos [l,m,n] normilized to length 1
        unitvect = legvect / numpy.sqrt((legvect**2).sum())
        # cgmove [dx,dy,dz] d = 2 - 1
        cgmove = numpy.array(cg_xyz2) - numpy.array(cg_xyz1)
        # matrix multiply to get distance change in direction of unitect
        chg_along_vector = np.dot(cgmove,unitvect)
        return chg_along_vector

    def get_sensitivity(self,xrot=0,yrot=0,zrot=0.,xtrans=0,ytrans=0,ztrans=0):
        """
        capsdiff,legsdiff = H.get_sensitivity(...)
        Returns change in leg length and cap gauge readings
        only change one input at a time
        
        Input:
        rotation in radians or translation in mm
        Ouput:
        legsdiff <1darray> leg length change node to node
        capsdiff <1darray> cap gauge reading change
        """
        newM1    = self.transform(self.nodesM1  ,xrot,yrot,zrot,xtrans,ytrans,ztrans)
        newnodeM1seps = self.get_legseps(newM1)
        legsdiff =  self.legsdiff(newnodeM1seps)
        
        new_caps = self.transform(self.capGauges,xrot,yrot,zrot,xtrans,ytrans,ztrans)
        #newcapseps = self.get_capseps(new_caps)
        capsdiff = self.capsdiff(new_caps)
        return capsdiff, legsdiff

    def get_sensitivity2(self,**kwds):
        """
        capsdiff,legsdiff = H.get_sensitivity2(...)
        Returns change in leg length and cap gauge readings
        only change one input at a time
    
        Input:
        rotation in radians or tranlation in mm
        Ouput:
        capsdiff <1darray> cap gauge reading change
        legsdiff <1darray> leg length change
        """
        newM1    = self.transform(self.nodesM1  ,**kwds)
        newnodeM1seps = self.get_legseps(newM1)
        legsdiff =  self.legsdiff(newnodeM1seps)
        
        new_caps = self.transform(self.capGauges,**kwds)
        #newcapseps = self.get_capseps(new_caps)
        capsdiff = self.capsdiff(new_caps)
        return capsdiff, legsdiff

    def get_capvectors(self):
        """
        legseps = H.get_legseps(nodesM1)
        Calculates length (seperation of nodes) of legs
        Input:
        nodesM1<arr> current coordinates of M1 nodes
        Ouput:
        legseps<1darray> length of legs
        """
        def get_unitVector(node_xyz1,node_xyz2):
            """
            Function to return unit vector.
            Returns the magnitude of the distance.    

            node_xyz1 <tuple>   (x,y,z) coordinates of hexapod leg node 1
                                    for met5 make node 1 the m1 nodes
            node_xyz2 <tuple>   (x,y,z) coordinates of hexapod leg node 2
                                    for met5 make node 2 the m2 nodes
                end points forming a line used to determine the direction of a
                unit vector.  
            """
            # legvect [dx,dy,dz] d = 2 - 1
            legvect = numpy.array(node_xyz2) - numpy.array(node_xyz1)
            # unitvect unit vector dicrection cos [l,m,n] normilized to length 1
            unit_Vector = legvect / numpy.sqrt((legvect**2).sum())
            return unit_Vector
        
        capvectors = []
        for ind in self.leginds:
            x1 = self.nodesM2[ind[0]][0]
            x2 = self.nodesM1[ind[1]][0]
            y1 = self.nodesM2[ind[0]][1]
            y2 = self.nodesM1[ind[1]][1]
            z1 = self.nodesM2[ind[0]][2]
            z2 = self.nodesM1[ind[1]][2]
            capvectors.append(get_unitVector([x1,y1,z1],[x2,y2,z2]))
        return numpy.array(capvectors)

    def get_legseps(self,nodesM1):
        """
        legseps = H.get_legseps(nodesM1)
        Calculates length (seperation of nodes) of legs
        Input:
        nodesM1<arr> current coordinates of M1 nodes
        Ouput:
        legseps<1darray> length of legs
        """
        legseps = []
        for ind in self.leginds:
            x1 = self.nodesM2[ind[0]][0]
            x2 = nodesM1[ind[1]][0]
            y1 = self.nodesM2[ind[0]][1]
            y2 = nodesM1[ind[1]][1]
            z1 = self.nodesM2[ind[0]][2]
            z2 = nodesM1[ind[1]][2]
            legseps.append(math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2))
        return numpy.array(legseps)

    def get_capseps(self,capcord):
        """
        Not used
        capseps = H.get_legseps(nodesM1)
        Calculates seperation of M2nodes and Cap Gauge read point on legs
        Input:
        nodesM1<arr> current coordinates of M1 nodes
        Ouput:
        capseps<1darray> seperations index 0 is for leg1 ...
        """
        capseps = []
        for i,ind in enumerate(self.capinds):
            x1 = self.nodesM2[ind][0] 
            x2 = capcord[i][0]
            y1 = self.nodesM2[ind][1]
            y2 = capcord[i][1]
            z1 = self.nodesM2[ind][2] + 17.65*math.sqrt(2)########################
            z2 = capcord[i][2]
            capseps.append(math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2))
        return numpy.array(capseps)
    
    def legsdiff(self,new_legseps):
        """
        legsdiff = H.legsdiff(new_legseps)
        returns 1darray of leg length diff from self.legseps
        """
        return new_legseps - self.legseps

    def capsdiff(self,new_caps):
        """
        capsdiff = H.capsdiff(new_caps)
        returns 1darray of cap seperation length along vector
        """

        def vect_proj(unit_vector,cg_xyz1,cg_xyz2):
            '''
            chg_along_vector = H.vect_proj(cg_xyz1,cg_xyz2)

            Function to determine the absolute distance, projected along a vector
            direction.
            The distance is determined from the two cg_xyz coordinates, and the
            unit direction vector is determined from the two node_xyz coordinates.

            Returns the magnitude of the distance.    


            cg_xyz1 <tuple>     (x,y,z) coord. of hexapod cap-gauge target point 1
                                    for met5 point 1 is the static point
            cg_xzy2 <tuple>     (x,y,z) coord. of hexapod cap-gauge target point 2
                                    for met5 point 2 is on the leg and it moves
                position of two points in space (or before/after move) used to
                determine move/change between two points, projected along a
                direction    
            '''
            # cgmove [dx,dy,dz] d = 2 - 1
            cgmove = numpy.array(cg_xyz2) - numpy.array(cg_xyz1)
            # matrix multiply to get distance change in direction of unitect
            chg_along_vector = numpy.dot(cgmove,unit_vector)
            return chg_along_vector
        capsdiff = []
        for i in range(len(self.capGauges)):
            capsdiff.append(vect_proj(self.capvectors[i],self.capGauges[i,:],new_caps[i]))                       
        return numpy.array(capsdiff)


    def transform(self,arr,xrot=0,yrot=0,zrot=0,xtrans=0,ytrans=0,ztrans=0):
        """
        new_arr = self.transform(...)
        Returns arr with data points rotated and translated in the following order:
        Scale x,y,z Rotations x,y,z Translation x,y,z
        scale is set to 1.
        Inputs
        arr np.array of x,y,z 
        xrot,yrot,zrot angle to rotate in radians
        ztrans,ytrans,ztrans amount to translate in mm
        """
        '''
        scale=<number or tuple> if not 1 then will also scale returned xyz
                if tuple (xscale,yscale,zscale)
        '''
        scale = 1.0
        import math
        import numpy

        cosx = math.cos(xrot)
        sinx = math.sin(xrot)
        cosy = math.cos(yrot)
        siny = math.sin(yrot)
        cosz = math.cos(zrot)
        sinz = math.sin(zrot)

        R = numpy.zeros((4,4))
        R[0,0] = cosy * cosz
        R[1,0] = cosy * sinz
        R[2,0] = -siny
        R[3,0] = 0.

        R[0,1] = -cosx * sinz + sinx * siny * cosz
        R[1,1] = cosx * cosz + sinx * siny * sinz
        R[2,1] = sinx * cosy
        R[3,1] = 0.

        R[0,2] = sinx * sinz + cosx * siny * cosz
        R[1,2] = -sinx * cosz + cosx * siny * sinz
        R[2,2] = cosx * cosy
        R[3,2] = 0.

        R[0,3] = xtrans
        R[1,3] = ytrans
        R[2,3] = ztrans
        R[3,3] = 1.
        if not scale == 1:
            if isinstance(scale,(list,tuple)) and len(scale) == 3:
                xs = scale[0]
                ys = scale[1]
                zs = scale[2]
            else:
                xs = scale
                ys = scale
                zs = scale
            S = numpy.identity(4)
            S[0,0] = xs
            S[1,1] = ys
            S[2,2] = zs
            #combine scale matrix with Rotation matrix
            R = numpy.dot(R,S)
        v = numpy.ones((4,(len(arr))))
        v[0,:] = arr[:,0] # x
        v[1,:] = arr[:,1] # y
        v[2,:] = arr[:,2] # z

        newx,newy,newz , a = numpy.dot(R,v)
        return numpy.array(zip(newx,newy,newz))

    def transform2(self,arr,**kwds):
        """
        not used
        new_arr = self.transform(...)
        Returns arr with data points rotated and translated in the following order:
        Scale x,y,z Rotations x,y,z Translation x,y,z
        scale is set to 1.
        Inputs
        arr np.array of x,y,z 
        xrot,yrot,zrot angle to rotate in radians
        ztrans,ytrans,ztrans amount to translate in mm
        """
        '''
        scale=<number or tuple> if not 1 then will also scale returned xyz
                if tuple (xscale,yscale,zscale)
        '''
        scale = 1.0
        import math
        import numpy

        xtrans,ytrans,ztrans,xrot,yrot,zrot = 0
        for k,v in kwds.items():
            exec ('%s = %s' % (k,v))
        cosx = math.cos(xrot)
        sinx = math.sin(xrot)
        cosy = math.cos(yrot)
        siny = math.sin(yrot)
        cosz = math.cos(zrot)
        sinz = math.sin(zrot)

        R = numpy.zeros((4,4))
        R[0,0] = cosy * cosz
        R[1,0] = cosy * sinz
        R[2,0] = -siny
        R[3,0] = 0.

        R[0,1] = -cosx * sinz + sinx * siny * cosz
        R[1,1] = cosx * cosz + sinx * siny * sinz
        R[2,1] = sinx * cosy
        R[3,1] = 0.

        R[0,2] = sinx * sinz + cosx * siny * cosz
        R[1,2] = -sinx * cosz + cosx * siny * sinz
        R[2,2] = cosx * cosy
        R[3,2] = 0.

        R[0,3] = xtrans
        R[1,3] = ytrans
        R[2,3] = ztrans
        R[3,3] = 1.
        if not scale == 1:
            if isinstance(scale,(list,tuple)) and len(scale) == 3:
                xs = scale[0]
                ys = scale[1]
                zs = scale[2]
            else:
                xs = scale
                ys = scale
                zs = scale
            S = numpy.identity(4)
            S[0,0] = xs
            S[1,1] = ys
            S[2,2] = zs
            #combine scale matrix with Rotation matrix
            R = numpy.dot(R,S)
        v = numpy.ones((4,(len(arr))))
        v[0,:] = arr[:,0] # x
        v[1,:] = arr[:,1] # y
        v[2,:] = arr[:,2] # z
        newx,newy,newz , a = numpy.dot(R,v)
        return numpy.array(zip(newx,newy,newz))

    def get_sensdict(self,translations_xyz =.1 , rotations_xyz = .001):
        """
        senscaps,senslegs,perts,terms,amounts,units = H.get_sensdict()
        
        Inputs:
        translations_xyz<float> value for each translation x,y,z mm
        rotations_xyz<float> value for each rotation x,y,z radians
        Output:
        senscaps<dict> sensalign.py format sensitivity dict for capgauges
        senslegs<dict> sensalign.py format sensitivity dict for leg lengths
        perts<list>  compensators
        terms<list>  measurable indapendent varibles
        amounts<list> from senscaps dict
        units<list> from senscaps dict
        """
        senscaps = {}
        senslegs = {}
        terms = ['cap1','cap2','cap3','cap4','cap5','cap6']
        perts = ['xrot','yrot','zrot','xtrans','ytrans','ztrans']
        amounts = []
        units = []
        for pert in perts:
            kwds = {}
            if pert.endswith('trans'):
                kwds = {} # just to be safe
                kwds[pert]= translations_xyz
                unit = 'mm'
                capsdiff,legsdiff = self.get_sensitivity2(**kwds)
                senscaps[pert]={}
                senslegs[pert]={}
                senscaps[pert]['amount'] = translations_xyz
                senscaps[pert]['units'] = unit
                senslegs[pert]['amount'] = translations_xyz
                senslegs[pert]['units'] = unit
                amounts.append(senscaps[pert]['amount'])
                units.append(senscaps[pert]['units'])
                for i,term in enumerate(terms):
                    senscaps[pert][term] = capsdiff[i]
                    senslegs[pert][term] = legsdiff[i]
            elif pert.endswith('rot'):
                kwds = {} # just to be safe
                kwds[pert]= rotations_xyz
                unit = 'Radains'
                capsdiff,legsdiff = self.get_sensitivity2(**kwds)
                senscaps[pert]={}
                senslegs[pert]={}
                senscaps[pert]['amount'] = rotations_xyz
                senscaps[pert]['units'] = unit
                senslegs[pert]['amount'] = rotations_xyz
                senslegs[pert]['units'] = unit
                amounts.append(senscaps[pert]['amount'])
                units.append(senscaps[pert]['units'])
                for i,term in enumerate(terms):
                    senscaps[pert][term] = capsdiff[i]
                    senslegs[pert][term] = legsdiff[i]
        return senscaps,senslegs,perts,terms,amounts,units

    def get_trail_values(self,xrot=0,yrot=0,zrot=0,xtrans=0,ytrans=0,ztrans=0):
        """
        amounts,cap_changes = H.get_trail_values()
        
        Inputs:
        translations<float> values for each pertabation translation x,y,z mm
        rotations<float> values for each pertabation rotation x,y,z radians
        Output:
        amounts<list> of numbers for perts amount from args
        meas_varibles<list> simulated list of measured varibles cabgauge changes
        """
        amounts = [xrot,yrot,zrot,xtrans,ytrans,ztrans]#in same order as usedperts
        capsdiff,legsdiff = self.get_sensitivity(xrot=xrot,
                                                  yrot=yrot,
                                                  zrot=zrot,
                                                  xtrans=xtrans,
                                                  ytrans=ytrans,
                                                  ztrans=ztrans)
               
        return amounts,capsdiff

class Hexalign(object):
    """
    Class to Solve necessary Hexapod leg length changes needed to achieve
    required perturbation adjustments of the M1 mirror i.e. xtrans ytrans etc.
    
    Construction:
    self.hexs          Instance of Hexsens
    self.Amat_caps     Sensitivity matrix calculated from Hexsens.senscaps dict
    self.Amat_legs     Sensitivity matrix calculated from Hexsens.senslegs dict
    self.pert_adjusts  Desired M1 adjustments i.e. xtrans ytrans xrot etc
    self.cap_changes   Calculated Cap Gauge changes to cause leg length changes
                       needed to achieve desired M1 adjustments.
    self.leg_changes   Calculated leg length changes needed to achieve desired
                       M1 adjustments.

    Creates square Sensitivity Matrix A (self.Amat_sens)
    cap_changes = A * pert_adjusts

    
    Usage Example:
    import met5hexapod
    hexa = met5hexapod.Hexalign('1')
    hexa.set_pert_adjusts([.0001,.0007,None,-.015,.03,.02])
    hexa.solve()
    hexa.disp_solve()
    hexa.move()                      
    """
    def __init__(self,hexopod_id):
        """
        Inputs:
        hexopod_id<str> Id of hexopod. This used to track capgauge readings
        """
        self.hexopod_id = hexopod_id
        self.hexs = Hexsens()
        self.pert_adjusts = None#amounts to adjust m1 mirror i.e. xtrans ytrans etc
        self.cap_changes = None #solve values for adjusting perts
        self.leg_changes = None
        self.Amat_caps = self._getAmat(self.hexs.senscaps)
        self.Amat_legs = self._getAmat(self.hexs.senslegs)
        # the following for testing only not part of final class
        #cap_readings = [0.,0.,0.,0.,0.,0.]
        #self.save_capGauge_readings(cap_readings,filenameroot='hex_cg_readings',
        #                      ext='txt',mode='new')
    
    def _getAmat(self,sens):
        """
        Amat = _getAmat(sens)
        Make the main sensitivity matrix
        Amat<2darray>  6x6 Sensitivity or Design matrix contianing
                the independent variables for each  Perturbation.
        Input:
        sens<dict> sensitivty data
        Uses:
        self.hexs.perts<list> list of strings of pert names to be useded
        self.hexs.terms<list> of strings of names of Measured Variables  i.e. z9
        """
        #sens = self.hexs.sens
        usedperts = self.hexs.perts
        allterms = self.hexs.terms
        n = len(usedperts)
        m = len(allterms) 
        A = numpy.zeros((m,n),dtype='float64')
        for k,term in enumerate(allterms):
            for p,pert in enumerate(usedperts):
                #print pert,term ,sens[pert][term]
                A[k,p] = float(sens[pert][term]) 
        return A
        
    def solve(self):
        """
        This version of solve does not invert matrix A
        Solves (Calculates) for the the parameter vector z in z = Ap
        Using simple .dot() Matrix multiply.
        The A matrix is and must be square.
        hexapod.py has the terms and perts somewhat reversed
        perts are xtrans, ytrans but they are in use are the knowns
        terms are capGauge reading changes and they are the compensatores.

        No least Squares, no force and no weights
        
        Used Attributes:
        self.pert_adjusts<list> of values for measusred pertabations
                            becoumes the self.p array
        self.Amat_caps<2darray> 6x6 sensitivty matrix
        self.Amat_legs<2darray> 6x6 sensitivty matrix
        Sets:
        self.cap_changes<1darray> amounts to change cap gauges to cause
                                    desired pert_adjusts
        self.leg_changes<1darray> amounts to change leg lengths to cause
                                    desired pert_adjusts
                                    
            self.cap_changes are probebly -1 * required change to correct
        """
        def solve_each(A):
            p = numpy.array(self.pert_adjusts)
            p_unscaled = p / self.hexs.amounts
            changes = numpy.dot(A,p_unscaled)
            #print 'changes' , changes
            res = self._get_residiual(A,p_unscaled,changes)#not used
                                                           #should all be zero
            return changes,res


            
        if self.pert_adjusts[2] is None or \
           numpy.isnan(self.pert_adjusts[2]):
            self.min_zrot()
##        A = self.Amat.copy()
##        p = numpy.array(self.pert_adjusts)
##        p_unscaled = p / self.hexs.amounts
##        self.cap_changes = numpy.dot(A,p_unscaled)
##        #print 'self.cap_changes' , self.cap_changes
##        res = self._get_residiual(A,p_unscaled,self.cap_changes)

        self.cap_changes, self.rescaps = solve_each(self.Amat_caps)
        self.leg_changes, self.rescaps = solve_each(self.Amat_legs)

    def min_zrot(self):
        """
        Optimize Z rotation to minimize leg length change
        """
        from scipy.optimize import fmin,anneal,fminbound,brent
        rpt = Report('\n*** Optimize Z Rotation to Minimize Leg Length Change ***')
        func = 'fminbound'
        
        def abscaps(zrot):
            """
            Returns max abs change in hexapod capGauge
            Input:
            zrot<float> zrot value in radians
            """
            self.pert_adjusts[2] = zrot
            self.solve()
            maxmove = numpy.abs(self.cap_changes).max()
            #print 'zrot',zrot , 'maxmove',maxmove
            return maxmove

        def abslegs(zrot):
            """
            Returns max abs change in hexapod leg lengths
            Input:
            zrot<float> zrot value in radians
            """
            self.pert_adjusts[2] = zrot
            self.solve()
            maxmove = numpy.abs(self.leg_changes).max()
            #print 'zrot',zrot , 'maxmove',maxmove
            return maxmove
            
##        if func=='fmin':
##            #looks like fminbound works better here
##            print func
##            #xtol=fittol,ftol=fittol,
##            zrot_start = -.0003
##            vsolved = fmin(abslegss, zrot_start, maxiter=1000, maxfun=1000)
##            print 'Final min zrot',vsolved

        if func=='fminbound':
            preleg = abslegs(0.0)
            zrot,absleg,fail,maxfun = fminbound(abslegs, -.001, .001,
                            xtol=1e-05, maxfun=500, full_output=True, disp=3)
            if fail:
                rpt += 'zrot optimize failed. Setting zrot to = 0.0'
                zrot = 0.0
                absleg = abslegs(zrot)
            rpt += ''
            rpt += 'Optimization Function: %s' % func
            rpt += ' Final Optimization Results zrot: %+.6f radians' % zrot
            rpt += '      Absolute leg length change: %+.3f mm' % absleg
            rpt += ' Pre Optimization leg len change: %+.3f mm' % preleg
            rpt += '        Optimized Length savings: %+.3f mm' % (preleg-absleg)
        print rpt
        return rpt


    def single_cap(self,num,amount=.1):
        """
        This is an experimental function to see if the effect of single
        cap gauge length changes can be isolated and the resulting change
        to xtrans ytrans ztrans xrot yrot zrot found. This would allow making
        a normal sensalign.py sensitivity dict and matrix. Presumably this could
        also be done my simply inverting the current A matrix.
        Input:
        num<int> leg number 1 - 6
        amount<float> change in mm
        Output:
        pert_adjusts<arr> M1 adjustments i.e. xrot,yrot, etc.
        """
        from scipy.optimize import leastsq,fsolve
        print '\n Optimize Single Cap Gauge Change'
        trylist = [0]
        def single(perts,num,amount):
            """
            Optimization func
            leg number 1..6
            amount to change
            """
            ind = 0
            self.set_pert_adjusts([perts[0],perts[1],perts[2],
                                     perts[3],perts[4],perts[5]])
            self.solve()
            back = self.cap_changes.copy()
            back[num-1] += amount
            trylist[0] += 1
            #print '\nback',back
            return back
            
        vstart = [0.]*6
        # not sure which is better for this leastsq or fsolve
##        vsolved = leastsq(single, vstart, args=(num,amount), Dfun=None, full_output=0,
##                          col_deriv=0, ftol=1.49012e-08, xtol=1.49012e-08,
##                          gtol=0.0, maxfev=0, epsfcn=1e-8, factor=100,
##                          diag=None)[0]
        vsolved = fsolve(single, vstart, args=(num,amount), fprime=None, full_output=0,
                       col_deriv=0, xtol=1.49012e-08, maxfev=0, band=None,
                       epsfcn=1e-8, factor=100, diag=None)
        back = single(vsolved,num,amount)
        print 'Leg and Cap Gauge Number: %s' % num
        print 'Cap Gauge Change: %s' % amount
        numpy.set_printoptions(precision=7,suppress=True)
        print 'leg_changes',self.leg_changes
        print 'cap_changes',self.cap_changes
        for i,v in enumerate(self.hexs.perts):
            print '%s %+.6f' % (v,vsolved[i])
        print 'number of Optimization iterations',trylist[0]
        self.pert_adjusts = None
        self.cap_changes = None 
        return vsolved

    def single_leg(self,num,amount=.1):
        """
        This is an experimental function to see if the effect of single
        leg length changes can be isolated and the resulting change
        to xtrans ytrans ztrans xrot yrot zrot found. This would allow making
        a normal sensalign.py sensitivity dict and matrix. Presumably this could
        also be done my simply creating an A matrix based on leg length and
        inverting it.
        Input:
        num<int> leg number 1 - 6
        amount<float> change in mm
        Output:
        pert_adjusts<arr> M1 adjustments i.e. xrot,yrot, etc.
        """
        from scipy.optimize import leastsq,fsolve
        print '\n Optimize Single Leg lenght Change'
        trylist = [0]
        def single(perts,num,amount):
            """
            Optimization func
            leg number 1..6
            amount to change
            """
            ind = 0
            self.set_pert_adjusts([perts[0],perts[1],perts[2],
                                     perts[3],perts[4],perts[5]])
            self.solve()
            back = self.leg_changes.copy()
            back[num-1] += amount
            trylist[0] += 1
            #print '\nback',back
            return back
            
        vstart = [0.]*6
        # not sure which is better for this leastsq or fsolve
##        vsolved = leastsq(single, vstart, args=(num,amount), Dfun=None, full_output=0,
##                          col_deriv=0, ftol=1.49012e-08, xtol=1.49012e-08,
##                          gtol=0.0, maxfev=0, epsfcn=1e-8, factor=100,
##                          diag=None)[0]
        vsolved = fsolve(single, vstart, args=(num,amount), fprime=None, full_output=0,
                       col_deriv=0, xtol=1.49012e-08, maxfev=0, band=None,
                       epsfcn=1e-8, factor=100, diag=None)
        back = single(vsolved,num,amount)
        print 'Leg and Cap Gauge Number: %s' % num
        print 'Leg Length Change: %s' % amount
        numpy.set_printoptions(precision=7,suppress=True)
        print 'leg_changes',self.leg_changes
        print 'cap_changes',self.cap_changes
        for i,v in enumerate(self.hexs.perts):
            print '%s %+.6f' % (v,vsolved[i])
        print 'number of Optimization iterations',trylist[0]
        self.pert_adjusts = None
        self.cap_changes = None
        return vsolved


            
    def _get_residiual(self,A,p,z):
        """
        Becouse it is a square matrix residiual should alway be 0
        """
        newz = numpy.dot(A,p)
        res = newz - z
        return res
    
    def set_pert_adjusts(self,pert_adjusts):
        """
        xrot,yrot,zrot,xtrans,ytrans,ztrans
        Sets self.pert_adjusts
        Input:
        pert_adjusts<list> [xrot,yrot,zrot,xtrans,ytrans,ztrans]
                            amount to adjust each pertabation of m1 mirror
                            xrot,yrot,zrot,xtrans,ytrans,ztrans,
                            rot in radians, trans in mm
        Note: zrot should normaly be None in first pass. If zrot is None
        solve() method will optimize for best zrot to minimize max length change
        in legs
        """
        self.pert_adjusts = pert_adjusts
        self.cap_changes = None #set to None becouse new solve needed
        self.leg_changes = None

    def disp_solve2(self):
        """
        Display solve amounts
        Returns Report 
        """
        rpt = Report('\n*** Report Calculated Required Cap Gauge Measured Changes ***')
        rpt += '\n      Desired M1 Mirror Adjustments:'
        for pert,adjust,units in zip(self.hexs.perts,self.pert_adjusts,
                                     self.hexs.pertunits):
            pert = pert.rjust(6)
            rpt += '        %s %+.6f %s' % (pert,adjust,units)
        rpt += '\n Required Cap Gauge Measured Change:'
        for i,v in enumerate(self.cap_changes):
            rpt += '    CapGauge_%s %+.6f mm' % (i+1,v)

        rpt += '\n Required Leg Length Change:'
        for i,v in enumerate(self.leg_changes):
            rpt += '         Leg_%s %+.6f mm' % (i+1,v)
        print rpt
        return rpt

    def disp_solve(self):
        """
        Display solve amounts
        Returns Report 
        """
        rpt = Report('\n*** Report Calculated Required Cap Gauge Measured Changes ***')
        rpt += '      Desired M1 Mirror Adjustments:'
        for pert,adjust,units in zip(self.hexs.perts,self.pert_adjusts,
                                     self.hexs.pertunits):
            pert = pert.rjust(6)
            rpt += '        %s %+.6f %s' % (pert,adjust,units)
        rpt += '\n Required Changes:'
        rpt += '     dLeg Length(mm)   dCapGauge(mm)'
        for i in range(len(self.cap_changes)):
            rpt += '    Leg_%s  %+.6f    %+.6f' % (i+1,self.leg_changes[i],self.cap_changes[i])
        print rpt
        return rpt

    def save_capGauge_readings(self,cap_readings,filenameroot='hex_cg_readings',
                               ext='txt',mode='append',comment=''):
        """
        Saves file in Records :  \\usrics02\omase_tl2\Records\met5\pob\rgen
        Used Attb:
        self.hexopod_id<str> Id of hexopod
        
        Input:
        cap_readings=<list> of capGauge readings units are microns
        filenameroot<str>  filename will be '%s_%s.%s' % (filenameroot,hexopod_id,ext)
        ext=<str> filenane ext
        mode='append' or 'new'  'a' for append to file 'w' for delete and start new

        file format:
        datetime.datetime, numorder, gc1 , gc2 , cg3 ,cg4 , cg5 ,cg6
            Example:
        datetime.datetime, 1, gc1 , gc2 , cg3 ,cg4 , cg5 ,cg6
        datetime.datetime, 2, gc1 , gc2 , cg3 ,cg4 , cg5 ,cg6
        datetime.datetime, 3, gc1 , gc2 , cg3 ,cg4 , cg5 ,cg6
        
        numorder is entry number start with 1
        gc1..6 are floats from cap gauge readings
        """
        import datetime
        import os
        comment = comment.replace(',','_')
        now = datetime.datetime.now()
        path = os.path.join(omsys.compinfo['recordspath'],'met5\\pob\\rgen',filenameroot)
        filename = '%s_%s.%s' % (path,self.hexopod_id,ext)
        #filename = '%s_%s.%s' % (filenameroot,self.hexopod_id,ext)
        if mode == 'new':
            if os.path.isfile(filename):
                os.remove(filename)
            k = 0
            f1 = open(filename,mode='w')#creates file for append latter
            f1.close()
        else:
            f1 = open(filename,mode='r')
            k = 0
            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line:
                    k += 1
            f1.close()
        c = cap_readings
        f1 = open(filename,mode='a')
        f1.write('%sdt, %i, %.7f, %.7f, %.7f, %.7f, %.7f, %.7f , %s \n' % \
                 (repr(now),k+1,  c[0], c[1], c[2], c[3], c[4], c[5],comment))
        f1.close()
        
    def read_capGauge_file(self,num=1,filenameroot='hex_cg_readings',ext='txt'):
        """
        datetime,[cg1,cg2,cg3,cg4,cg5,cg6],comment = read_capGauge_file()
        reads file in Records :  \\usrics02\omase_tl2\Records\met5\pob\rgen
        Reads file with cap cage readings
        Input:
        num=<int> entery number in file normaly would be 1
        filenameroot<str>  filename will be '%s_%s.%s' % (filenameroot,hexopod_id,ext)
        ext=<str> filenane ext
        Output:
        datetime object
        list of floats units are microns
        """
        import datetime
        import os
        path = os.path.join(omsys.compinfo['recordspath'],'met5\\pob\\rgen',filenameroot)
        filename = '%s_%s.%s' % (path,self.hexopod_id,ext)
        f1 = open(filename,mode='r')
        lines = f1.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line:
                sline = line.split('dt,')
                dt = eval(sline[0])
                rline =  sline[1].split(',')
                linenum = int(rline[0])
                if int(num) == linenum:
                    break
        f1.close()
        return dt,[float(rline[1]),float(rline[2]),float(rline[3]),
                   float(rline[4]),float(rline[5]),float(rline[6])],rline[7]

    def read_capGague_file_positions(self, filenameroot='hex_cg_readings', ext='txt'):
        """
        @Purpose:
            read the capgauge position files and return a map of all the positions.
        @Inputs:
            (str) filenameroot = file nane to parse
            (str) ext = file extension
        @Outpus:
            (dict) {1: [(list) list_cap_positions, (datetime) dateObj, (str) comments], ...}
        """
        retval = {}

        import datetime
        import os
        path = os.path.join(omsys.compinfo['recordspath'],'met5\\pob\\rgen',filenameroot)
        filename = '%s_%s.%s' % (path,self.hexopod_id,ext)
        f1 = open(filename,mode='r')
        for line in f1:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line:
                sline = line.split('dt,')
                dt = eval(sline[0])
                rline =  sline[1].split(',')
                linenum = int(rline.pop(0))
                comments = rline.pop(-1)
                cap_pos = [float(ele) for ele in rline]
                retval[linenum] = [cap_pos, dt, comments]
        f1.close()
        return retval
    
    def move(self,cap_changes=None):
        """
        I don't think this method will be used
        
        Adjusts motors on legs to change readings on cap gauges
        cap_changes<list> or None values to change cap gauge readings
                            if None will use self.cap_changes
        """
        if cap_changes is None:
            cap_changes = self.cap_changes
        #move leg motors with Charlies module code
        print ' ***No moves yet***'
        self.pert_adjusts = None
        self.cap_changes = None 

if __name__ == '__main__':
    #hexs = Hexsens()
    hexa = Hexalign(hexopod_id='1')

    for i in range(1,7):
        hexa.single_leg(num=i,amount=.1)

    for i in range(1,7):
        hexa.single_cap(num=i,amount=.1)

    '''
    hexa.set_pert_adjusts([.0001,.0007,.001,-.015,.03,.02])
    hexa.solve()
    hexa.disp_solve()


    hexa.set_pert_adjusts([.0001,.0007,numpy.NaN,-.015,.03,.02])
    hexa.solve()
    hexa.disp_solve()

    hexa.set_pert_adjusts([0,0,0,0,0,.1])
    hexa.solve()
    hexa.disp_solve()

    hexa.set_pert_adjusts([0,0,0,.1,0,0])
    hexa.solve()
    hexa.disp_solve()
    
    hexa.set_pert_adjusts([0,0,0,0,.1,0])
    hexa.solve()
    hexa.disp_solve()

    hexa.set_pert_adjusts([0,0,.001,0,0,0])
    hexa.solve()
    hexa.disp_solve()

    hexa.set_pert_adjusts([0.001,0,0,0,0,0])
    hexa.solve()
    hexa.disp_solve()

    hexa.set_pert_adjusts([0,0.001,0,0,0,0])
    hexa.solve()
    hexa.disp_solve()
    '''
