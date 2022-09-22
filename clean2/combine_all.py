import pandas as pd
from pathlib import Path

path = Path('../data/predicted_data/ptt/')
csv_file = [data for data in path.iterdir()]

df = pd.DataFrame()

for data_path in csv_file:
    data = pd.read_csv(data_path)
    data.insert(0, 'date', data_path.stem)
    df = pd.concat([df, data], ignore_index=True)

df2 = pd.get_dummies(df.label)
df2.columns = ['label_0', 'label_1', 'label_2']  # type: ignore
df = pd.concat([df, df2], axis=1)
df = df[['date', 'label_0', 'label_1', 'label_2']]
df_final = df.groupby('date').sum().reset_index()
stock_df = pd.read_csv(f'{path}/../../TAIEX.csv')
all_df = pd.merge(df_final,
                  stock_df,
                  left_on="date",
                  right_on="Date",
                  how='left').drop('Date', axis=1)
all_df = all_df[[
    'date', 'label_0', 'label_1', 'label_2', 'Close', 'points', 'status'
]]
all_df.to_csv("total.csv")