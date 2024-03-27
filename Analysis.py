file_list = glob.glob(os.path.join(folder_path, "*.abf"))
# compiled_indiv = pd.DataFrame()
# compiled_stfx = pd.DataFrame()
rheobase_spike_stats = pd.DataFrame()
rheobase_list = pd.DataFrame()
for file in file_list:
    abf_file = parse_file_name(file)
    if abf_file.stiprotocal not in ["1000ms", "500ms"]:
      continue
    current_file, rheobase = spike_analysis1(abf_file)
    # compiled_indiv = pd.concat([compiled_indiv, current_file])
    rheobase_sweep = current_file[current_file['sweep'] == rheobase]
    info = rheobase_sweep.iloc[0][['date', 'backgrounds', 'genotype', 'age', 'slice_Num', 'cell_Num', 'stiprotocal', 'record_Num']]
    mean_data = rheobase_sweep[['threshold_v', 'width', 'amplitude', 'rise_time', 'fall_time', 'upstroke_downstroke_ratio']].mean()
    combined = pd.concat([info, mean_data])
    rheo = pd.Series([current_file[current_file['sweep'] == rheobase].iloc[0]['peak_i']], name = 'rheobase')
    r = pd.concat([info.T, rheo])
    rheobase_list = pd.concat([rheobase_list, r], axis = 1)
    rheobase_spike_stats = pd.concat([rheobase_spike_stats, combined], axis = 1)
    # compiled_stfx = pd.concat([compiled_stfx, stfx_file])
    phase_plots(file, rheobase)
rheobase_list.to_csv(f"{Output_path}/Rheobase_list.csv")
