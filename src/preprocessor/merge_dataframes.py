import pandas as pd
import os
from glob import glob

data_dir = "data/output/preprocessed/final"

df_ls = []
for file in glob(data_dir + '/**.csv'):
    df = pd.read_csv(file)
    df_ls.append(df)

df_merged = pd.concat(df_ls)

print(len(df_merged))  # 3125141

df_dedup = df_merged.drop_duplicates(subset=["id"])


print(len(df_dedup))  # 2724340
df_dedup.to_csv(data_dir+'/all.csv', index=False)
