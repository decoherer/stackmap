import numpy as np
from wavedata import Wave

class Stackmap():
        def __init__(self,x0,x1,y0,y1=None):
            self.limits = self.x0,self.x1,self.y0,self.y1 = (x0,x1,y0,y1)
            self.stack = [Wave(2*[y0],[x0,x1],'')]
            self.stackhistory = []
            self.titlehistory = []
            self.colors = {'SiO₂':'#9dd0d4','Al₂O₃':'#a47fad'}
            self.colors.update(dict(resist='#f288b6',tfln='#d17a24',quartz='#d7dbda',
                               metal='#edcf4a',gold='#edcf4a',sio2='#9dd0d4',al2o3='#a47fad',
                               ti='#c9c2d1',au='#edcf4a',si='#f0b27a')) # si last since si is in sio2
        def color(self,name):
            if name is None: return None
            for k in self.colors:
                if k.lower() in name.lower(): return self.colors[k]
            return None
        def widths2wave(self,widths,invert=False):
            d = self.x1-self.x0-np.nansum(widths)
            n = np.sum(np.isnan(widths))
            widths = np.nan_to_num(widths,nan=d/n)
            wy = [0] + [0,1,1,0]*(len(widths)//2) + [0]
            wy = [1-y for y in wy] if invert else wy
            wx = [xx for x in np.cumsum([0]+list(widths)) for xx in [x,x]]
            wx = self.x0 + np.array(wx[1:-1])
            return Wave(wy,wx)
        

        def liftoff(self,liftoffdepth=2,title='Liftoff'):
            # assumes liftoff layer is the penulitmate layer
            assert 2==liftoffdepth, '2<liftoffdepth not yet implemented'
            assert liftoffdepth<len(self.stack)
            self.stackhistory += [self.stack[:]]
            self.titlehistory += [title]
            c,b,a = self.stack[-3:]
            b = b.mergex(a)
            c = c.mergex(b)
            isthick = ~np.isclose(b.y,c.y)
            anew = Wave(np.where(isthick,c.y,a.y),a.x,a.name)
            bnew = Wave(c.y,c.x,'',lw=0)
            self.stack = self.stack[:-2] + [bnew,anew]
            return self
        def strip(self,layerdepth=1,title='Strip'):
            # assumes strip layer is the penulitmate layer
            assert layerdepth+1<len(self.stack)
            self.stackhistory += [self.stack[:]]
            self.titlehistory += [title]
            # b,a = self.stack[-2:]
            # n = len(self.stack)-layerdepth
            # c,b = self.stack[n-1:n+1]
            # bnew = Wave(c.y,c.x,'',lw=0)
            # self.stack = self.stack[:n] + [bnew] + self.stack[n+1:]

            n = len(self.stack)-layerdepth
            c,b,*aa = self.stack[n-1:]
            bnew = Wave(c.y,c.x,'',lw=0)
            delta = b.addlayer(-c)
            aanew = [a.addlayer(-delta).rename(a.name) for a in aa]
            self.stack = self.stack[:n] + [bnew] + aanew
            return self
            # todo: check 'warning: non-zero thickness above stripped layer'

        def etch(self,w,title='Etch'):
            assert np.all(0<=w)
            self.stackhistory += [self.stack[:]]
            self.titlehistory += [title]
            profile = self.stack[-1].addlayer(-w)
            self.stack = [u.minimumlayer(profile) for u in self.stack]
            return self
        def exposedevelop(self,w,mask,title0='Expose',title1='Develop',airgap=1,maskdepth=2):
            # mask = +1 for positive resist, -1 for negative resist
            u0 = self.stack[-1]
            assert (+1==mask and 'positive resist' in u0.name.lower()) or (-1==mask and 'negative resist' in u0.name.lower())
            uair = (airgap+max(u0)+0*u0).rename('').setplot(c='#ffffff00',lw=0)
            wmask = maskdepth*np.sign(w if -1==mask else max(w)-w)
            umask = uair.addlayer(wmask).rename('mask').setplot(c='k',lw=0)
            self.stack += [uair,umask]
            self.plot()
            self.stack = self.stack[:-2]
            self.stackhistory += [self.stack]
            self.titlehistory += [title1]

            self.etch(w,title=title1)

            return self
        
        def develop(self,w,title='Develop',mask=0):
            return self.etch(w,title=title)            
        def masketch(self,depth,title='Etch'):
            # top layer assumed to be the mask for the etch
            assert 1<len(self.stack)
            a = self.stack[-1]
            b = self.stack[-2].mergex(a)
            w = Wave(depth*np.isclose(a.y,b.y),a.x)
            return self.etch(w,title=title)
        def deposit(self,w,name='',title=''):
            title = title if title else f'Deposit {name}'
            return self.addlayer(w,name,title=title)
        def addlayer(self,w,name='',title=''):
            title = title if title else name
            self.stackhistory += [self.stack[:]]
            self.titlehistory += [f'{title}']
            w = w if isinstance(w,Wave) else Wave([w,w],[self.x0,self.x1])
            layer = self.stack[-1].addlayer(w)
            self.stack += [layer.rename(name)]
            return self
        def addsymlayer(self,thickness,widths,name='',title='',invert=False):
            assert 1==len(widths)%2 and np.all(np.array(widths)==np.array(widths[::-1]))
            # print(self.widths2wave([np.nan]+widths+[np.nan],invert=invert))
            d = 0.5*(self.x1-self.x0-np.sum(widths))
            widths = [d]+list(widths)+[d]
            wy = [0] + [0,1,1,0]*(len(widths)//2) + [0]
            wy = [1-y for y in wy] if invert else wy
            wx = [xx for x in np.cumsum([0]+list(widths)) for xx in [x,x]]
            wx = np.array(wx[1:-1])-0.5*np.sum(widths)
            self.addlayer(thickness*Wave(wy,wx),name,title=title)
            return self
        def ppt(self,title,**kwargs):
            save = f"figs/{kwargs.pop('save',title)}.pptx"
            from pypowerpoint import Presentation,addadvrslide
            from time import sleep
            pngs = list(self.plothistory(title,**kwargs))
            sleep(5)
            prs = Presentation()
            for n,(pngfile,text) in enumerate(zip(pngs,self.titlehistory)):
                addadvrslide(prs,title=title,text=text,imagefile=pngfile)
            prs.save(save)
            return prs
        def plothistory(self,title,**kwargs):
            stacks = self.stackhistory[1:]+[self.stack]
            N = max([len(stack) for stack in stacks])
            cc = kwargs.pop('c','01234567890123456789'[:N])
            for n,stack in enumerate(stacks):
                c = [self.color(w.name) for w in stack]
                c = [(ci if ci else cci) for ci,cci in zip(c,cc)]
                d = dict(c=c[::-1],
                         fillbetween=1,x='µm',y='µm',xlim=(self.x0,self.x1),ylim=(self.y0,self.y1),
                         corner='upper right',seed=8,scale=1.8,dpi=300,aspect=1,lw=1,show=0,fork=0)
                d.update(**kwargs)
                yield Wave.plots(*stack[::-1],**d,save=f'{title} {n:02d}.png')
        def plot(self,**kwargs):
            # c = [str(n) for n in range(len(self.stack))][::-1]
            c = '01234567890123456789'[:len(self.stack)][::-1]
            d = dict(c=c,fillbetween=1,x='µm',y='µm',xlim=(self.x0,self.x1),ylim=(self.y0,self.y1),
                     corner='upper right',seed=8,scale=1.8,dpi=300,aspect=1,lw=1)
            d.update(**kwargs)
            return Wave.plots(*self.stack[::-1],**d)

if __name__ == '__main__':
    L = Stackmap(-20,20,-5,15)
    L.addlayer(5,'quartz')
    L.addlayer(3,'silicon 3µm')

    # L.deposit(0.5,'positive resist 0.5µm')
    # L.exposedevelop(0.5*Wave([0,0,1,1,0,0,1,1,0,0],[-20,-10,-10,-5,-5,5,5,10,10,20]),mask=+1)

    L.addsymlayer(0.5,[5,10,5],'resist 0.5µm',invert=1)
    L.masketch(1.5)
    L.addlayer(1,'metal 1µm')
    L.liftoff()
    L.addlayer(2,'SiO₂ 2µm')#.plot()
    L.ppt('stackmap example')

    L.plot()

    # todo: wave from list of widths
