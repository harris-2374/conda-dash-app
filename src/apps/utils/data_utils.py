import pandas as pd
import plotly

def check_input_columns(cols):
    expected = {
        'Chromosome': str,
        'Window': int,
        'NewickTree': str,
        'TopologyID': str,
    }
    final_cols = []
    # Double check standard column names, change if wrong
    for key, value, col in zip(expected.keys(), expected.values(), cols[:4]):
        try:
            assert type(col) == value
            assert col == key
            final_cols.append(col)
        except AssertionError:
            final_cols.append(key)
    # Add additional data column names
    if len(cols[4:]) == 0:
        final_cols.append('None')
    for c in cols[4:]:
        final_cols.append(c)
    return final_cols


def build_file_json(file=None):
    """
    Load in file depending on file type, return pandas DataFrame in json format
    """
    # Identify file type and open accordingly
    if file.suffix == '.csv':
        open_file = pd.read_csv(file, sep=',')
        cols = check_input_columns(open_file.columns.to_list())
        if "None" in cols:
            open_file['None'] = [0]*len(open_file)
        open_file.columns = cols
        open_file.sort_values(by=[cols[0], cols[2]], inplace=True) # sort by chromosome and topology #
        return open_file.to_json()
    elif file.suffix == '.xlsx':
        open_file = pd.read_excel(file, engine='openpyxl')
        cols = check_input_columns(open_file.columns.to_list())
        print(cols)
        if "None" in cols:
            open_file['None'] = [0]*len(open_file)
        open_file.columns = cols
        open_file.sort_values(by=[cols[2]], inplace=True)
        open_file.reset_index(drop=True, inplace=True)
        return open_file.to_json()
    elif file.suffix == '.bed':
        open_file = pd.read_csv(file, sep='\t', names=["Chromosome", "Start", "Stop"])
        return open_file.to_json()
    elif file.suffix == '.txt':
        open_file = pd.read_csv(file, sep='\t')
        return open_file.to_json()


def build_file_dataframe(file=None):
    """
    Load in file depending on file type, return pandas DataFrame in json format
    """
    # Identify file type and open accordingly
    if file.suffix == '.csv':
        open_file = pd.read_csv(file, sep=',')
        cols = check_input_columns(open_file.columns.to_list())
        if "None" in cols:
            open_file['None'] = [0]*len(open_file)
        open_file.columns = cols
        open_file.sort_values(by=[cols[0], cols[2]], inplace=True) # sort by chromosome and topology
        return open_file
    elif file.suffix == '.tsv':
        open_file = pd.read_csv(file, sep='\t')
        cols = check_input_columns(open_file.columns.to_list())
        if "None" in cols:
            open_file['None'] = [0]*len(open_file)
        open_file.sort_values(by=[cols[0], cols[2]], inplace=True) # sort by chromosome and topology
        return open_file
    elif file.suffix == '.xlsx':
        open_file = pd.read_excel(file, engine='openpyxl')
        cols = check_input_columns(open_file.columns.to_list())
        if "None" in cols:
            open_file['None'] = [0]*len(open_file)
        open_file.columns = cols
        open_file.sort_values(by=[cols[0], cols[1]], inplace=True)
        open_file.reset_index(drop=True, inplace=True)
        return open_file


def newick_semicolon_check(tree_str):
    """
    This function will check the last character of
    the tree in newick form and ensure that is ends in ";".
    """
    if list(tree_str)[-1] != ";":
        tree_str += ';'
        return tree_str
    else:
        return tree_str


def fix_bed_file_chroms(start, stop):
    try:
        chrom_start = int(start)
        chrom_stop = int(stop)
    except:
        chrom_start = str(start).strip(",")
        chrom_stop_comma_split = str(stop).split(",")
        chrom_stop = "".join(chrom_stop_comma_split)
        # Ensure int datatype before return
        chrom_start = int(chrom_start)
        chrom_stop = int(chrom_stop)
    return chrom_start, chrom_stop


def build_file_json_for_data_import(file=None):
    """
    Load in file depending on file type, return pandas DataFrame in json format
    """
    # Identify file type and open accordingly
    if file.suffix == '.csv':
        open_file = pd.read_csv(file, sep=',')
        # open_file.sort_values(by=["topology"], inplace=True)
        return open_file
    elif file.suffix == '.xlsx':
        open_file = pd.read_excel(file, engine='openpyxl')
        open_file.sort_values(by=["topology"], inplace=True)
        open_file.reset_index(drop=True, inplace=True)
        return open_file
    elif file.suffix == '.bed':
        open_file = pd.read_csv(file, sep='\t', names=["Chromosome", "Start", "Stop"])
        return open_file
    elif file.suffix == '.txt':
        open_file = pd.read_csv(file, sep='\t')
        return open_file


def output_dataframe_based_on_filetype(dataframe, output_file=None):
    """
    Load in file depending on file type, return pandas DataFrame in json format
    """
    # Identify file type and open accordingly
    if output_file.suffix == '.csv':
        dataframe.to_csv(output_file, sep=',', index=False)
        # open_file.sort_values(by=["topology"], inplace=True)
        return 
    elif output_file.suffix == '.xlsx':
        dataframe.to_csv(output_file, sep=',', index=False)
        return 
    elif output_file.suffix == '.bed':
        dataframe.to_csv(output_file, sep='\t', index=False)
        return 
    elif output_file.suffix == '.txt':
        dataframe.to_csv(output_file, sep='\t', index=False)
        return 


