"""Rebuild TVT revision figures from the unchanged local evidence.

The small JSON/CSV inputs saved alongside the figures make this plotting step
portable; the extraction step requires the original UAV experiment project.
Usage: python figures/make_figures.py [--extract E:/path/to/experiment/project]
"""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
from figure_palette import PRIMARY, SECONDARY, LIGHT_PRIMARY, QUADRANT_BACKGROUND

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--extract', type=Path)
parser.add_argument('--selected', nargs='*', help='Only write named data figures.')
parser.add_argument('--data-only', action='store_true', help='Rebuild data plots without touching the system diagram.')
args = parser.parse_args()
if args.extract:
    p = args.extract
    summary = json.loads((p/'results/final_guard_confirmation/summary.json').read_text(encoding='utf-8-sig'))
    quality = [json.loads((p/f'results/uav_continuation/quality_{e:02d}.json').read_text(encoding='utf-8-sig'))['bounds'] for e in (0,25)]
    data = dict(pairs=summary['pairs'], quality=quality,
                provenance={'pairs':'results/final_guard_confirmation/summary.json: pairs',
                            'quality':'results/uav_continuation/quality_00.json and quality_25.json: bounds',
                            'ledgers':'results/uav_continuation/chain_progress.json: runs',
                            'scale':'manuscript/uav_executable_scheduling_e4n15.tex: tab:bounded-scale'},
                scale=dict(sources=[2,4,8,16], interval=[278323,558404,1113477,2216410],
                           exact=[275637,552895,1102772,2203587],
                           loss_interval_percent=[.133,.067,.200,.400],
                           loss_exact_percent=[.067,.133,.200,.400]))
    rows=json.loads((p/'results/uav_continuation/chain_progress.json').read_text(encoding='utf-8-sig'))['runs']
    data['ledgers']=[]
    for budget in (1000,1280):
        for loss in (0.,.1):
            r=[v for v in rows if v['budget']==budget and v['loss'][0]==loss]
            a=next(v for v in r if v['method']=='ExactMarginal')
            b=next(v for v in r if v['method']=='IntervalNoReport')
            data['ledgers'].append(dict(budget=budget,loss=loss,ip=b['total_wire_bytes']-a['total_wire_bytes'],udp=b['outer_wire_bytes']-a['outer_wire_bytes']))
    (HERE/'plot_data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
else:
    data=json.loads((HERE/'plot_data.json').read_text(encoding='utf-8'))

plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
    'mathtext.fontset':'stix','font.size':9,'axes.labelsize':9.5,'axes.titlesize':9,
    'axes.labelweight':'bold','xtick.labelsize':8.5,'ytick.labelsize':8.5,'legend.fontsize':8.5,
    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
    'axes.spines.top':True,'axes.spines.right':True,'axes.linewidth':1.0,
    'axes.facecolor':'white','axes.edgecolor':'black','axes.grid':False,
    'xtick.direction':'in','ytick.direction':'in','legend.fancybox':False,
    'axes.axisbelow':True,'lines.linewidth':1.4,'savefig.facecolor':'white'})
BLUE=PRIMARY; ORANGE=SECONDARY
LOCKED_OUTPUTS=[]
GENERATED=[]
def origin_axes(ax):
    """Consistent publication theme inspired by conventional Origin 2D graphs."""
    inset=getattr(ax,'_origin_inset',False)
    ax.set_facecolor('white')
    ax.grid(False,which='both')
    for spine in ax.spines.values():
        spine.set_visible(True);spine.set_edgecolor('black');spine.set_linewidth(.7 if inset else 1.0)
    ax.tick_params(axis='both',which='major',direction='in',top=False,right=False,
                   length=2.6 if inset else 4.2,width=.7 if inset else .85,
                   colors='black',labeltop=False,labelright=False,pad=2.5)
    if not inset:
        if not getattr(ax,'_categorical_x',False):ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        if not getattr(ax,'_categorical_y',False):ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='both',which='minor',direction='in',top=False,right=False,length=2.2,width=.65)
    legend=ax.get_legend()
    if legend is not None:
        legend.set_frame_on(True)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_edgecolor('black')
        legend.get_frame().set_linewidth(.6)
        legend.get_frame().set_alpha(1.)
    for child in ax.child_axes:origin_axes(child)

