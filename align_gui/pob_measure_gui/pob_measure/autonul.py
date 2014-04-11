import sys
sys.path.append("C:/motion")

import pobtest
import os
import mrc3_client
import socket

allaxislist = pobtest.axislist   #Contains all motors.  Should not be used for any UI windows.
allaxisnames = {}
for i in allaxislist:
    allaxisnames[i.label] = i


class AutoNulException(Exception):
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg
    
    def __str__(self):
        return "ERROR: AutoNulException; expression = %s; %s\n" % (repr(self.expr), self.msg)

#-------------------------------------------------------------------
def ErrorBox(parent, message):
    """A standardized error message box"""
    """
    erdlg = wx.MessageDialog(parent, message,'Error',wx.CANCEL | wx.ICON_ERROR)
    erdlg.ShowModal()
    erdlg.Destroy()
    """
    raise AutoNulException("AutoNul Exception", message)

#-------------------------------------------------------------------
def tip_tip_z_to_3z(group, xtilt = 0, ytilt = 0, ztran = 0):
    """Converts xtilt, ytilt, and ztran values into 3 z axis movements"""
    movements = [[0.0,0.0,0.0],['','','']]
    a = allaxisnames[group + ' X Tilt'].move(xtilt, check = True)
    b = allaxisnames[group + ' Y Tilt'].move(ytilt, check = True)

    #Note a,b need to be processed before z even if a,b = 0 to add motor names.
    for i in [a,b]:
        for j in range(len(i[0])):
            movements[0][j] = movements[0][j] + i[0][j]
            movements[1][j] = i[1][j]
    if float(ztran) != 0.0:
        c = allaxisnames[group + ' Z Axis'].move(ztran, check = True)   #applies Z flip correctly
        for i in range(len(movements[0])):
            movements[0][i] = movements[0][i] + c
    return movements
#-----------------------------------
def simple_move_motor(motor, amount, absolute = False):
    """A simpler movement function for when the program knows where to move.
    Units must be in motor default units.  Implemented for offset motion."""
    amount = float(amount)
    if absolute:
        motor.move_abs(amount)
    else:
        motor.move(amount)


#-----------------------------------
# A dictionary with stored motion parameters.
autonulchoices = {'TransSph Trans' : ['TS',0.0,0.0,0.0,1.03334E-5,-1.02703E-5 ], #SH flipped signs of coeffs (not tested for POB)
                  'RetroSph Trans' : ['Ret',0.0,0.0,0.0,1.9687E-6,-2.01222E-6 ],
                  'TransSph Trans w Power' : ['TS',0.0,0.0,-3.9364437E-4,1.03334E-5,-1.02703E-5],
                  'RetroSph Trans w Power' : ['Ret',0.0,0.0,1.4954E-5,1.9687E-6,-2.01222E-6 ]}
#-----------------------------------
                                   
def moveautonul(parameters):
    """parameters -- a list of 6 run parameters that control the autonul responce
                     [motion group, X Tilt, Y Tilt, Z Translation, X Translation, Y Translation]
    """
    

    group,sensz2,sensz3,sensz4,senTz2,senTz3 = parameters
    
    
    #Check that group motors are homed (tip / tilt use all 3 axis so only 1 needs to be checked.)
    #Or if only 1 axis exits it will be the Z Axis
    if sensz2 or sensz3 or sensz4:
        if hasattr(allaxisnames[group + ' Z Axis'], 'ishomed') and not allaxisnames[group + ' Z Axis'].ishomed:
            ErrorBox(None, 'All Z axes must be homed to use AutoNull')
            return False

    #Check that Xtrans is homed if it is used
    if senTz2 and hasattr(allaxisnames[group + ' X Axis'], 'ishomed') and not allaxisnames[group + ' X Axis'].ishomed:
        ErrorBox(None, 'All Z axes must be homed to use AutoNull')
        return False

    #Check that Ytrans is homed if it is used
    if senTz3 and hasattr(allaxisnames[group + ' Y Axis'], 'ishomed') and not allaxisnames[group + ' Y Axis'].ishomed:
        ErrorBox(None, 'All Z axes must be homed to use AutoNull')
        return False

    #access metropro computer, and execute predefined script.
    hostSH='1PBZ3V1'  #SH added 2/24/14 for robustness
    ip = socket.gethostbyname(hostSH) #SH added 2/24/14 nominal '172.18.106.130' ip of the testing computer (1PBZ3V1)
    script = 'EPOgetzrn.scr'
    try:
        (out_buf,err_msg,err_status)=mrc3_client.run_script(script, ip)
        (z2, z3, z4) = out_buf.rstrip(os.linesep).split()

        #Calculate combind Z motor movements and execute moves.  Tip args are: group, xtilt, ytilt, z trans
        if sensz2 or sensz3 or sensz4:
            if allaxisnames.has_key(group +' X Tilt'):  #has 3 Z motors
                movements = tip_tip_z_to_3z(group,float(z2)*sensz2,float(z3)*sensz3,float(z4)*sensz4)
            else:   # has 1 Z motor
                movements = [[float(z4)*sensz4],[allaxisnames[group +' Z Axis']]]
        else:
            movements = [[],[]] #SH BillR added to avoid empty list

        for j in range(len(movements[0])):
            if movements[0][j] != 0.0 and movements[1][j] != '':
                simple_move_motor(movements[1][j], movements[0][j])

        #move X translation
        if senTz2:
            simple_move_motor(allaxisnames[group +' X Axis'], senTz2*float(z2)) #SH BillR float(z2) and allaxisnames[group +' X Axis']
        #move Y translation
        if senTz3:
            simple_move_motor(allaxisnames[group +' Y Axis'], senTz3*float(z3)) #SH BillR float(z3) and allaxisnames[group +' X Axis']
        return True
        
    except RuntimeError, message:
        ErrorBox(None, 'Could not communicate with MetroPro\n'+str(message))
        return False
    except ValueError:
        ErrorBox(None, 'ValueError from metroscript return values.')
        return False

                                  