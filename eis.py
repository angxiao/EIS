import pandas as pd

class EISData:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self._load_data()
        self.new_df = self._process_dataframe()
        
    def _load_data(self):
        df = pd.read_csv(self.file_path, delimiter='\t')
        
        # Ensure columns are formatted properly
        for col in df.columns:
            if "cycle number" in col.lower():
                df.rename(columns={col: "cycle number"}, inplace=True)
            if "Re" in col:
                df.rename(columns={col: "Re"}, inplace=True)
            if "Im" in col:
                df.rename(columns={col: "Im"}, inplace=True)
        return df
    
    def _process_dataframe(self):
        # Extracting and processing 'Re' column
        grouped_re = self.df.groupby('cycle number')['Re'].apply(list).reset_index()
        new_df_re = pd.DataFrame(grouped_re['Re'].values.tolist())
        new_df_re.columns = [f'Re_{i+1}' for i in range(new_df_re.shape[1])]
        
        # Extracting and processing 'Im' column
        grouped_im = self.df.groupby('cycle number')['Im'].apply(list).reset_index()
        new_df_im = pd.DataFrame(grouped_im['Im'].values.tolist())
        new_df_im.columns = [f'Im_{i+1}' for i in range(new_df_im.shape[1])]
        
        # Combine the results and add 'cycle number'
        new_df = pd.concat([grouped_re['cycle number'], new_df_re, new_df_im], axis=1)
        
        return new_df
    
    def get_cycle_numbers(self):
        return self.new_df['cycle number'].tolist()
    
    def get_EIS_data_for_cycle(self, cycle_number):
        row = self.new_df[self.new_df['cycle number'] == cycle_number]
        if not row.empty:
            return row.drop(columns=['cycle number']).values.flatten().tolist()
        else:
            print(f"No data found for cycle number: {cycle_number} in {self.file_path}")
            return []