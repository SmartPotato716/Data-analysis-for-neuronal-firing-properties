# Organize the Rheobase Spike Stats
rheobase_spike_stats_T = rheobase_spike_stats.T
# Identify and separate the data based on genotype
genotype_wt_data = rheobase_spike_stats_T[rheobase_spike_stats_T['genotype'] == 'WT']
genotype_het_data = rheobase_spike_stats_T[rheobase_spike_stats_T['genotype'] == 'HET']

# Prepare the Excel file with two sheets
new_excel_file_path = f"{Output_path}/categorized_rheobase_spike_stats.xlsx"
with pd.ExcelWriter(new_excel_file_path) as writer:
    genotype_wt_data.to_excel(writer, sheet_name='WT')
    genotype_het_data.to_excel(writer, sheet_name='HET')

# Return the path to the new Excel file
new_excel_file_path

import glob
import pandas as pd

exported_folder_path = InputOutput_BatchExport_path
csv_files = glob.glob(os.path.join(exported_folder_path, "*.csv"))
csv_output_path = f"{Output_path}/Categorized_InputOut.xlsx"

data_by_background_stiprotocal_genotype = {}

for csv_file in csv_files:
    csv_data = pd.read_csv(csv_file)
    background_value = csv_data['backgrounds'].iloc[0]  # Extracting background value
    stiprotocal_value = csv_data['stiprotocal'].iloc[0]
    genotype_value = csv_data['genotype'].iloc[0]

    csv_identifier = csv_file.split('/')[-1].split('.')[0]
    extracted_data = csv_data[['current step', 'average_rate']].rename(columns={
        'current step': f'current_step_{csv_identifier}',
        'average_rate': f'avg_rate_{csv_identifier}'
    })

    # Create nested dictionary structure
    if background_value not in data_by_background_stiprotocal_genotype:
        data_by_background_stiprotocal_genotype[background_value] = {}
    if stiprotocal_value not in data_by_background_stiprotocal_genotype[background_value]:
        data_by_background_stiprotocal_genotype[background_value][stiprotocal_value] = {}
    if genotype_value not in data_by_background_stiprotocal_genotype[background_value][stiprotocal_value]:
        data_by_background_stiprotocal_genotype[background_value][stiprotocal_value][genotype_value] = extracted_data
    else:
        data_by_background_stiprotocal_genotype[background_value][stiprotocal_value][genotype_value] = pd.merge(
            data_by_background_stiprotocal_genotype[background_value][stiprotocal_value][genotype_value],
            extracted_data,
            left_index=True, right_index=True, how='outer'
        )

with pd.ExcelWriter(csv_output_path) as writer:
    for background, stiprotocals_data in data_by_background_stiprotocal_genotype.items():
        for stiprotocal, genotypes_data in stiprotocals_data.items():
            for genotype, data in genotypes_data.items():
                sheet_name = f"{background}_{stiprotocal}_{genotype}"
                data.to_excel(writer, sheet_name=sheet_name, index=False)