def regular_ticks(ax,axis,nbins=4):
    """Display every major tick, with axis endpoints on the first/last tick."""
    lo,hi=getattr(ax,f'get_{axis}lim')()
    ticks=MaxNLocator(nbins=nbins,min_n_ticks=3).tick_values(lo,hi)
    getattr(ax,f'set_{axis}ticks')(ticks)
    getattr(ax,f'set_{axis}lim')(ticks[0],ticks[-1])

def save(fig,name):
    if args.selected and name not in args.selected:
        plt.close(fig); return
    for ax in fig.axes:origin_axes(ax)
    for ext in ('pdf','eps','png'):
        out=HERE/(name+'.'+ext)
        tmp=HERE/(name+'.pending.'+ext)
        fig.savefig(tmp,format=ext,dpi=240)
        try:
            tmp.replace(out)
        except PermissionError:
            # Some Windows PDF viewers deny rename but allow content refresh.
            try:
                out.write_bytes(tmp.read_bytes())
                tmp.unlink()
            except PermissionError:
                LOCKED_OUTPUTS.append(str(out))
    GENERATED.append(name)
    plt.close(fig)

# The current model is the author's corrected vector PDF, not the old generator.
# Rebuilding data figures must preserve this diagram, including in default mode.

# The curve is evaluated from the same stored profile coefficients as admission.
fig,ax=plt.subplots(figsize=(3.5,2.60),layout='constrained')
t=np.linspace(0,.8,161)
for i,b in enumerate(data['quality']):
    tp,tv,ep,ev,A,beta,jp,jv=b
    r=.01486216499869309+2*(tp+ep)+t*(.05882613629652209+tv+ev+beta)+.5*A*t*t+jp+t*jv
    assert abs(r[-1]-[.441932,.403072][i])<1e-6
    ax.plot(t,r,color=[BLUE,ORANGE][i],ls=['-','--'][i],marker=['o','s'][i],
            markevery=20,ms=5.2,mfc='none',mew=1.1,clip_on=False,label=f'UAV {i+1}')
ax.axhline(.5,color='#333333',ls=':',lw=1.1,label='_nolegend_')
# Keep the measured domain and ticks, with room for the full endpoint markers.
ax.set(xlim=(-.025,.825),ylim=(0,.6),xlabel='Prospective update age (s)',ylabel='Certified position bound (m)',
       xticks=np.arange(0,.81,.1),yticks=np.arange(0,.61,.1))
ax.grid();ax.legend(loc='upper left',bbox_to_anchor=(.015,.86),frameon=False,handlelength=3.2,numpoints=1,handletextpad=.7)
save(fig,'quality_profiles')

# Every fixed comparator and condition is retained. Plot the paired CPU median;
# all three observations and their measured range remain in the CSV evidence.
panels=[('GuardedInterval',0.,'Scalar interval'),('GuardedTwoInterval',0.,'Two intervals'),('FixedLocal',0.,'FixedLocal'),
        ('Hatami',0.,r'Hatami ($\eta=0$)'),('Hatami',.1,r'Hatami ($\eta=0.1$)'),('Hatami',1.,r'Hatami ($\eta=1$)'),
        ('Yang',0.,r'Yang ($\eta=0$)'),('Yang',.01,r'Yang ($\eta=0.01$)'),('Yang',.1,r'Yang ($\eta=0.1$)')]
