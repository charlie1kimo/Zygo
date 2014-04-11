import os

#------------------------------------------------------------------------------
def PrintText(File,Size='L',SavePS='N',Print='Y'):
   # Prints a text file using PSPrint
   i=0

   
   f=open(File)
   Linelist=f.readlines()
   f.close()
   NumLines=len(Linelist)
   if Size.upper()=='L':
      LinesPerPage=66
   else:
      LinesPerPage=75
      
   if NumLines>LinesPerPage:   
      LinesLeft=NumLines
      i=1
      while LinesLeft>0:
         f=open('prttemp%i.txt'%i,'w')
         if LinesPerPage<LinesLeft:
            K=LinesPerPage-1
         else:
            K=LinesLeft
         for l in range(K):
            f.write(Linelist[l])
         f.close()
         LinesLeft=LinesLeft-(LinesPerPage-1)
         if LinesLeft>0:
            Linelist=Linelist[LinesPerPage-1:]
            i=i+1
      for j in range(1,i+1):
         f=open('prttemp%i.txt'%j,'a')
         if j==i:
            LinesLeft = -1*LinesLeft
            if LinesLeft>1:
               for space in range(1,LinesLeft):
                  f.write('\n')
         f.write('\t\t\t\tPage %i of %i\n'%(j,i))
         f.close()

   if Size.upper()=='L':
      FontSize=12
      LineSpacing=10
   else:
      FontSize=8
      LineSpacing=9

   PSName=os.path.splitext(File)[0]+'.ps'      
   if i==0:     
      TextToPs(File,'temptxt.ps',45,50,FontSize,LineSpacing)
      if Print.upper()=='Y':
         PSPrint('temptxt.ps','mono')
      if SavePS.upper()=='Y':
         shutil.copyfile('temptxt.ps',PSName)
      os.remove('temptxt.ps')

   else:
      L=[]
      for p in range(1,i+1):
         TextToPs('prttemp%i.txt'%p,'temptxt%i.ps'%p,45,50,FontSize,LineSpacing)
         os.remove('prttemp%i.txt'%p)
         L.append('temptxt%i.ps'%p)
      if Print.upper()=='Y':
         PSPrint(L,'mono')
      if SavePS.upper()=='Y':
         Cline=''
         for p in L:
            Cline=Cline+" "+p
         Cline='catps '+Cline
         os.system(Cline)
         shutil.copyfile('xoutput.ps',PSName)
      for p in range(1,i+1):
         os.remove('temptxt%i.ps'%p)
   if SavePS.upper()=='Y':
      return PSName
#-----------------------------------------------------------------------------

