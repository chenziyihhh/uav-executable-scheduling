"""Reproduce single-column communication/CPU bars from unchanged CSV data."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from figure_palette import PRIMARY, SECONDARY, LIGHT_PRIMARY, SECONDARY_EDGE
P=Path(__file__).parent
rows=list(csv.DictReader((P/"operating_conditions.csv").open(encoding="utf8")))
blue=PRIMARY;pale=LIGHT_PRIMARY;orange=SECONDARY
plt.rcParams.update({"font.family":"serif","font.serif":["Times New Roman"],
    "mathtext.fontset":"stix","font.size":8,"axes.labelsize":9,
    "xtick.labelsize":8,"ytick.labelsize":8,"legend.fontsize":7.5,
    "pdf.fonttype":42,"axes.linewidth":.85})
fig,ax=plt.subplots(figsize=(3.5,3.25))
cpu=ax.twinx()
x=np.arange(len(rows));width=.23
b1=ax.bar(x-width,[float(r["mean_saved_B"]) for r in rows],width,
          color=blue,edgecolor=blue,label="Mean saved bytes (left)")
b2=ax.bar(x,[float(r["worst_saved_B"]) for r in rows],width,
          color=pale,edgecolor=blue,hatch="///",label="Worst saved bytes (left)")
b3=cpu.bar(x+width,[float(r["CPU_median_ms"]) for r in rows],width,
           color=orange,edgecolor=SECONDARY_EDGE,hatch="..",label="Median extra CPU (right)")
ax.set_ylim(-300,600);cpu.set_ylim(-150,300)
ax.set_yticks(np.arange(-300,601,150));cpu.set_yticks(np.arange(-150,301,75))
ax.axhline(0,color=".35",lw=.8)
ax.set_xticks(x,[str(r["budget_Bps"])+"\n"+format(float(r["loss"]),"g") for r in rows])
ax.set_xlabel("Budget (B/s) / loss probability")
ax.set_ylabel("Saved contract bytes (B)",color=blue)
cpu.set_ylabel("Extra session CPU (ms)",color=orange)
ax.tick_params(which="both",direction="in",top=False,right=False)
cpu.tick_params(axis="y",which="both",left=False,right=False,labelcolor=orange)
ax.tick_params(axis="y",labelcolor=blue)
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
cpu.yaxis.set_minor_locator(AutoMinorLocator(2))
ax.set_xlim(-.55,3.55)
leg=cpu.legend(handles=[b1,b2,b3],loc="upper right",framealpha=1,
               fancybox=False,borderpad=.45,labelspacing=.35)
leg.get_frame().set_edgecolor("black");leg.get_frame().set_linewidth(.6)
fig.subplots_adjust(left=.18,right=.82,bottom=.20,top=.97)
fig.savefig(P/"operating_conditions.pdf")
fig.savefig(P/"operating_conditions.png",dpi=300)
plt.close(fig)
print("Updated single-column grouped bars; original data preserved.")
