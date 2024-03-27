# Plotting grouped dV/dt
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def plot_group_comparison(filenames, labels, colors, output_path, strain):
    fig, ax = plt.figure(figsize=(12, 8)), plt.gca()
    plt.title(f"Phase Plot Comparison for {strain}", fontsize=18)
    plt.xlabel("Voltage (mV)", fontsize=14)
    plt.ylabel("dv/dt (mV/ms)", fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    for i, (file_group, label) in enumerate(zip(filenames, labels)):
        datasets = [pd.read_csv(file) for file in file_group]

        # Check if datasets are empty
        if not datasets or not all('voltage' in d and 'dv_dt' in d for d in datasets):
            continue

        all_voltages = np.array([data['voltage'].values for data in datasets])
        all_dv_dt = np.array([data['dv_dt'].values for data in datasets])

        # Check if all_voltages and all_dv_dt are not empty
        if all_voltages.size == 0 or all_dv_dt.size == 0:
            continue

        mean_voltages = np.mean(all_voltages, axis=0)
        mean_dv_dt = np.mean(all_dv_dt, axis=0)
        sem_dv_dt = stats.sem(all_dv_dt, axis=0)
        ci_95 = 1.96 * sem_dv_dt

        ax.plot(mean_voltages, mean_dv_dt, color=colors[i], label=f'{label} Mean')
        ax.fill_between(mean_voltages, mean_dv_dt - ci_95, mean_dv_dt + ci_95, color=colors[i], alpha=0.3)

    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
    fig.savefig(f"{output_path}/Grouped_PhasePlot_{strain}.png", dpi=300)


def process_directory_for_strain_comparison(directory_path, output_path):
    # List all CSV files in the directory
    all_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.csv')]

    # Process for each strain
    for strain in ['B6M', 'CD1M']:
        wt_files = [file for file in all_files if strain in file and 'WT' in file]
        het_files = [file for file in all_files if strain in file and 'HET' in file]

        if wt_files or het_files:
            plot_group_comparison([wt_files, het_files], labels=['WT', 'HET'], colors=['blue', 'red'], output_path=output_path, strain=strain)

# Example usage with a directory path and output path
# Replace 'your_directory_path' and 'your_output_path' with the actual paths
process_directory_for_strain_comparison(PhasePlot_BatchExport_path, Output_path)


# Plot InputOutput
import numpy as np
import scipy.stats as stats

# Function to calculate mean and SEM for avg_rate
def calculate_mean_and_sem(data):
    avg_rate_data = data.filter(like='avg_rate')
    mean = avg_rate_data.mean(axis=1)
    sem = stats.sem(avg_rate_data, axis=1, nan_policy='omit')
    return mean, sem

# Calculating mean and SEM for B6M_500ms_WT and B6M_500ms_HET
b6m_500ms_wt_mean, b6m_500ms_wt_sem = calculate_mean_and_sem(b6m_500ms_wt_sheet)
b6m_500ms_het_mean, b6m_500ms_het_sem = calculate_mean_and_sem(b6m_500ms_het_sheet)

# Assuming the 'current_step' columns are consistent across the dataset and can be used for the x-axis
current_step_wt = b6m_500ms_wt_sheet[b6m_500ms_wt_sheet.columns[b6m_500ms_wt_sheet.columns.str.contains('current_step')]].iloc[:, 0]
current_step_het = b6m_500ms_het_sheet[b6m_500ms_het_sheet.columns[b6m_500ms_het_sheet.columns.str.contains('current_step')]].iloc[:, 0]

# Plotting the data with SEM error bars
plt.figure(figsize=(12, 8))
plt.errorbar(current_step_wt, b6m_500ms_wt_mean, yerr=b6m_500ms_wt_sem, color='blue', label='B6M 500ms WT', fmt='-o')
plt.errorbar(current_step_het, b6m_500ms_het_mean, yerr=b6m_500ms_het_sem, color='red', label='B6M 500ms HET', fmt='-o')
plt.title('Comparison of B6M 500ms WT and B6M 500ms HET with SEM')
plt.xlabel('Current Step')
plt.ylabel('Average Rate')
plt.legend()
plt.grid(True)
plt.show()