#----------------------------------------------------------------------------
def TextToPs(FileIn,FileOut='',LeftMargin=45,TopMargin=50,FontSize=8,LineSpacing=9,FontName='Bold'):
   # Converts ascii text file to a postsript file
   if FileOut=='':
      FileOut=os.path.splitext(FileIn)[0]+'.ps'
   FontPath=getenvvar('gs_fontpath')
   if FontPath=='':
      FontPath=os.path.join(getenvvar('ghostpath'),'fonts')

   FontName=FontName.upper()
   if FontName=='BOLD':
      FontFile='n022004l.pfb'
   elif FontName=='REGULAR':
      FontFile='n022003l.pfb'
   else:
      FontFile=FontName
    

   f=open(FileOut,'w')
   f.write('\
/p\n\
{ 0.0 coffset sub 0 translate\n\
  /temp coffset def\n\
  /coffset noffset def\n\
  /noffset temp def\n\
  coffset 0 translate\n\
  copypage erasepage newpath 0 pgtop moveto\n\
} def\n\
/n\n\
{ spacing 0 3 -1 roll ashow\n\
  0 linepitch rmoveto\n\
  /y currentpoint exch pop def\n\
  y 0 lt\n\
  { p }\n\
  { 0 y moveto } ifelse\n\
} def\n\
/r\n\
{ spacing 0 3 -1 roll ashow\n\
  /y currentpoint exch pop def\n\
  0 y moveto\n\
} def\n')
   f.write('/%s\\%s findfont %.1f scalefont setfont\n'%(FontPath,FontFile,FontSize))
   f.write('/linepitch -%.1f def\n'%LineSpacing)
   f.write('/spacing 0.0 def\n')
   f.write('/coffset %i def\n'%LeftMargin)
   f.write('/noffset 30 def\n')
   f.write('\
clippath pathbbox\n\
/pgtop exch def\n\
pop /y exch def y translate\n')
   f.write('/pgtop pgtop y sub %.1f sub linepitch add def\n'%TopMargin)
   f.write('\
coffset 0 translate\n\
newpath 0 pgtop moveto\n\
')
   g=open(FileIn)
   Linelist=g.readlines()
   g.close()
   for line in Linelist:
      if line.count('\\')>=1:
         line=line.replace('\\','\\\\')
      if line.count(')')>=1:
         line=line.replace(')','\)')
      if line.count('(')>=1:
         line=line.replace('(','\(')
      if line.count('\t')>=1:
         line=line.replace('\t','        ')
         # Need to write algorithm that figures out the spacing for each tab
      f.write('('+line.rstrip()+') n\n')
   f.write('p\n')
   f.close()
#------------------------------------------------------------------------------

#----------------------------------------------------------------------------
def PSPrint(FileList,Mode='COLOR'):
   # Prints Postscript files.
   # FileList is list of the names of the postscript files.  Can be a string if one file.
   # Mode is either "color" or "mono" or "gray"

   Gpath=getenvvar('ghostpath')
   if os.path.isfile(os.path.join(Gpath,'gsprint.exe')):
      Files='xgp.cfg'
      list=[]
      
      GSExe = os.path.join(Gpath,'gswin32c.exe')   
      
      if Mode.upper()!='COLOR' and  Mode.upper()!='MONO' and Mode.upper()!='GRAY':
         return 'Incorrect mode'

      if type(FileList)==type(''):
         list.append(FileList)
      elif type(FileList)==type([]):
         list=FileList
      else:
         return 'Invalid input for FileList'
      
      for file in list:
         if not(os.path.isfile(file)):
            return '%s not found' % file
         
      f=open(Files,'w')
      for file in list:
         f.write(file+'\n')
      f.close()
      
      Cline = ' -%s -ghostscript %s -config %s > nul'%(Mode,GSExe,Files)
      Cline = os.path.join(Gpath,'gsprint') + Cline

      E=syscmd(Cline)
      if E!=0:
         return 'error in running PSPRINT!'
         
      os.remove(Files)
      return ''
   else:
      from melissa import windowtype
      CInfoPath = os.path.join(getenvvar('omasepath'),'machinfo')
      ComputerInfo = CInfoPath+'\\compinfo.cfg'
      w=windowtype()
      Exec=''
      if w=='WIN32':
         Exec=PSGetDefault(ComputerInfo,'GSEXEC')
         if Exec=='':
            Exec='gswin32c'
      elif w=='DOS16':
         Gpath='%omasepath%\\gstools\\gs5.10'
         Exec='gs386'

      
      
      list=[]
      Device=''
      Rez=300
      
      if not(os.path.isfile(ComputerInfo)):
         return 'No cpinfo.txt'
      if Mode.upper()=='COLOR':
         Device=PSGetDefault(ComputerInfo,'GSDCOLOR').lower()+' gamma.ps'
         if Device=='':
            Device='cdj550 gamma.ps'
      elif Mode.upper()=='MONO':
         Device=PSGetDefault(ComputerInfo,'GSDMONO').lower()
         if Device=='':
            Device='ljet4'
      else:
         return 'Incorrect mode'
      
      Rez=PSGetDefault(ComputerInfo,'GSREZ')
      if Rez=='':
         Rez=300

      Cline = '-q  -r%f -dNOPAUSE -sDEVICE=%s'% (Rez,Device)
      
      if type(FileList)==type(''):
         list.append(FileList)
      elif type(FileList)==type([]):
         list=FileList
      else:
         return 'Invalid input for FileList'

      for file in list:
         if not(os.path.isfile(file)):
            return '%s not found' % file
         Cline = Cline+' '+file
      Cline=Cline+' quit.ps'
      f=open('gscline.txt','w')
      f.write(Cline+'\n')
      f.close()
      if w=='WIN32':
         E=syscmd(Gpath+'\\'+Exec+' @gscline.txt')
         if E!=0:
            return 'error in running Ghostscript'
      elif w=='DOS16':
         x='tmp.bat'
         f=open(x,'w')
         f.write('set gs_lib=%s\n'%Gpath)
         f.write('set gs_fontpath=%s\\fonts\n'%Gpath)
         f.write(Gpath+'\\'+Exec+' @gscline.txt\n')
         f.close()
         E=syscmd(x)
         os.remove(x)
      os.remove('gscline.txt')
      return 0