fig,axs=plt.subplots(3,3,figsize=(7.16,5.8))
for k,(ax,(method,eta,title)) in enumerate(zip(axs.flat,panels)):
    rows=[x for x in data['pairs'] if x['reference']==method and x['price']==eta]
    assert len(rows)==16
    groups={}
    for r in rows:
        key=(r['saved_bytes']/1000,r['extra_cpu_ms']/1000,r['task_gate'])
        groups[key]=groups.get(key,0)+1
    def draw_points(target,marker_size,annotate_duplicates=True):
        for (px,py,gate),count in groups.items():
            color=PRIMARY if gate else SECONDARY
            target.plot([px],[py],ls='',marker='o' if gate else '^',ms=marker_size*np.sqrt(count),
                        mfc='white',mec=color,mew=.8,zorder=3)
            if count>1 and annotate_duplicates:
                target.annotate(r'$\times'+str(count)+'$',(px,py),xytext=(4,-1),
                                textcoords='offset points',ha='left',va='center',
                                fontsize=7.5,color=color,zorder=5)
    draw_points(ax,3.4)
    ax.axhline(0,color='#545454',lw=.8,ls='--',zorder=2);ax.axvline(0,color='#545454',lw=.8,ls='--',zorder=2)
    ax.tick_params(pad=2,labelsize=7.5);ax.locator_params(axis='both',nbins=4)
    ax.set_xlabel('Saved contract bytes (kB)',fontsize=8,labelpad=3)
    ax.set_ylabel('Extra session CPU (s)',fontsize=8,labelpad=3)
    ax.text(.5,-.42,f'({chr(97+k)}) {title}',transform=ax.transAxes,
            ha='center',va='top',fontsize=8.5)
    ax.grid();ax.margins(x=.15,y=.12)
    ymin,ymax=ax.get_ylim();ax.set_ylim(ymin,ymax+.45*(ymax-ymin))
    regular_ticks(ax,'x');regular_ticks(ax,'y')
    xmin,xmax=ax.get_xlim(); ymin,ymax=ax.get_ylim()
    if xmax>0 and ymin<0:
        ax.add_patch(Rectangle((0,ymin),xmax,-ymin,facecolor=QUADRANT_BACKGROUND,edgecolor='none',zorder=0))
    ax.legend(handles=[Line2D([],[],color=PRIMARY,marker='o',mfc='white',ms=3.8,ls='',label='Task preserved'),
                       Line2D([],[],color=SECONDARY,marker='^',mfc='white',ms=3.8,ls='',label='Task trade-off')],
              loc='upper right',ncol=1,fontsize=7.5,frameon=False,
              handletextpad=.3,borderpad=.3,labelspacing=.2,handlelength=1)
    zoom=None
    if method=='GuardedTwoInterval':
        zoom=(-.01,.01,-.21,-.11)
    elif method=='Hatami' and eta==1.:
        zoom=(.40,1.00,-10.,0.)
    if zoom is not None:
        xmin,xmax,ymin,ymax=zoom
        inset=ax.inset_axes([.14,.65,.30,.30])
        inset._origin_inset=True
        draw_points(inset,2.8)
        inset.set(xlim=(xmin,xmax),ylim=(ymin,ymax))
        inset.tick_params(labelsize=7,pad=1,length=2)
        inset.set_xticks([xmin,0,xmax] if method=='GuardedTwoInterval' else [.4,.7,1.])
        inset.set_yticks([-.21,-.16,-.11] if method=='GuardedTwoInterval' else [-10,-5,0])
        inset.grid(lw=.4)
        for spine in inset.spines.values():spine.set_edgecolor('#77828C')
        ax.add_patch(Rectangle((xmin,ymin),xmax-xmin,ymax-ymin,fill=False,
                               edgecolor='#77828C',ls=':',lw=.7,zorder=2))
fig.subplots_adjust(left=.095,right=.99,bottom=.12,top=.97,hspace=.92,wspace=.50)
save(fig,'paired_cost_frontier')

