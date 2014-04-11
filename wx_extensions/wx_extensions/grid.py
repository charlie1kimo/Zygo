"""
grid.py
    grid.py contains the useful grid extension class for wxPython grid
    for example, the CustomDataGrid class can have a custom data table
    rather than all String data table in original wxPython grid class.
"""
__version__ = '1.0'
__owner__ = 'cchen'
'''
History:
3/7/2013    cchen   first created documentation
'''

import  wx
import  wx.grid as gridlib

#######################################################################
## class CustomDataGrid
#   @Purpose:
#       Wrapper of the CustomDataTable
#######################################################################
class CustomDataGrid(gridlib.Grid):
    """
    class CustomDataGrid
    @Purpose:
        Wrapper of the CustomDataTable
    @Constructor: 
        CustomDataGrid(parent, labels, dataTypes, data=[], rowGrouped=False)
        parent = parent wxWidget
        labels = list of labels of fixed row or column
        dataTypes = [gridlib.GRID_VALUE_NUMBER,
                       gridlib.GRID_VALUE_STRING,
                       gridlib.GRID_VALUE_NUMBER + ':1,5',
                       gridlib.GRID_VALUE_CHOICE + ':all,MSW,GTK,other',
                       gridlib.GRID_VALUE_BOOL,
                       gridlib.GRID_VALUE_FLOAT + ':6,2',   #second number is num of significant digit
                       gridlib.GRID_VALUE_CHOICEINT,
                       gridlib.GRID_VALUE_DATETIME,
                       gridlib.GRID_VALUE_TEXT,
                       ]
        data = table data (2D array aka array of array, first index is row)
        rowGrouped = True if group by row; False if group by column
    """

    def __init__(self, parent, labels, dataTypes, data=[], rowGrouped=False):
        gridlib.Grid.__init__(self, parent, -1)

        table = CustomDataTable(labels, dataTypes, data, rowGrouped)
        self.table = table
        self.labels = labels
        self.dataTypes = dataTypes
        self.rowGrouped = rowGrouped

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.table, True)

        # setup cell default attributes
        # Columns
        self.EnableDragColSize(True)
        if rowGrouped:
            self.SetColLabelSize(1)
        else:
            self.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        
        # Rows
        self.EnableDragRowSize(True)
        if not rowGrouped:
            self.SetRowLabelSize(1)
        else:
            self.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Cell background color hack (make cells background = panel background for beauty)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.SetDefaultCellBackgroundColour(color)
        
        # Cell Defaults
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.SetFocus()
        self.AutoSize()
    
    def GetCellValue(self, row, col):
        return self.table.GetValue(row, col)
    
    def SetCellValue(self, row, col, value):      
        if not self.table.CanSetValueAs(row, col, type(value).__name__):
            raise TypeError("Expecting value type to be %s, but value type is %s" % \
                    (self.table.GetTypeName(row, col), type(value).__name__))
        
        self.table.SetValue(row, col, value)
    
    # ClearTable:
    # @Purpose:
    #   Clear the data in table, but preserve the data types and labels
    def ClearTable(self):
        self.table = CustomDataTable(self.labels, self.dataTypes, [], self.rowGrouped)
        self.SetTable(self.table, True)

    # SetRowReadOnly:
    # @Purpose:
    #   Set a row to be readonly
    def SetRowReadOnly(self, row):
        readonlyAttr = gridlib.GridCellAttr()
        readonlyAttr.SetReadOnly(True)
        self.SetRowAttr(row, readonlyAttr)

    # SetColReadOnly:
    # @Purpose:
    #   Set a column to be readonly
    def SetColReadOnly(self, col):
        readonlyAttr = gridlib.GridCellAttr()
        readonlyAttr.SetReadOnly(True)
        self.SetColAttr(col, readonlyAttr)

    # ResetDefaultCellBackgroundColour:
    # @Purpose:
    #   Reset the cell background colour to the default
    def ResetDefaultCellBackgroundColour(self, row, col):
        # Cell background color hack (make cells background = panel background for beauty)
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.SetCellBackgroundColour(row, col, color)
        

