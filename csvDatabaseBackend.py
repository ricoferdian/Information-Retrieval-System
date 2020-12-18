import pandas as pd

def export_feature_csv(feature_dict):
    df = pd.DataFrame(feature_dict)
    df.to_csv('feature_database.csv', index=False)

def import_feature_csv():
    df = pd.read_csv('feature_database.csv')
    return df