# Descriptive counts of all fixed conditions; no independence/significance claim.
fig,ax=plt.subplots(figsize=(3.5,3.65))
counts=[]
for method,eta,title in panels:
    rows=[r for r in data['pairs'] if r['reference']==method and r['price']==eta]
    nwin=sum(bool(r['task_gate']) and r['saved_bytes']>0 and r['saved_outer_bytes']>0
             and all(v<0 for v in r['extra_cpu_rounds_ms']) for r in rows)
    ngate=sum(bool(r['task_gate']) for r in rows)
    counts.append([nwin,ngate-nwin,16-ngate])
assert all(sum(r)==16 for r in counts)
ax._categorical_y=True
left=np.zeros(9);y=np.arange(9)[::-1]
for j,(col,hatch,label) in enumerate([(PRIMARY,None,'Joint benefit'),(LIGHT_PRIMARY,'///','Task preserved, other'),(SECONDARY,'..','Task trade-off')]):
    vals=100*np.array(counts)[:,j]/16
    ax.barh(y,vals,left=left,height=.62,color=col,hatch=hatch,edgecolor='#444444',lw=.45,label=label)
    for yy,v,l in zip(y,vals,left):
        if v:ax.text(l+v/2,yy,f'{v:g}%',ha='center',va='center',fontsize=6.3,color='white' if j==0 else '#222222',bbox=dict(facecolor=col,edgecolor='none',pad=.5))
    left+=vals
ax.set(yticks=y,yticklabels=[r[2] for r in panels],xlim=(0,100),xticks=np.arange(0,101,25),ylim=(-.65,12.0))
ax.tick_params(axis='y',labelsize=7)
ax.set_xlabel('Share of conditions (%)',fontsize=8)
ax.legend(loc='upper left',fontsize=7,handlelength=1.8,labelspacing=.4,borderpad=.45)
fig.subplots_adjust(left=.35,right=.97,bottom=.13,top=.98)
save(fig,'paired_outcome_counts')
(HERE/'paired_outcome_counts.csv').write_text('comparator,price,joint_benefit,gate_met_other,gate_not_met\n'+
    ''.join(f'{method},{eta},'+','.join(map(str,c))+'\n' for (method,eta,_),c in zip(panels,counts)),encoding='utf-8')

# Alternative byte ledgers share units but are not additive. Pair them by condition.
fig,ax=plt.subplots(figsize=(3.5,2.8))
rows=data['ledgers'];y=np.arange(len(rows))[::-1]
assert [r['ip'] for r in rows]==[266,333,550,330]
assert [r['udp'] for r in rows]==[-1097,-243,830,498]
ax._categorical_y=True
ax.axvline(0,color='#444444',lw=.8,zorder=1)
for key,offset,color,marker,style,label in [
    ('ip',.15,BLUE,'o','-','Contract IP'),
    ('udp',-.15,ORANGE,'s','--','Outer UDP')]:
    for yp,r in zip(y,rows):
        value=r[key];level=yp+offset
        ax.plot([0,value],[level,level],color=color,ls=style,lw=1.4,zorder=2)
        ax.plot(value,level,marker=marker,ms=5,mfc='white',mec=color,mew=1.2,ls='',zorder=3)
        ax.annotate(str(value),(value,level),xytext=(5 if value>=0 else -5,0),
                    textcoords='offset points',ha='left' if value>=0 else 'right',
                    va='center',fontsize=7.4,color='black')
ax.set(xlim=(-1500,1500),xticks=np.arange(-1500,1501,500),ylim=(-.6,4.1),yticks=y,
       yticklabels=[fr"${r['budget']},\ {r['loss']:g}$" for r in rows])
ax.set_xlabel('Saved bytes (B)',fontsize=9,labelpad=4)
ax.set_ylabel(r'Refill $B$ (B/s), loss $p$',fontsize=8.5,labelpad=5)
ax.tick_params(axis='x',labelsize=7)
ax.tick_params(axis='y',labelsize=8)
ax.legend(handles=[Line2D([],[],color=BLUE,marker='o',mfc='white',mew=1.2,ms=5,ls='-',label='Contract IP'),
                   Line2D([],[],color=ORANGE,marker='s',mfc='white',mew=1.2,ms=5,ls='--',label='Outer UDP')],
          loc='upper left',ncol=1,fontsize=8,handlelength=3.2,handletextpad=.6,numpoints=1,
          columnspacing=.8,borderpad=.4,borderaxespad=.5)
