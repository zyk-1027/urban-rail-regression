# 城市轨道交通规模影响因素回归分析

本项目使用中国城市的人口、面积和 GDP 数据，对城市轨道交通线路长度进行幂函数回归分析。分析对象包括地铁、市域快轨和有轨电车三种制式，并输出回归系数、拟合优度、Excel 结果表和对比图。

## 项目结构

```text
urban-rail-analysis/
├── data/
│   └── city_rail_transit_data.csv     # 城市基础指标与轨道交通长度数据
├── outputs/
│   ├── coefficient_res.xlsx           # 三种制式的回归分析结果
│   └── figures/                       # 回归相关图表
├── src/
│   ├── rail_transit_regression.py     # 回归建模与结果导出
│   └── plotting.py                    # 结果可视化
├── .gitignore
├── README.md
└── requirements.txt                   # Python 依赖清单
```

## 数据说明

`data/city_rail_transit_data.csv` 共包含 54 个城市、7 个字段：

| 字段 | 含义 |
| --- | --- |
| 城市 | 城市名称 |
| 人口 | 城市人口指标 |
| 面积 | 城市面积指标 |
| GDP | 城市 GDP 指标 |
| 地铁长度 | 地铁线路长度 |
| 市域快轨 | 市域快轨线路长度 |
| 有轨电车 | 有轨电车线路长度 |

三种轨道交通制式的有效样本量分别为地铁 39 个、市域快轨 21 个、有轨电车 16 个。回归分析会自动删除对应字段存在缺失值的样本。

## 分析方法

项目假设轨道交通线路长度与城市指标之间存在幂函数关系：

```text
L = b0 * P^b1 * S^b2 * G^b3
```

其中，`L` 为轨道交通线路长度，`P` 为人口，`S` 为面积，`G` 为 GDP。对公式两边取自然对数后，使用普通最小二乘法估计 `b0`、`b1`、`b2` 和 `b3`，并在对数变换后的线性模型中计算 `R2` 和调整 `R2`。

## 环境准备

建议使用 Python 3.9 或更高版本。

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 运行方式

先在项目根目录执行回归分析：

```bash
python src/rail_transit_regression.py
```

然后执行绘图脚本：

```bash
python src/plotting.py
```

运行完成后，结果会写入：

- `outputs/coefficient_res.xlsx`
- `outputs/figures/不同轨道交通制式模拟分析样本点数量的柱状图.png`
- `outputs/figures/不同轨道交通制式回归系数对比.png`

## 结果概览

| 轨道交通制式 | 有效样本量 | R2 | 调整 R2 | 拟合判断 |
| --- | ---: | ---: | ---: | --- |
| 地铁 | 39 | 0.7626 | 0.7423 | 拟合较好 |
| 市域快轨 | 21 | 0.0643 | -0.1009 | 拟合很差，低于均值基准 |
| 有轨电车 | 16 | 0.1474 | -0.0658 | 拟合很差，低于均值基准 |

完整系数请查看 `outputs/coefficient_res.xlsx`。本项目的回归结果用于描述样本数据中的统计关系，不能直接解释为因果关系。

## 注意事项

- 图表默认使用 `Microsoft YaHei` 中文字体。如果系统没有该字体，请在 `src/plotting.py` 中修改 `rcParams["font.sans-serif"]`。
- 如需替换数据，请保持 CSV 文件的列名不变，或同步修改脚本中的列名参数。
