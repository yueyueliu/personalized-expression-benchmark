import pandas as pd

# 定义列名
column_names = ['gene ID', 'chr', 'TSS position', 'gene name','strand']
path = "/storage/zhangkaiLab/liuyue87/Projects/personalized-expression-benchmark/data/gene_list.csv"
# 读取CSV文件，并指定列名
df = pd.read_csv(path, names=column_names)

# 过滤出 chr=21 的行
chr_21_data = df[df['chr'] == 21]

# 保存过滤后的数据为新的CSV文件
chr_21_data.to_csv('gene_list_demo.csv', index=False)

