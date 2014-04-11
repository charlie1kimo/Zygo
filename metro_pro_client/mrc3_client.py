"""
   mrc3_client.py - A ctypes non object-oriented Python wrapper 
                    for mrc3_client.dll.

   Author: Jay Thomas <jthomas@zygo.com>
           Charlie Chen <cchen@zygo.com>
   
   Copyright (c) 2012, Zygo Corporation
   All rights reserved.
"""

__docformat__ = 'restructuredtext'
__version__   = '$Id$'

import os
from ctypes import *
import numpy as np

class MetroProClientException(Exception):
  """
  @Purpose:
    This is a custom exception class for MetroProClient.
  """
  def __init__(self, expr, msg):
    self.expr = expr
    self.msg = msg
  
  def __str__(self):
    return "ERROR: MetroProClient; expression = %s; %s\n" % (repr(self.expr), self.msg)


c_int_p = POINTER(c_int)
c_int8_p = POINTER(c_int8)
c_ubyte_p = POINTER(c_ubyte)
c_float_p = POINTER(c_float)
c_double_p = POINTER(c_double)
c_void_p_p = POINTER(c_void_p)
c_short_p = POINTER(c_short)


# Assumes associated DLL is in same directory as this module. Note
# that mrc2_client.dll and mrc4_client.dll are also required to be
# present in the same directory. The stdcall calling convention is
# used.
cwd = os.path.dirname(os.path.abspath(__file__))
print cwd
_mrc3dll = windll.LoadLibrary("mrc3_client.dll")


# prototypes for the DLL functions
mrc3OpenLogFile = _mrc3dll.mrc3_open_log_file
mrc3OpenLogFile.restype = c_int 
mrc3OpenLogFile.argtypes = [c_char_p]

mrc3CloseLogFile = _mrc3dll.mrc3_close_log_file
mrc3CloseLogFile.restype = None 
mrc3CloseLogFile.argtypes = []

mrc3LogMessage = _mrc3dll.mrc3_log_message
mrc3LogMessage.restype = None 
mrc3LogMessage.argtypes = [c_char_p]

mrc3NewInterface = _mrc3dll.mrc3_new_interface
mrc3NewInterface.restype  = c_int 
mrc3NewInterface.argtypes = [c_int_p]

mrc3FreeInterface = _mrc3dll.mrc3_free_interface
mrc3FreeInterface.restype  = c_int 
mrc3FreeInterface.argtypes = [c_int_p]

mrc3SetInterfaceParams = _mrc3dll.mrc3_set_interface_params
mrc3SetInterfaceParams.restype = c_int 
mrc3SetInterfaceParams.argtypes = [c_int, c_char_p, c_char_p, c_char_p]

mrc3PingServer = _mrc3dll.mrc3_ping_server
mrc3PingServer.restype = c_int 
mrc3PingServer.argtypes = [c_int]

mrc3RequestControl = _mrc3dll.mrc3_request_control
mrc3RequestControl.restype = c_int 
mrc3RequestControl.argtypes = [c_int]

mrc3ReleaseControl = _mrc3dll.mrc3_release_control
mrc3ReleaseControl.restype = c_int 
mrc3ReleaseControl.argtypes = [c_int]

mrc3GetServerState = _mrc3dll.mrc3_get_server_state
mrc3GetServerState.restype = c_int 
mrc3GetServerState.argtypes = [c_int,c_int_p]

mrc3SetScriptFilename = _mrc3dll.mrc3_set_script_filename
mrc3SetScriptFilename.restype = c_int
mrc3SetScriptFilename.argtypes = [c_int, c_char_p]

mrc3SetScriptText = _mrc3dll.mrc3_set_script_text
mrc3SetScriptText.restype = c_int 
mrc3SetScriptText.argtypes = [c_int, c_char_p]

mrc3SetScriptContext = _mrc3dll.mrc3_set_script_context
mrc3SetScriptContext.restype = c_int 
mrc3SetScriptContext.argtypes = [c_int, c_int]

# c_bool not in omase ctypes
mrc3RunScript = _mrc3dll.mrc3_run_script
mrc3RunScript.restype = c_int 
mrc3RunScript.argtypes = [c_int, c_int]

mrc3StartScript = _mrc3dll.mrc3_start_script
mrc3StartScript.restype = c_int 
mrc3StartScript.argtypes = [c_int]

mrc3GetScriptRunning = _mrc3dll.mrc3_get_script_running
mrc3GetScriptRunning.restype = c_int 
mrc3GetScriptRunning.argtypes = [c_int, c_int_p]

mrc3WaitIdle = _mrc3dll.mrc3_wait_idle
mrc3WaitIdle.restype = c_int 
mrc3WaitIdle.argtypes = [c_int, c_int]

mrc3GetScriptError = _mrc3dll.mrc3_get_script_error
mrc3GetScriptError.restype = c_int 
mrc3GetScriptError.argtypes = [c_int, c_int_p]

mrc3GetScriptOutput = _mrc3dll.mrc3_get_script_output
mrc3GetScriptOutput.restype = c_int
mrc3GetScriptOutput.argtypes = [c_int, c_char_p, c_int]

