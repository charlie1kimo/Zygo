from ompy import *
from env_database.env_plots2 import env_plots2

omsys.finddir('zeiss\\SL1700i\\Welle\\WLC\\R2')
#omsys.finddir('WLC R2')
env_plots2.run('ct_probes.cfg')