fig.subplots_adjust(left=.28,right=.965,bottom=.19,top=.97)
save(fig,'communication_ledgers')

fig,(ax,ax_loss)=plt.subplots(1,2,figsize=(3.5,2.85))
d=data['scale'];rate=100*(np.array(d['interval'])-d['exact'])/np.array(d['interval'])
x=np.arange(4)
bars=ax.bar(x,rate,width=.58,color=PRIMARY,edgecolor='black',lw=.5)
ax._categorical_x=True
ax_loss._categorical_x=True
for xp,yp in enumerate(rate):
    ax.annotate(f'{yp:.3f}%',(xp,yp),xytext=(0,3),textcoords='offset points',
                ha='center',va='bottom',fontsize=6.5,rotation=90)
ax.set(xticks=x,xticklabels=d['sources'],ylim=(0,1.5),yticks=np.arange(0,1.51,.3))
ax.set_xlabel('Number of UAV\nsources',fontsize=7.5,labelpad=3)
ax.set_ylabel('Byte reduction (%)',fontsize=7.5,labelpad=1)
ax.text(.5,-.28,'(a) Contract-byte\nreduction',transform=ax.transAxes,
        ha='center',va='top',fontsize=7.5)
# Side-by-side bars retain equal outcomes without hiding either comparator.
w=.29
for j,(vals,color,label) in enumerate([
    (d['loss_interval_percent'],LIGHT_PRIMARY,'Guarded scalar\ninterval'),
    (d['loss_exact_percent'],PRIMARY,'Guarded exact\nsupport')]):
    ax_loss.bar(x+(j-.5)*w,vals,width=w,color=color,edgecolor='black',lw=.5,hatch='///' if j==0 else None,label=label)
ax_loss.set(xticks=x,xticklabels=d['sources'],ylim=(0,.5),yticks=np.arange(0,.51,.1))
ax_loss.set_xlabel('Number of UAV\nsources',fontsize=7.5,labelpad=3)
ax_loss.set_ylabel('Worst-source loss (%)',fontsize=7.5,labelpad=1)
ax_loss.legend(loc='upper left',bbox_to_anchor=(.015,.99),fontsize=6.0,handlelength=1.0,handletextpad=.3,
               labelspacing=.25,borderpad=.35,borderaxespad=.4)
for panel in (ax,ax_loss):panel.tick_params(labelsize=7)
ax_loss.text(.5,-.28,'(b) Worst-source\ntask loss',transform=ax_loss.transAxes,
             ha='center',va='top',fontsize=7.5)
fig.subplots_adjust(left=.145,right=.985,bottom=.30,top=.97,wspace=.8)
save(fig,'scale_relative')

with (HERE/'paired_cost_frontier.csv').open('w',newline='',encoding='utf-8') as f:
    names=['record','budget','loss','reference','penalty','task_gate','saved_contract_B','saved_outer_B','extra_deliveries','extra_cpu_median_ms','extra_cpu_min_ms','extra_cpu_max_ms']
    w=csv.writer(f);w.writerow(names)
    for p in data['pairs']:
        w.writerow([p['case']['record'],p['case']['budget'],p['case']['loss'][0],p['reference'],p['price'],p['task_gate'],p['saved_bytes'],p['saved_outer_bytes'],p['extra_deliveries'],p['extra_cpu_ms'],min(p['extra_cpu_rounds_ms']),max(p['extra_cpu_rounds_ms'])])
if LOCKED_OUTPUTS:
    raise SystemExit('Close the viewer and rerun to replace locked output(s): '+', '.join(LOCKED_OUTPUTS))
print(f'Generated {len(GENERATED)} data figures and all 144 paired rows; system model preserved; no experiment rerun.')
