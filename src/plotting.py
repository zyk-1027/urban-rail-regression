import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from pathlib import Path
from matplotlib.patches import Patch   #导入Patch类，用于生成矩形补丁，用于画图例
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

rcParams['font.sans-serif'] = ['Microsoft YaHei']
rcParams['font.size'] = 13
rcParams["figure.titlesize"] = 15
rcParams['axes.titlesize'] = 13
plt.rcParams["axes.titleweight"] = "bold"

#画不同轨道交通制式模拟分析样本点数量的柱状图.png
x = range(3)
y = [39,21,16]

plt.figure(figsize=(10,6),dpi=80)

bars = plt.bar(x,y,width=0.4,color=["#2F6FBA","#E8833A","#4C9F70"])

#给每个柱子上添加对应的样本点数量
for bar in bars:
    height = bar.get_height()
    plt.text(
       bar.get_x()+bar.get_width()/2,
        height,
        s=f'{height}',
        ha='center',
        va='bottom',
        fontsize=13
    )


xticks = ['地铁','市域快轨','有轨电车']

plt.xticks(x,xticks)

plt.xlabel(xlabel='轨道交通制式')
plt.ylabel(ylabel='回归分析可用样本点')
plt.title(label='不同轨道交通制式进行模拟分析的样本点数量')

plt.tight_layout()

#创建补丁对象集合
legend_handles  = [
    Patch(facecolor="#2F6FBA",label=xticks[0]),
    Patch(facecolor="#E8833A",label=xticks[1]),
    Patch(facecolor="#4C9F70",label=xticks[2]),
]

plt.legend(handles=legend_handles,title='轨道交通制式')

plt.savefig(fname=PROJECT_ROOT /'outputs'/'figures'/'不同轨道交通制式模拟分析样本点数量的柱状图.png')

#画不同轨道交通系数对比图
coefs_df = pd.read_excel(PROJECT_ROOT / "outputs" / "coefficient_res.xlsx")

coefs_df.set_index('轨道交通制式',inplace=True)

xticks = ['人口弹性\nb1','面积弹性\nb2','GDP弹性\nb3']
modes = ['地铁','市域快轨','有轨电车']
coef_cols = ["b1","b2","b3"]

#设置每种制式的字体，采用字典映射的方式
colors = {
    "地铁":"#2F6FBA",
    "市域快轨":"#E8833A",
    '有轨电车':"#4C9F70"
}

x = np.arange(len(modes))
width = 0.28

plt.figure(figsize=(10,6),dpi=80)

#分组制图
for i,mode in enumerate(modes):
    #将Series类型的对象转化为数组，数组当中保存的数据类型设置为float类型
    values = coefs_df.loc[mode,coef_cols].to_numpy(dtype=float)
    bars = plt.bar(
        x+(i-1)*width,
        values,
        width,
        color=colors[mode],
        label=mode
    )
    #给每个柱子设置标签，fmt设置格式化字符串的格式，padding设置文字与柱状图顶部的距离
    plt.bar_label(bars,fmt='%.2f',padding=3,fontsize=13)

#画位置高度为0的水平位置参考线
plt.axhline(0, color='black', linestyle='--',alpha=0.7)

plt.xticks(x,xticks)

plt.xlabel(xlabel='回归参数')
plt.ylabel(ylabel='回归参数值')
plt.title(label='不同轨道交通制式回归系数对比')

plt.legend(title="不同轨道交通制式")

#通过axis参数只显示对应轴线上的网格
plt.grid(axis='y',linestyle='--',alpha=0.3)

plt.ylim(-1.5,1.8)  #设置y轴的可显示界限范围

plt.tight_layout()

plt.savefig(fname=PROJECT_ROOT /'outputs'/'figures'/'不同轨道交通制式回归系数对比.png')


