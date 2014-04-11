"""
wxGnt
	a wxGnt object extends Gnt to have the graphing ability to put figure in
	wxWigets
"""

import wx
import ompy.gnt

##################################
# class WxGnt
##################################
class WxGnt(ompy.gnt.Gnt):
	
	def __init__(self, filename='', **kwds):
		super(WxGnt, self).__init__(filename, **kwds)
	
	def plot(self,color='jet',title=None,bnd=None,movefids=False,**kwds):
        """
        G.plot(...) -- Makes 2d image plot using matplotlib

        Inputs:
        color<str> = One of:
                autumn bone cool copper flag gray hot hsv jet pink
                prism spring summer winter spectral

        title<str> Title on plot
        bnd<Bnd> draws boundary on plot
        movefids<bool> if True will allow the fids to be moved by mouse drag


        Optional kwds:
        fid=<str> or <list> Examples: fid = 't' , fid = 'all' , fid = ['t','b','dim']
        clim=<tuple> color limits of plot (zmin,zmax) units mm

        Output:
        self or newGnt if movefids = True

        KeyHit fetures:
        c change plot color
        p print plot

        Usage Examples:
        G.plot()
        G.plot('pink')
        newgnt = G.plot(fid='t',movefids=True)
        '''
        '''
        Other kwds arguments used by developers
        Print prints
        dialog for printer
        write writes image file
        """
        from report import Report
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import time
        import numpy
        import pltfuncs
        def split_alpha_int(string):
            """
            alpha,intg = split_alpha_int(string)
            splits string into alpha part and int part
            Example:
            alpha,intg = split_alpha_int('dim3')
            returns dim,3
            """
            alpha = ''
            intg = None
            for i in xrange(len(string)):
                alpha = string[:i]
                try:
                    intg = int(string[i:])
                    break
                except ValueError:
                    pass
            return alpha,intg
                               
        plt.ion()
        mz=self.z.copy()
        write,Print,dialog = pltfuncs.wPd_start(plt,**kwds)
        #set up clim (zmin zmax)
        try:
            clim = kwds['clim']
        except:
            clim = None
        #disp units
        try:
            dispunits = kwds['dispunits']
        except:
            ptvmm = mz.ptp()
            if ptvmm > 1 :
                dispunits = 'mm'
            elif ptvmm > .001:
                dispunits = 'um'
            else:
                dispunits = 'nm'
        dpuscale = omsys.unitvalues[dispunits]
        #make report
        rpt  = Report()
        info = self.info()
        rpt + 'RMS: %.3f %s' % (info['rms']/dpuscale, dispunits)
        rpt + 'PTV: %.3f %s' % (info['zptv']/dpuscale, dispunits)
        rpt + 'STD: %.3f %s' % (info['std']/dpuscale, dispunits)
        rpt + ''
        rpt + 'X_apr: %.3f %s' % (info['x_aperture'], 'mm')
        rpt + 'Y_apr: %.3f %s' % (info['y_aperture'], 'mm')
        rpt + 'Apr_r_Org: %.3f %s' % (info['r_origin'],'mm')
        rpt + 'Apr_r_Cen: %.3f %s' % (info['r_center'],'mm\n')
        rpt + 'ngx: %s' % (self.z.shape[1])
        rpt + 'ngy: %s' % (self.z.shape[0])
        rpt + 'X_space:    %.3f %s' % (info['xspac'],'mm')
        rpt + 'Y_space:    %.3f %s' % (info['yspac'],'mm')
        rpt + 'Grid_X_Cen: %.3f %s' % (info['gxcen'],'mm')
        rpt + 'Grid_Y_Cen: %.3f %s' % (info['gycen'],'mm\n')
        rpt + 'Zmin:   %.3f %s' % (info['zmin']/dpuscale, dispunits)
        rpt + 'Zmax:   %.3f %s' % (info['zmax']/dpuscale, dispunits)
        rpt + 'Z_Avg:  %.3f %s' % (info['zmean']/dpuscale, dispunits)
        rpt + 'Area:   %.1f %s' % (info['area'],'mm^2')
        rpt + 'Volume: %.3f %s' % (info['volume'],'mm^3')
        rpt + 'npts:   %s' % (int(info['npts']))

        #set up figure plot
        fig = plt.figure(figsize=((10,8)))
        #ax = fig.add_subplot(111)
        #l,b,w,h
        ax = fig.add_axes([.3,.1,.65,.80])
        #setup text
        footer = (time.asctime(time.localtime())+'  ' + os.getcwd())
        fig.text(.05,.01,footer)
        plotreport = ''
        for v in rpt:
            plotreport = plotreport+'\n'+v
        fig.text(.05,.25, plotreport, fontsize=12,family='monospace')
        if title == None:
            title = ''
        try:
            name = kwds['name']
        except:
            name = omsys.getobjname(self)
        # Set up a colormap:
        palette = eval('cm.%s' % color)
        if color in ['pink','copper','gray','bone',]:
            palette.set_bad('b', .8)
        else:
            palette.set_bad('b', .5)
        #plot fids
        out_fids={} #Used for moving fiducials
        fid_labels=[] #Used for moving labels when moving fiducials
        try:
            fid = kwds['fid']
            f = self.fids.copy()
            if fid == 'all':
                fidL = list(f)
            elif isinstance(fid,(tuple,list)):
                fidL = fid
            elif isinstance(fid,str):
                fidL = [fid]
            else:
                raise ValueError,'fid input incorrect'
            for fidkey in fidL:
                if fidkey.lower() in ['t','test']:
                    #Only t fid allowed to change
                    fidkey =  'test' 
                    fidlabel = 't'
                else:
                    fidlabel = fidkey
                v = fidkey # needed until Dan can change his code
                out_fids[fidkey]=[]  # Dan code, bk changed v to fidkey
                x,y = zip(*f[fidkey])
                for i in range(len(x)):
                    ax.plot(x[i],y[i],'+',markersize=16,markeredgewidth=1,picker=5,
                            label=fidlabel+str(i+1))
                    fid_labels.append(ax.text(x[i],y[i],'  '+fidlabel+str(i+1),ha='left',va='bottom',size=10,
                            label=fidlabel+str(i+1))) # Dan code, bk changed v to fidkey
                    out_fids[fidkey].append((x[i],y[i])) # Dan code, bk changed v to fidkey
        except KeyError:
            pass
        #plot bnd
        if bnd:
            from bnd import Bnd
            bp = Bnd(bnd).topolygon(1000)
            x=list(bp.POLY_X)
            y=list(bp.POLY_Y)
            x.append(x[0])
            y.append(y[0])
            ax.plot(x,y)
        #plot image
        Zm=self.z.copy()
        Zm /= dpuscale
        extent=self._getgridextent(cellcenter=False)
        im = ax.imshow(Zm, interpolation='nearest', origin='lower',
                cmap=palette,extent=extent,aspect='equal')
        if clim:
            im.set_clim(clim)
        cbar = fig.colorbar(im,ax=ax,shrink=.80)
        title = '\n\n'+title
        ax.set_title(name,  fontsize = 14)
        fig.suptitle(title, fontsize = 18)
        tcolor = fig.text(.05,.22, 'Color: %s' % color, fontsize=11,family='monospace')
        class ColorChange(object):
            def __init__(self):
                import matplotlib.cm as cm
                self.tcolor = tcolor
                self.color = color
                self.palette = palette
                self.cm = cm
                self.k = -1
                self.cid = fig.canvas.mpl_connect('key_press_event', self.on_key)
            def on_key(self,event):
                self.k += 1
                k= self.k
                if event.key == 'c':
                    cl = ['autumn', 'bone', 'cool', 'copper', 'flag', 'gray',\
                          'hot', 'hsv', 'jet', 'pink', 'prism', 'spring',\
                          'summer', 'winter', 'spectral']
                    self.color = cl[k % 15]
                    self.palette = eval('self.cm.%s' % self.color)
                    self.tcolor.set_text('Color: %s' % self.color)
                    if self.color in ['pink','copper','gray','bone',]:
                        self.palette.set_bad('b', .8)
                    else:
                        self.palette.set_bad('b', .5)
                    im.set_cmap(self.palette)
                    fig.canvas.draw()
                if event.key == 'p':
                    fn = omsys.rndfilename('ps')
                    print 'Making Image for print...'
                    self.palette.set_bad(alpha=0.)
                    im.set_cmap(self.palette)
                    fig.savefig(fn,orientation='landscape',dpi=600)
                    plt.close(fig)
                    omsys.psprint(fn,dialog = True)
                    os.remove(fn)
                    plt.close(fig)
                    fig.canvas.mpl_disconnect(self.cid)
                    print 'Print Done, Enter to Continue\n'
        class MoveFids(object):
            '''returns new fiducial locations
            '''
            def __init__(self,axes):
                self.fid_labels=fid_labels
                self.out_fids=out_fids
                self.pick = None
                self.point = None
                self.axes = axes
                self.connect()
                plt.draw()
                raw_input('Enter to Close and Continue')
                plt.close(self.axes.figure)
                #psdseto.overlap = self.overlap
                return

            def connect(self):
                'connect to all the events we need'
                self.cidpick = self.axes.figure.canvas.mpl_connect(
                    'pick_event', self.on_pick)
                self.cidrelease = self.axes.figure.canvas.mpl_connect(
                    'button_release_event', self.on_release)
                self.cidmotion = self.axes.figure.canvas.mpl_connect(
                    'motion_notify_event', self.on_motion)
                self.cidkey = self.axes.figure.canvas.mpl_connect(
                    'key_press_event', self.on_key)

            def on_key(self,event):
                if event.key in ['enter','escape']:
                    plt.close(self.axes.figure)
                    print '\nEnter to Continue:',
                if event.key == 'p':
                    fn = omsys.rndfilename('ps')
                    print '\nMaking Image for print...'
                    self.axes.figure.savefig(fn,orientation='landscape',dpi=600)
                    omsys.psprint(fn,dialog = True)
                    os.remove(fn)
                    print 'Print Done, Enter to Continue\n'

            def on_motion(self, event):
                'on motion we will move the point if the mouse is over us'
                
                if self.pick is None: return
                if event.inaxes != self.axes: return
                self.point.set_xdata(event.xdata)
                self.point.set_ydata(event.ydata)
                self.point.figure.canvas.draw()
                name = self.point.get_label()
                for f_l in self.fid_labels:
                    if f_l.get_label() ==name:
                        f_l.set_position((event.xdata,event.ydata))
                

            def on_release(self, event):
                'on release we reset the press data'
                if self.point is None: return
                name = self.point.get_label()
                x = event.xdata
                y = event.ydata
                
                self.point.set_xdata(x)
                self.point.set_ydata(y)
                self.point.figure.canvas.draw()
                self.pick = None
                self.point = None
                for f_l in self.fid_labels:
                    if f_l.get_label() == name:
                        f_l.set_position((x,y))
                        alpha,intg = split_alpha_int(name)# added to Dan's code
                        if alpha == 't':
                            alpha =  'test'
                        self.out_fids[alpha][intg-1]=(x,y) #changed Dan's code

            def disconnect(self):
                'disconnect all the stored connection ids'
                #don't think this is being used
                self.point.figure.canvas.mpl_disconnect(self.cidpress)
                self.point.figure.canvas.mpl_disconnect(self.cidrelease)
                self.point.figure.canvas.mpl_disconnect(self.cidmotion)

            def on_pick(self,event):
                self.pick = True
                self.point = event.artist
        if movefids:
            
            fig.canvas.draw()
            rr = ColorChange()
            f=MoveFids(ax)
            out_gnt=self.copy()
            for fid_name in out_fids:
                out_gnt.fids[fid_name]=out_fids[fid_name]
            return out_gnt
        elif Print:
            fn = omsys.rndfilename('ps')
            print 'Making Image for print...'
            palette.set_bad(alpha=0.)
            im.set_cmap(palette)
            fig.savefig(fn,orientation='landscape',dpi=600)
            plt.close(fig)
            omsys.psprint(fn,dialog = dialog)
            os.remove(fn)
            return
        elif write:
            imtype = kwds['imtype']
            print'Making Image for file: %s' % name
            palette.set_bad(alpha=0.)
            im.set_cmap(palette)
            fig.savefig(name,orientation='landscape',dpi=300,format=imtype)
            plt.close(fig)
        else:
            fig.canvas.draw()
            rr = ColorChange()
            raw_input('Enter to Close and Continue\n')
            plt.close(fig)
        return self.copy()

if __name__ == "__main__":
	print "hello world!"