mrc3GetScriptStopStrVal = _mrc3dll.mrc3_get_script_stop_str_val
mrc3GetScriptStopStrVal.restype = c_int
mrc3GetScriptStopStrVal.argtypes = [c_int, c_char_p, c_int]

mrc3GetScriptStopNumVal = _mrc3dll.mrc3_get_script_stop_num_val
mrc3GetScriptStopNumVal.restype = c_int
mrc3GetScriptStopNumVal.argtypes = [c_int, c_double_p]

mrc3GetInterfaceGuid = _mrc3dll.mrc3_get_interface_guid
mrc3GetInterfaceGuid.restype = None
mrc3GetInterfaceGuid.argtypes = [c_char_p, c_int]

mrc3GetErrorMessage = _mrc3dll.mrc3_get_error_message
mrc3GetErrorMessage.restype = None 
mrc3GetErrorMessage.argtypes = [c_int, c_char_p, c_int]

# callbacks prototype example code
"""
def _mrc3_status_callback_func_t(callback_id, status):
    pass

_mrc3_status_callback_func_prototype = CFUNCTYPE(c_int, c_int)
mrc3StatusCallbackFuncT = _mrc_status_callback_func_prototype(_mrc3_status_callback_func_t)
"""

# callbacks
mrc3SetStatusCallbackFunction = _mrc3dll.mrc3_set_status_callback_function
mrc3SetStatusCallbackFunction.restype = c_int

mrc3SetStatusCallbackId = _mrc3dll.mrc3_set_status_callback_id
mrc3SetStatusCallbackId.restype = c_int
mrc3SetStatusCallbackId.argtypes = [c_int, c_int]

mrc3SetStatusCallbackMask = _mrc3dll.mrc3_set_status_callback_mask
mrc3SetStatusCallbackMask.restype = c_int
mrc3SetStatusCallbackMask.argtypes = [c_int, c_int]


# Invalid handle value.
MRC_INVALID_HANDLE = -1

# Size of the characters arrays that receive script output returned 
# by MetroPro to a client. 
MRC_SCRIPT_OUTPUT_BUFSIZ = 512


# SERVER STATE CODES

# Integer code for the UNKNOWN server state.
MRC_SERVER_STATE_UNKNOWN = -1
 
# Integer code for the STOPPED server state. 
MRC_SERVER_STATE_STOPPED = 0
 
# Integer code for the IDLE server state. 
MRC_SERVER_STATE_IDLE = 1

# Integer code for the ACTIVE server state. 
MRC_SERVER_STATE_ACTIVE = 2


# SCRIPT CONTEXT CODES

# Integer code to specify that a script is to run in the context of the 
# MetroPro desktop. 
MRC_SCRIPT_CONTEXT_DESKTOP = 0

# Integer code to specify that a script is to run in the context of the 
# MetroPro front-most open app.
MRC_SCRIPT_CONTEXT_FRONTMOST_APP = 1
 

# ERROR CODES

# No error occurred.
MRC_ERR_NONE = 0

# Error return code base value. 
MRC_ERR_BASE = 0x20000000

# A run-script command failed. 
MRC_ERR_RUN_SCRIPT_FAILED = 0x20000000

# MetroPro is busy executing a remote command. 
MRC_ERR_SERVER_BUSY = 0x20000001

# MetroPro could not accept a command within a time limit. 
MRC_ERR_COMMAND_TIMEOUT = 0x20000002

# MetroPro could not transition from the MRC_SERVER_STATE_IDLE state to the 
# MRC_SERVER_STATE_ACTIVE state. 
MRC_ERR_REQUEST_CONTROL_FAILED = 0x20000003

# MetroPro could not transition from the MRC_SERVER_STATE_ACTIVE state to 
# the MRC_SERVER_STATE_IDLE state.
MRC_ERR_RELEASE_CONTROL_FAILED = 0x20000004

# MetroPro could not run a script because there is no open app.  
MRC_ERR_SCRIPT_CONTEXT_NO_APP = 0x20000005

# A passed parameter value is invalid. 
MRC_ERR_INVALID_PARAM = 0x20000006

# MetroPro could not write a required temporary file.
MRC_ERR_CANT_WRITE_TEMP_FILE = 0x20000007

# The passed handle value is invalid. 
MRC_ERR_INVALID_HANDLE = 0x20000008
 
# The client RPC binding could not be created.  
MRC_ERR_RPC_BINDING_CREATE = 0x20000009

# The client RPC binding could not be freed. 
MRC_ERR_RPC_BINDING_FREE = 0x2000000A

# A memory allocation failed. 
MRC_ERR_NO_MEM = 0x2000000B

# The client interface is busy. 
MRC_ERR_CLIENT_INTERFACE_BUSY = 0x2000000C

# The client interface is already open.
MRC_ERR_CLIENT_INTERFACE_OPEN = 0x2000000D
 
# The client interface is not open. 
MRC_ERR_CLIENT_INTERFACE_NOT_OPEN = 0x2000000E
 