#######################################################################
## class CustomDataTable
#   @Constructor:
#       CustomDataTable(labels, dataTypes, data=[], rowGrouped=False)
#       @Inputs:
#           labels = [label, ...]
#           dataTypes = [gridlib.GRID_VALUE_NUMBER,
#                       gridlib.GRID_VALUE_STRING,
#                       gridlib.GRID_VALUE_NUMBER + ':1,5',
#                       gridlib.GRID_VALUE_CHOICE + ':all,MSW,GTK,other',
#                       gridlib.GRID_VALUE_BOOL,
#                       gridlib.GRID_VALUE_FLOAT + ':6,2',
#                       gridlib.GRID_VALUE_CHOICEINT,
#                       gridlib.GRID_VALUE_DATETIME,
#                       gridlib.GRID_VALUE_TEXT,
#                       ]
#           data = table data (array of an array; 2D array)
#           rowGrouped = True if dataTypes are grouped by row; False if dataTypes are grouped by column
#######################################################################
class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self, labels, dataTypes, data=[], rowGrouped=False):
        gridlib.PyGridTableBase.__init__(self)
        self.typesMap = {'long': ['int', 'long'],
                        'string': ['str', 'unicode'],
                        'choice': ['str', 'unicode'],
                        'bool': ['bool'],
                        'double': ['float', 'float64'],
                        'choiceint': ['int', 'long'],
                        'datetime': ['datetime']}
        self.rowLabels = []
        self.colLabels = []
        self.dataTypes = dataTypes
        self.data = data
        self.rowGrouped = rowGrouped
        
        if rowGrouped:
            self.rowLabels = labels
            if len(labels) > 0 and len(self.data) == 0:
                self.data = [[None] for i in range(len(labels))]
        else:
            self.colLabels = labels
            if len(labels) > 0 and len(self.data) == 0:
                self.data = [[None for i in range(len(labels))]]

    #-----------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        if len(self.data) == 0:
            return 0
            
        return len(self.data[0])

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    # Get/Set values in the table.  The Python version of these
    # methods can handle any data-type, (as long as the Editor and
    # Renderer understands the type too,) not just strings as in the
    # C++ version.
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        try:
            typeKey = self.GetTypeName(row, col).split(':')[0]
            typeName = self.typesMap[typeKey][0]
            exec("self.data[row][col] = "+typeName+"(value)")
        except IndexError:
            if self.rowGrouped:
                # add a new col
                for r in self.data:
                    r.append('')
                self.SetValue(row, col, value)
                    
                # tell the grid we've added a col
                msg = gridlib.GridTableMessage(self,            # The table
                    gridlib.GRIDTABLE_NOTIFY_COLS_APPENDED, # what we did to it
                    1                                       # how many
                    )
            else:
                # add a new row
                self.data.append([''] * self.GetNumberCols())
                self.SetValue(row, col, value)

                # tell the grid we've added a row
                msg = gridlib.GridTableMessage(self,            # The table
                    gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, # what we did to it
                    1                                       # how many
                    )

            self.GetView().ProcessTableMessage(msg)
        except ValueError:
            # here is for float('') and int(''); default to do nothing
            pass

    #--------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        if len(self.colLabels) > 0:
            return self.colLabels[col]
        else:
            return ''
    
    def GetRowLabelValue(self, row):
        if len(self.rowLabels) > 0:
            return self.rowLabels[row]
        else:
            return ''

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        if self.rowGrouped:
            return self.dataTypes[row]
        else:
            return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, typeName):
        if self.rowGrouped:
            index = row
        else:
            index = col
        dType = self.dataTypes[index].split(':')[0]
        if typeName in self.typesMap[dType]:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)
