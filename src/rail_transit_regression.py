"""轨道交通线路长度与城市指标的幂函数回归分析。"""

from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict

def fit_power_law_regression(
    data: pd.DataFrame,
    length_col: str,
    population_col: str = "人口",
    area_col: str = "面积",
    gdp_col: str = "GDP",
) -> Dict[str, float]:
    """估计公式 L = b0 * P^b1 * S^b2 * G^b3 中的四个回归系数。

    参数:
        data: pandas 读取后的城市数据表，每一行是一个城市。
        length_col: 轨道交通长度列名，对应公式中的 L。
            例如："地铁长度"、"市域快轨"、"有轨电车"。
        population_col: 人口列名，对应公式中的 P。
        area_col: 面积列名，对应公式中的 S。
        gdp_col: GDP 列名，对应公式中的 G。

    返回:
        {"b0": 数值, "b1": 数值, "b2": 数值, "b3": 数值,
         "R2": 数值, "调整R2": 数值}

    异常:
        ValueError: 列不存在、数据无法转换为数值、样本量不足或存在非正数、
        非有限数值时抛出。
    """
    required_columns = [population_col, area_col, gdp_col, length_col]
    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        raise ValueError(f"数据表中缺少列: {', '.join(missing_columns)}")

    try:
        #将读取的数据转化为数值类型
        numeric_data = data[required_columns].apply(pd.to_numeric, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("四个指定列中的数据必须能够转换为数值") from exc

    # 删除有空值的行，你数据都补全，无法进行统计分析
    complete_data = numeric_data.dropna()
    #判断清晰后的数据的数据量能否进行回归分析
    if len(complete_data) <= 4:
        raise ValueError("删除缺失值后至少需要 5 组样本才能计算调整 R2")

    #将Series对象转化为ndarray类型的数组对象
    arrays = {
        "population": complete_data[population_col].to_numpy(),
        "area": complete_data[area_col].to_numpy(),
        "gdp": complete_data[gdp_col].to_numpy(),
        "length": complete_data[length_col].to_numpy(),
    }
    for name, values in arrays.items():
        if np.any(~np.isfinite(values)) or np.any(values <= 0):
            raise ValueError(f"列 {required_columns[list(arrays).index(name)]} 的数据必须为有限正数")

    # 幂函数两边取自然对数后，转化为线性最小二乘问题：
    # ln(L) = ln(b0) + b1*ln(P) + b2*ln(S) + b3*ln(G)
    # 将行向量按列拼接成矩阵
    design_matrix = np.column_stack(
        (
            np.ones(len(complete_data)),
            np.log(arrays["population"]),
            np.log(arrays["area"]),
            np.log(arrays["gdp"]),
        )
    )
    #本质利用矩阵乘法进行回归分析，取返回的元组的第0个元素，当中返回回归分析模拟出的参数[ln(b0),b1,b2,b3]
    coefficients = np.linalg.lstsq(design_matrix, np.log(arrays["length"]), rcond=None)[0]

    # R2和调整R2都在对数变换后的线性回归中计算。
    log_length = np.log(arrays["length"])
    fitted_log_length = design_matrix @ coefficients
    residual_sum_squares = np.sum((log_length - fitted_log_length) ** 2)
    total_sum_squares = np.sum((log_length - np.mean(log_length)) ** 2)
    if total_sum_squares == 0:
        raise ValueError("因变量完全相同，无法计算 R2")

    r2 = 1 - residual_sum_squares / total_sum_squares
    adjusted_r2 = 1 - (1 - r2) * (len(complete_data) - 1) / (
        len(complete_data) - design_matrix.shape[1]
    )

    return {
        "b0": float(np.exp(coefficients[0])),
        "b1": float(coefficients[1]),
        "b2": float(coefficients[2]),
        "b3": float(coefficients[3]),
        "R2": float(r2),
        "调整R2": float(adjusted_r2),
    }

#这个函数是为了将对DF对象当中的每列调用fit_power_law_regression函数，然后将输出一个DF对象，将分析结果保存在当中
def analyze_all_modes(data: pd.DataFrame) -> pd.DataFrame:
    """对地铁、市域快轨、有轨电车三种制式分别进行回归分析。"""
    #定义xls文件中行标题与csv当中数据列标题的映射字典
    mode_columns = {
        "地铁": "地铁长度",
        "市域快轨": "市域快轨",
        "有轨电车": "有轨电车",
    }

    results = []
    for mode_name, length_col in mode_columns.items():
        coefficients = fit_power_law_regression(
            data,
            length_col=length_col,
            population_col="人口",
            area_col="面积",
            gdp_col="GDP",
        )

        if coefficients["调整R2"] >= 0.7:
            fit_quality = "拟合较好"
        elif coefficients["调整R2"] >= 0.5:
            fit_quality = "拟合中等"
        elif coefficients["调整R2"] >= 0.3:
            fit_quality = "拟合偏弱"
        elif coefficients["调整R2"] >= 0:
            fit_quality = "拟合较弱"
        else:
            fit_quality = "拟合很差，低于均值基准"

        meaning = (
            f"基于对数里程回归，模型解释了 {coefficients['R2']:.1%} 的变异，"
            f"调整后为 {coefficients['调整R2']:.1%}，{fit_quality}"
        )

        #这里**coefficients参数的含义是将字典中的键值对当中元素写到另外一个字典当中
        results.append({"轨道交通制式": mode_name, **coefficients, "含义": meaning})

    result_table = pd.DataFrame(results).set_index("轨道交通制式")
    result_table.index.name = "轨道交通制式"
    return result_table

#负责将analyze_all_modes分析汇总后得到的结果写入指定文件路径下
def export_regression_results(
    results: pd.DataFrame,
    output_path: Path,
) -> None:
    """将回归分析结果保存为 Excel 表格。"""
    output_path = Path(output_path)
    #创建文件所在文件夹和自身文件
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_excel(output_path, index=True)


if __name__ == "__main__":
    data_file = Path(__file__).resolve().parents[1] / "data" / "city_rail_transit_data.csv"
    output_file = Path(__file__).resolve().parents[1] / "outputs" / "coefficient_res.xlsx"
    '''
    1.Path(__file__).resolve()获取当前文件的绝对路径
    2.parents[1]找当前文件的父目录
    3.直接进行路径的拼接找到想要读取的文件的绝对路径
    '''
    #读取csv数据，获取DF对象
    city_data = pd.read_csv(data_file)

    #调用analyze_all_modes方法，对所有制式进行回归分析S
    result_table = analyze_all_modes(city_data)

    #保存回归分析结果到指定文件中
    export_regression_results(result_table, output_file)

    print(result_table.round(6).to_string())
    print(f"结果已保存到: {output_file}")
