import pandas as pd

class CapacityData:
    def __init__(self, file_path, eol = None):
        self.file_path = file_path
        self.eol = eol
        self.df = self._load_data()
        self.cell_number = self._extract_cell_number()
        self.rul, self.capacity, self.cycle_number, self.capacity_retention = self._extract_capacity()

    def _load_data(self):
        df = pd.read_csv(self.file_path, delimiter='\t')
        
        # Ensure 'cycle number' and 'capacity' is formatted properly
        for col in df.columns:
            if "cycle number" in col:
                df.rename(columns={col: "cycle number"}, inplace=True)
            if "Capacity" in col:
                df.rename(columns={col: "Capacity/mA.h"}, inplace=True)        
        
        # Rename columns based on their presence
        if "Unnamed: 3" in df.columns:
            df.rename(columns={"Unnamed: 3": "capacity (mAh)"}, inplace=True)
        elif "Capacity/mA.h" in df.columns:
            df.rename(columns={"Capacity/mA.h": "capacity (mAh)"}, inplace=True)

        # Extract the last row for each cycle number
        df = df.groupby("cycle number").last().reset_index()
        df['capacity retention'] = df['capacity (mAh)'] / df['capacity (mAh)'].iloc[0]

        if self.eol and not df[df['capacity retention'] < self.eol].empty:
            # Find the index of the first occurrence where 'capacity retention' is less than 0.8
            index = df[df['capacity retention'] < self.eol].index[0]
            # Filter out all rows below this index
            df = df[df.index < index]
        
        df['rul'] = df['cycle number'].max() - df['cycle number']
        
        return df

    def _extract_cell_number(self):
        return self.file_path.split("/")[-1].split("_")[2].split(".")[0]
    
    def _extract_capacity(self):
        rul = self.df['rul']
        capacity = self.df['capacity (mAh)']
        cycle_number = self.df['cycle number']
        capacity_retention = self.df['capacity retention']
        return rul, capacity, cycle_number, capacity_retention
    
    def get_capacity(self):
        metrics = {
            'Cell Number': self.cell_number,
            'RUL': self.rul,
            'Capacity': self.capacity,
            'Cycle Number': self.cycle_number,
            'Capacity Retention': self.capacity_retention
        }
        return metrics