# No script filename or text was specified.  
MRC_ERR_NO_SCRIPT_FILENAME_OR_TEXT = 0x2000000F

# A log file could not be created. 
MRC_ERR_CANT_CREATE_LOG_FILE = 0x20000010

# Timeout waiting for the interface to become idle. 
MRC_ERR_TIMEOUT_WAITING_FOR_IDLE = 0x20000011

# Timeout waiting for script done.
MRC_ERR_TIMEOUT_WAITING_FOR_SCRIPT = 0x20000012

# STATUS CALLBACKS

# Bitmask value to enable a callback when acquisition begins.
MRC_ENABLE_STATUS_CALLBACK_BEGIN_ACQUIRE = 0x0001

# Bitmask value to enable a callback when acquisition ends.
MRC_ENABLE_STATUS_CALLBACK_END_ACQUIRE = 0x0002

# Bitmask value to enable a callback when FDA begins.
MRC_ENABLE_STATUS_CALLBACK_BEGIN_FDA = 0x0004

# Bitmask value to enable a callback when FDA ends.
MRC_ENABLE_STATUS_CALLBACK_END_FDA = 0x0008

# Bitmask value to enable a callback by MetroScript "mrcstatus."
MRC_ENABLE_STATUS_CALLBACK_SCRIPT = 0x0010

# Bitmask value to enable a callback when the script is done executing.
MRC_ENABLE_STATUS_CALLBACK_END_SCRIPT = 0x0020

# Bitmask value to enable a callback containing the scan offset.
MRC_ENABLE_STATUS_CALLBACK_SCAN_OFFSET = 0x0040

# Bitmask value to enable all callbacks.
MRC_ENABLE_STATUS_CALLBACK_ALL = 0xFFFF

# CALLBACKS

# Begin of acquisition.
MRC_CALLBACK_STATUS_BEGIN_ACQUIRE = 1

# End of acquisition.
MRC_CALLBACK_STATUS_END_ACQUIRE = 2

# Beginning of FDA
MRC_CALLBACK_STATUS_BEGIN_FDA = 3

# End of FDA.
MRC_CALLBACK_STATUS_END_FDA = 4

# End of script execution.
MRC_CALLBACK_STATUS_END_SCRIPT = 5


# Extended error messages.
mrc3_error_msgs = {MRC_ERR_NONE:'No error occurred.',
                   MRC_ERR_RUN_SCRIPT_FAILED:'A run-script command failed.', 
                   MRC_ERR_SERVER_BUSY:'MetroPro is busy executing a remote'
                   'command.', 
                   MRC_ERR_COMMAND_TIMEOUT:'MetroPro could not accept a '
                   'command within a time limit.',
                   MRC_ERR_REQUEST_CONTROL_FAILED:'MetroPro could not '
                   'transition from the MRC_SERVER_STATE_IDLE state to '
                   'the MRC_SERVER_STATE_ACTIVE state.',
                   MRC_ERR_RELEASE_CONTROL_FAILED:'MetroPro could not '
                   'transition from the MRC_SERVER_STATE_ACTIVE state to ' 
                   'the MRC_SERVER_STATE_IDLE state.',
                   MRC_ERR_SCRIPT_CONTEXT_NO_APP:'MetroPro could not run '
                   'a script because there is no open app.',
                   MRC_ERR_INVALID_PARAM:'A passed parameter value is invalid.',
                   MRC_ERR_CANT_WRITE_TEMP_FILE:'MetroPro could not write a '
                   'required temporary file.',
                   MRC_ERR_INVALID_HANDLE:'The passed handle value is invalid.',
                   MRC_ERR_RPC_BINDING_CREATE :'The client RPC binding could '
                   'not be created.',
                   MRC_ERR_RPC_BINDING_FREE:'The client RPC binding could '
                   'not be freed.',
                   MRC_ERR_NO_MEM:'A memory allocation failed.',
                   MRC_ERR_CLIENT_INTERFACE_BUSY:'The client interface is busy.',
                   MRC_ERR_CLIENT_INTERFACE_OPEN:'The client interface is '
                   'already open.',
                   MRC_ERR_CLIENT_INTERFACE_NOT_OPEN:'The client interface is '
                   'not open.',
                   MRC_ERR_NO_SCRIPT_FILENAME_OR_TEXT:'No script filename or '
                   'text was specified.',
                   MRC_ERR_CANT_CREATE_LOG_FILE:'A log file could not be created.',
                   MRC_ERR_TIMEOUT_WAITING_FOR_IDLE:'Timeout waiting for the '
                   'interface to become idle.',
                   MRC_ERR_TIMEOUT_WAITING_FOR_SCRIPT:'Timeout waiting for '
                   'script done.'
                  }