#----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Used for getting enviromental variable values.
def getenvvar(Varname,Verbose=1):
   Name = Varname.upper()
   l = os.environ

   List={}
   K = l.keys()
   for k in K:
      List[k.upper()]=l[k]
   
   if List.has_key(Name):
      return List[Name]
   else:
      if Verbose !=1:
         print "Enviromental variable not found!!"
      return ''

#-----------------------------------------------------------------------------
# Used for running dos commands and returing an error if something goes wrong
def syscmd(Command=''):
##   Cmdline=Command.strip().split(' ')
##   if len(Cmdline)>0:
##      Exe=Cmdline[0]
##      Args=Cmdline
##   else:
##      Exe=''
##      Args=[]
##    
##   for path in os.environ["PATH"].split(os.pathsep):
##      Program = os.path.join(path, Exe)
##      try:
##         return os.spawnv(os.P_WAIT,Program,Args)
##      except os.error:
##         pass
##   print 'Could not find %s.' % Exe
##   return 1
   flag=0
   Batch='xsyscmd0'

   # Temporary addition to clean up old syscmd*.bat files.  19-Jun-2007
   os.system('if exist syscmd*.bat del syscmd*.bat')
   
   if os.path.isfile('xerror.txt'): os.remove('xerror.txt')
   while os.path.isfile(Batch+'.bat'):
      N=int(Batch[-1])
      Batch=Batch[:-1]+'%i'%(N+1)

   f=open(Batch+'.bat','w')
   f.write('@echo off\n')
   f.write(Command+'\n')
   ErrorCode=range(0,256)                                                                      #add
   ErrorCode.reverse()                                                                              #add
   for Error in ErrorCode:                                                                           #add
    f.write('if errorlevel %s goto e%s\n' % (Error,str(Error)))            #add
   for Error in ErrorCode:                                                                           #add
    f.write(':e%s\necho %s >xerror.txt\ngoto done\n' % (str(Error),Error))      # modifed
   f.write(':done')                                                                                           #add
   f.close()
   os.system(Batch)
##   os.system('copy temp.txt t.txt /y')
##   os.system('copy %s.bat+t.txt temp.txt'% Batch)
   if os.path.isfile('xerror.txt'):
      f=open('xerror.txt')
      lineList = f.readlines()
      f.close()
      for line in lineList:
          flag=int(line.strip())                                                  # modified from next line
#         fields = string.split(string.lstrip(line))                                          # delete
#         if fields[0]=='1':                                                                                 # delete
#           flag=1                                                                                                # delete
   if os.path.isfile('xerror.txt'):
      os.remove('xerror.txt')
   if os.path.isfile(Batch+'.bat'):
      os.remove(Batch+'.bat')
   return flag

#-----------------------------------------------------------------------------