def mrc3_open_log_file(pathname):
    """ 
        This function opens a log file to receive diagnostic 
        messages. Overwrites any existing file of the same name.
        Only a single log file is supported.

        Parameters:
            pathname    Input: specifies the file path.
            
        Returns:
            None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3OpenLogFile(pathname)
    if code != 0:
        raise RuntimeError('mrc3_open_log_file: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_close_log_file():
    """ 
        This function closes the diagnostic log file that was opened by 
        mrc3_open_log_file().

        Parameters:
            None.
            
        Returns:
            None.
    """
    
    mrc3CloseLogFile()
    
    
def mrc3_log_message(msg):
    """ 
        This function writes a message to a diagnostic log file that 
        was opened by mrc3_open_log_file(). This function does nothing 
        if there is no open log file.

        Parameters:
            msg    Input: String to write to log file.
            
        Returns:
            None.
    """
    
    mrc3LogMessage(msg)    
    

def mrc3_new_interface():
    """
       This function creates a new interface for communication with a server.
       The return value is a handle that is a required input parameter to most 
       of the functions in mrc3_client. Therefore this is normally the first 
       function a client program should call. Note that this function does 
       not perform any communication with a server. Before the interface 
       can be used to communicate with a server, function 
       mrc3_open_interface() must be called.
       
       This function fails if:
           Memory could not be allocated.    
       
    
       Parameters: None
    
       Returns:
           If successful, returns a handle. Otherwise raises a RuntimeError
           exception..
           
       Remarks:
           This function allocates memory associated with the handle. When 
           the interface is no longer needed, the client program should call 
           function mrc3_free_interface().
           
   """
    
    handle = c_int()
    code = mrc3NewInterface(byref(handle))
    if code != 0:
        raise RuntimeError('mrc3_new_interface: ' + 
                           mrc3_get_error_message(code))
    
    return handle


def mrc3_free_interface(handle):
    """
       This function frees an interface that was created by function 
       mrc3_new_interface(). It closes the interface if it was open and 
       frees associated memory. The handle is set to MRC_INVALID_HANDLE. 
       
       This function fails if: 
           The handle is invalid.    
       
       Parameters:
          handle  Input/Output: handle obtained from function mrc3_new_interface().
          
       Returns:
           None. Upon failure a RuntimeError exception is raised.

       Remarks:
           When an interface is no longer needed, the client program should 
           call this function to free associated memory. 
    """
    
    code = mrc3FreeInterface(byref(handle))
    if code != 0:
        raise RuntimeError('mrc3_free_interface: ' + 
                           mrc3_get_error_message(code))
        
    
def mrc3_set_interface_params(handle, protocol_sequence, 
                              network_address, end_point):
    """
       This function opens an interface for communication with a server.
       This function must be called before an interface can be used to 
       communicate with a server. Note that this function does not 
       perform any communication with the server.  
       
       This function fails if: 
           The handle is invalid.
           The interface parameters are invalid or inconsistent.    
    
       Parameters:
           handle             Input: handle obtained from function 
                                     mrc3_new_interface().
           protocol_sequence  Input: string specifying a communication protocol, 
                                     typically "ncalrpc" or "ncacn_ip_tcp". 
                                     This parameter cannot be an empty string.
           network_address    Input  string identifying the server computer. 
                                     Pass an empty string or 'null' when using the 
                                     ncalrpc protocol. Otherwise, specify the host 
                                     name or IP address as a string.
           end_point          Input: string specifying the server end point. 
                                     This parameter cannot be an empty string. 
                                     Use "localhost" with the ncalrpc protocol. 
                                     Specify a port number (e.g. "5000") when 
                                     using the ncacn_ip_tcp protocol.
                                     
           Returns:
               None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3SetInterfaceParams(handle.value, protocol_sequence,
                                  network_address, end_point)
    if code != 0:
        raise RuntimeError('mrc3_set_interface_params: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_ping_server(handle):
    """
        This function performs a do-nothing call to a server. An error is 
        generated if the server is not responsive. This function is useful to 
        test whether the server is available.
        
        This function fails if:
            The handle is invalid.
            The server MetroPro is not available.
            There is a communication error.    

       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           Zero if successful. Upon failure a RuntimeError exception is raised.
    """           
    
    code = mrc3PingServer(handle.value)
    if code != 0:
        raise RuntimeError('mrc3_ping_server: ' + 
                           mrc3_get_error_message(code))
    
    return code
    
    
def mrc3_request_control(handle):
    """
       Request control of a server.
       
       This function requests that the server enter the MRC_SERVER_STATE_ACTIVE
       state, which is the nominal "remote controlled" state. In this state, 
       MetroPro ignores operator input (except for the Esc key). An error is 
       generated if the server is not available or if it cannot transition to 
       MRC_SERVER_STATE_ACTIVE. No error is generated if the server is already 
       in the MRC_SERVER_STATE_ACTIVE state.
       
       This function fails if:
           The handle is invalid.
           The client interface is not idle.
           The server MetroPro is not available.
           There is a communication error.
           MetroPro cannot transition to the active state.
       
       Parameters:
           handle   Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3RequestControl(handle.value)
    if code != 0:
        raise RuntimeError('mrc3_request_control: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_release_control(handle):
    """
       This function requests that the server return to the 
       MRC_SERVER_STATE_IDLE state. In this state, MetroPro responds 
       normally to the operator while continuing to listen for remote 
       commands. An error is generated if the server is not available 
       or if it cannot transition to MRC_SERVER_STATE_IDLE. No error 
       is generated if the server is already in the MRC_SERVER_STATE_IDLE 
       state.
       
              
       This function fails if:
           The handle is invalid.
           The client interface is not idle.
           The server MetroPro is not available. 
           There is a communication error.
       
       Parameters:
           handle    Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3ReleaseControl(handle.value)
    if code != 0:
        raise RuntimeError('mrc3_release_control: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_get_server_state(handle):
    """
       This function gets the current state of a server, either 
       MRC_SERVER_STATE_IDLE or MRC_SERVER_STATE_ACTIVE. An error is 
       generated if the server is not available.
       
       This function fails if:
           The handle is invalid.
           The client interface is not idle.
           The server MetroPro is not available.
           There is a communication error.
           
       Parameters:
           handle   Input: handle obtained from function mrc3_new_interface().

       Returns:
           If successful an integer state code. Upon failure a RuntimeError 
           exception is raised.
    """
    
    result = c_int()
    code = mrc3GetServerState(handle.value, byref(result))
    if code != 0:
        raise RuntimeError('mrc3_get_server_state: ' + 
                           mrc3_get_error_message(code))
    
    return result.value
    
    
def mrc3_set_script_filename(handle, filename):
    """
       This function sets the name of a MetroScript file that can be
       subsequently run by the server MetroPro.  Note that the file
       in question must be on the MetroPro server computer, not the
       client computer.
       
       Either this function or mrc3_set_script_text() must be called 
       before calling mrc3_run_script() or mrc3_start_script().
       
       This function fails if:
           The handle is invalid.
           The client interface is not idle.
    
       Parameters:
           handle    Input: handle obtained from function mrc3_new_interface().
           filename  Input: Name of a MetroScript file that exists on the 
                            server computer. This parameter may be "null" or 
                            an empty string.
                            
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3SetScriptFilename(handle.value, filename)
    if code != 0:
        raise RuntimeError('mrc3_set_script_filename: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_set_script_text(handle, text):
    """
       This function sets MetroScript text that can be subsequently 
       run by the server MetroPro.
       
       Either this function or mrc3_set_script_filename() must be 
       called before calling mrc3_run_script() or mrc3_start_script().
       
       This function fails if:
           The handle is invalid.
           The client interface is not idle.    
       
    
       Parameters:
          handle  Input: integer handle obtained from function 
                          mrc3_new_interface().
          text    Input: MetroScript text of arbitrary length. This 
                         parameter may be an empty string.
          
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3SetScriptText(handle.value, text)
    if code != 0:
        raise RuntimeError('mrc3_set_script_text: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_set_script_context(handle, context): 
    """
        This function sets the context in which a script will run. 
        A script can run in the context of the MetroPro desktop 
        (the default) or in the context of the front-most app.
        The default context is MRC_SCRIPT_CONTEXT_FRONTMOST_APP.
        
        This function fails if:
            The handle is invalid.
            The client interface is not idle.    
        
    
        Parameters:
            handle   Input: integer handle obtained from function 
                            mrc3_new_interface().
            context  Input: integer code, one of the Script Context 
                            Codes defined above.
                            
        Returns:
            None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3SetScriptContext(handle.value, int(context))
    if code != 0:
        raise RuntimeError('mrc3_set_script_context: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_run_script(handle, wait_done):
    """
        This function causes the server MetroPro to start running 
        a script and optionally waits for completion.
        
        Before calling this function or mrc3_start_script(), either 
        mrc3_set_script_filename() or mrc3_set_script_text() must have 
        been called. If mrc3_set_script_filename() was called (passing 
        a non-empty script filename), then the script to be run is 
        specified to the server as a filename. It refers to a file that 
        exists on the server. Otherwise, if mrc3_set_script_text() was 
        called (passing a non-empty script text), then the script to be 
        run is specified to the server as text. The text, which can be 
        of arbitrary length, is transmitted from the client to the 
        server each time the script is run. The script filename takes 
        precedence if both mrc3_set_script_filename() and 
        mrc3_set_script_text() were called.
        
        This function fails if:
            The handle is invalid.
            The client interface is not idle.
            Both script text and filename are empty.
            The server MetroPro is not available.
            There is a communication error.
            MetroPro cannot transition to the active state.
        
            
        Parameters:
            handle     Input: handle obtained from function 
                              mrc3_new_interface().
            wait_done  Input: If wait_done is true, this function blocks 
                              the calling thread until the script is done 
                              running. If wait_done is false, this function 
                              starts the script running and returns.
                              
        Returns:
            None. Upon failure a RuntimeError exception is raised.
            
        See also:
            mrc3_start_script()    
    """
    
    code = mrc3RunScript(handle.value, int(wait_done))
    if code != 0:
        raise RuntimeError('mrc3_run_script: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_start_script(handle):
    """
       This function causes the server MetroPro to start running a script 
       without waiting for completion. Equivalent to calling 
       mrc3_run_script(handle, False).
       
       See the remarks for function mrc3_run_script().

       Parameters:
           handle    Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3StartScript(handle.value)
    if code != 0:
        raise RuntimeError('mrc3_start_script: ' + 
                           mrc3_get_error_message(code))


def mrc3_get_script_running(handle):
    """
    Tests if the interface is currently running a script. 
    
    This function fails if:
        The handle is invalid.
    
    Parameters:
        handle   Input: handle obtained from function mrc3_new_interface().
        
    Returns:
        1 if a script is running, 0 if not. Upon failure a RuntimeError 
        exception is raised.
    """
    
    result = c_int()
    code = mrc3GetScriptRunning(handle.value, byref(result))
    if code != 0:
        raise RuntimeError('mrc3_get_script_running: ' + 
                           mrc3_get_error_message(code))
    
    return result.value


def mrc3_wait_idle(handle, timeout_millisecs):
    """
       Waits until the client interface is idle.
       
       An idle client interface is neither running a script nor is 
       in use by another thread. This function blocks the calling 
       thread until the client interface is idle or the specified 
       timeout period has elapsed.
       
       This function fails if:
           The handle is invalid.
           The timeout period is exceeded.

       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().
           timeout_millisecs  Input: Timeout period in milliseconds. If 
                                     timeout_millisecs <= 0, the effective 
                                     timeout is infinite.
       Returns:
           None. Upon failure a RuntimeError exception is raised.
    """
    
    code = mrc3WaitIdle(handle.value, timeout_millisecs)
    if code != 0:
        raise RuntimeError('mrc3_wait_idle: ' + 
                           mrc3_get_error_message(code))
    


def mrc3_get_script_error(handle):
    """
        Gets the error code from the last script run.
        
        This function fails if:
            The client interface is not idle.
        
        Parameters:
            handle Input: handle obtained from function mrc3_new_interface().
        Returns:
            If successful, returns the integer error code resulting from the 
            last script run.  Otherwise, a RuntimeError exception is raised.
    """
    
    result = c_int()
    code = mrc3GetScriptError(handle.value, byref(result))
    if code != 0:
        raise RuntimeError('mrc3_get_script_error: ' + 
                           mrc3_get_error_message(code))
    
    return result.value


def mrc3_get_script_output(handle):
    """
       Gets the text output from the last script run.
       
       This function fails if:
           The client interface is not idle.
    
       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().
       Returns:
           If successful, returns a null padded Python-owned string containing 
           the script output. Otherwise, a RuntimeError exception is raised.
    """
    
    size = MRC_SCRIPT_OUTPUT_BUFSIZ
    result = create_string_buffer(size)
    code = mrc3GetScriptOutput(handle.value, result, size)
    if code != 0:
        raise RuntimeError('mrc3_get_script_output: ' + 
                           mrc3_get_error_message(code))
        
    return result.value


def mrc3_get_script_stop_str_val(handle):
    """
       Gets the stop string value from the last script run. 
       
       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().

       This function fails if:
           The client interface is not idle.
    
       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           If successful, returns a null padded Python-owned string containing 
           the stop string value from the script. Otherwise, a RuntimeError 
           exception is raised.
    """
    
    size = MRC_SCRIPT_OUTPUT_BUFSIZ
    result = create_string_buffer(size)
    code = mrc3GetScriptStopStrVal(handle.value, result, size)
    if code != 0:
        raise RuntimeError('mrc3_get_script_stop_str_val: ' + 
                           mrc3_get_error_message(code))
        
    return result.value


def mrc3_get_script_stop_num_val(handle):
    """
       Gets the stop numeric value from the last script run.
              
       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().

       This function fails if:
           The client interface is not idle.
    
       Parameters:
           handle  Input: handle obtained from function mrc3_new_interface().
           
       Returns:
           If successful, returns a double containing the stop numerical
           value from the script. Otherwise, a RuntimeError exception is 
           raised.
    """
    

    result = c_double()
    code = mrc3GetScriptStopNumVal(handle.value, byref(result))
    if code != 0:
        raise RuntimeError('mrc3_get_script_stop_num_val: ' + 
                           mrc3_get_error_message(code))
        
    return result.value

    
def mrc3_get_interface_guid():
    """
        This function returns a string for interface guid, which is useful
        for debugging the connection to MetroPro.
        
        Returns:
            GUID for thid DLL version
    """
    
    size = 256
    result = create_string_buffer(size)
    
    mrc3GetInterfaceGuid(result, size)
    
    return result.value
    
    
def mrc3_get_error_message(err):
    """
       This function gets a message string corresponding to an integer error 
       code.
       
       Parameters:
           err    Input: integer error code, e.g. a value returned by one of the 
                  functions in this DLL.
                  
       Returns:
           A null padded Python-owned string containing the error message.
    """
    
    
    size = 256
    result = create_string_buffer(size)
    
    mrc3GetErrorMessage(err,result,size)
    
    return result.value


def mrc3_set_status_callback_function(handle, function):
    """
        This function assigns a function that can be called to indicate a change
        in the status of the server MetroPro while it is running a script for the
        client. Use of a status callback function is optional.
        
        Parameters:
            handle      Input: integer handle obtained from function 
                        mrc3_new_interface().
            funciton    Input: Pointer to a function or NULL.
        
        Returns:
            If successful, returns void. Otherwise, raise a RuntimeError with
            an error code.
    """
    code = mrc3SetStatusCallbackFunction(handle, function)
    if code != 0:
        raise RuntimeError('mrc3_set_status_callback_function: ' + 
                           mrc3_get_error_message(code))
                           

def mrc3_set_status_callback_id(handle, callback_id):
    """
        This function assigns an integer value that will be passed to the status
        callback function. Use of a callback ID is option. The value can be used
        by the callback funciton to identify the context if a client program
        is receiving callbacks from multiple servers.
        
        Parameters:
            handle      Input: integer handle obtained from function 
                        mrc3_new_interface().
            callback_id Input: Any integer value.
            
        Returns:
            If successful, returns void. Otherwise, raise a RuntimeError with
            an error code.
    """
    code = mrc3SetStatusCallbackId(handle, callback_id)
    if code != 0:
        raise RuntimeError('mrc3_set_status_callback_id: ' + 
                           mrc3_get_error_message(code))
    
    
def mrc3_set_status_callback_mask(handle, bitmask):
    """
        While running a script for a client, a server can call back to the
        client to indicate a status change. This function specifies which
        status callbacks are required.
    
        Parameters:
            handle      Input: integer handle obtained from function
                        mrc3_new_interface().
            bitmask     Input: The logical OR of bits specified by the 
                        Enable Status Callback Bitmasks defined above.
                        
        Returns:
            If successful, returns void. Otherwise, raise a RuntimeError with
            an error code.
    """
    code = mrc3SetStatusCallbackMask(handle, bitmask)
    if code != 0:
        raise RuntimeError('mrc3_set_status_callback_mask: ' + 
                           mrc3_get_error_message(code))
    
    
# run_script (wrapper function)
def run_script(script, ip, conn_type='ncacn_ip_tcp', port='5001'):
    """
        run_script (throws exceptions):
        @Purpose:
            run a MetroScript on the target MetroPro computer, and gather the
            result, if there is any. MetroPro needs to have the necessary APP
            openned.
        @Inputs:
            script:     (String) the name of MetroScript (on MetroPro computer)
            ip:         (String) the MetroPro computer IP address
            conn_type:  (String) connection type - 'ncacn_ip_tcp' for remote control
                                                 - 'ncalrpc' for localhost
            port:       (String) connect port - '5001' default for remote control
                                              - 'localhost' for localhost
        @Outputs:
            (outBuffer, errMsg, errNum)
                outBuffer =	(String) MetroScript output buffer
                errMsg = 	(String) MetroScript error message
                errNumb = 	(float)MetroScript error status number
    """
    handle = mrc3_new_interface()
    mrc3_set_interface_params(handle, conn_type, ip, port)
    mrc3_ping_server(handle)

    mrc3_set_script_context(handle, MRC_SCRIPT_CONTEXT_FRONTMOST_APP)

    mrc3_set_script_filename(handle, script)
    mrc3_run_script(handle, True)

    err = mrc3_get_script_error(handle)
    if err != 0:
      try:
        expr = "ERROR: mrc3_client.call_script: error running MetroScript %s on %s!" % \
                (script, ip)
        msg = mrc3_get_error_message(err)
        raise MetroProClientException(expr, msg)
      finally:
        mrc3_release_control(handle)
        mrc3_free_interface(handle)

    outBuffer = mrc3_get_script_output(handle)
    errMsg = mrc3_get_script_stop_str_val(handle)
    errNum = mrc3_get_script_stop_num_val(handle)
    mrc3_release_control(handle)
    mrc3_free_interface(handle)
    
    return (outBuffer, errMsg, errNum)


def test_1():
    
    try:
        # create a new interface
        handle = mrc3_new_interface()
    
        # Set the interface parameters to communicate with a MetroPro
        # that is running on computer.at 172.18.107.71 listening to
        # port 5001.
        mrc3_set_interface_params(handle, 'ncacn_ip_tcp', '172.18.107.71', '5001')
            
        # ping the server to see if it's there.  Should
        # get back zero if it's there, exception otherwise.
        value = mrc3_ping_server(handle)
        print "VALUE = ", value
    except RuntimeError, message:
        print message
      
    # Close and free the interface. This MUST be done for each open
    # handle in order to release the memory allocated in the DLL. A 
    # memory leak will result otherwise.
    mrc3_free_interface(handle)
    
    
def test_2():
    
    try:
        # create a new interface
        handle = mrc3_new_interface()
        
        # ping the server to see if it's there.  Should
        # get back zero if it's there, exception otherwise.
        value = mrc3_ping_server(handle)
        print "VALUE = ", value
   
        # Set the interface parameters to communicate with a MetroPro
        # that is running on computer.at 172.18.107.71 listening to
        # port 5001.
        mrc3_set_interface_params(handle, 'ncacn_ip_tcp', '172.18.107.71', '5001')
        
        server_state = mrc3_get_server_state(handle)
        print "SERVER STATE = ", server_state
        
        print "GOING TO ACTIVE STATE"
        mrc3_request_control(handle)
        
        raw_input("Press Enter to return to IDLE state")

        print "RETURNING TO IDLE STATE"        
        mrc3_release_control(handle)
        
        
        
            
    except RuntimeError, message:
        print message
      
    # Close and free the interface. This MUST be done for each open
    # handle in order to release the memory allocated in the DLL. A 
    # memory leak will result otherwise.
    mrc3_free_interface(handle)
    

def example_1():
    
    # This now seems to work from my desk:
    #    Windows XP
    #    Debug DLLS
    #    180 second double pre. window time value
    #    int cast on boolean argument
    #    int cast on manifest constant
    # Need to find out why it now works.
    
    try:
        # create a new interface
        handle = mrc3_new_interface()
        print "HANDLE CREATED"
    
        # Set the interface parameters to communicate with a MetroPro
        # that is running on computer.at 172.18.107.71 listening to
        # port 5001
        mrc3_set_interface_params(handle, 'ncacn_ip_tcp', '172.18.107.71', '5001')
        print "INTERFACE SET"
        
        # ping the server to see if it's there.  Should
        # get back zero if it's there, exception otherwise.
        value = mrc3_ping_server(handle)
        print "VALUE = ", value
                
        # Run script from the desktop context.                 
        mrc3_set_script_context(handle, MRC_SCRIPT_CONTEXT_DESKTOP)
                
        # One-line script to display a message box for 10 seconds.
        text = "\t message(\" If you see this tell Jay! \", 1, 10)"
        mrc3_set_script_text(handle, text)
        print "SCRIPT TEXT SET"
        
        # Tell MetroPro to run the script and wait until it is done.
        mrc3_run_script(handle, True)
        #mrc3_start_script(handle)
        print "SCRIPT RUN"

        mrc3_release_control(handle)
    except RuntimeError, message:
        print message
        
    # Close and free the interface. This MUST be done for each open
    # handle in order to release the memory allocated in the DLL. A 
    # memory leak will result otherwise.
    mrc3_free_interface(handle)
    

def example_2():
    
    try:
        # create a new interface
        handle = mrc3_new_interface()
    
        # Set the interface parameters to communicate with a MetroPro
        # that is running on computer.at 172.18.107.71 listening to
        # port 5001
        mrc3_set_interface_params(handle, 'ncacn_ip_tcp', '172.18.107.71', '5001')
        
        # ping the server to see if it's there.  Should get back zero
        # if it's there, an exception is raised otherwise.
        value = mrc3_ping_server(handle)
                
        # Run script from the desktop context.                 
        mrc3_set_script_context(handle, MRC_SCRIPT_CONTEXT_DESKTOP)
                
        # One-line script to calculate and print the square root of 2
        text = "\t print \"The square root of 2 is \", sqrt(2)"
        mrc3_set_script_text(handle, text)
        
        # Tell MetroPro to run the script and wait until it is done.
        mrc3_run_script(handle, True)
        
        # Get the script error
        script_err = mrc3_get_script_error(handle)
        error_check(err);
        

        # Go back to the IDLE state.
        mrc3_release_control(handle)
    except RuntimeError, message:
        print message
        
    # Close and free the interface. This MUST be done for each open
    # handle in order to release the memory allocated in the DLL. A 
    # memory leak will result otherwise.
    mrc3_free_interface(handle)
    

def example_3():
    
    
    try:
        # create a new interface
        handle = mrc3_new_interface()
        print "HANDLE CREATED"
    
        # Set the interface parameters to communicate with a MetroPro
        # that is running on computer.at 172.18.107.71 listening to
        # port 5001
        mrc3_set_interface_params(handle, 'ncacn_ip_tcp', '172.18.107.71', '5001')
        print "INTERFACE SET"
        
        # ping the server to see if it's there.  Should
        # get back zero if it's there, exception otherwise.
        value = mrc3_ping_server(handle)
        print "VALUE = ", value
                
        # Run script from the desktop context.                 
        mrc3_set_script_context(handle, MRC_SCRIPT_CONTEXT_DESKTOP)
                
        # Run the script contained in 'test_script.txt'.  Note that
        # this refers to a file found on the Metropro server computer.
        mrc3_set_script_filename(handle, "c:\\jay\\test_script.txt")
        print "SCRIPT FILE SET"
        
        # Tell MetroPro to run the script and wait until it is done.
        mrc3_run_script(handle, True)
        #mrc3_start_script(handle)
        print "SCRIPT RUN"

        mrc3_release_control(handle)
    except RuntimeError, message:
        print message
        
    # Close and free the interface. This MUST be done for each open
    # handle in order to release the memory allocated in the DLL. A 
    # memory leak will result otherwise.
    mrc3_free_interface(handle)













