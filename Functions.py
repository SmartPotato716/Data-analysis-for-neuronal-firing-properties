def dv_dt (abf, sweep, sampling_rate, half_window_ms):
    # Select the trace in your recording
    sweep = abf.setSweep(sweepNumber=sweep, channel=0)
    # Identify the action potential with highest dV
    dv = np.diff(abf.sweepY)
    dv_max = np.argmax(dv)
    # Set the time window for the selected action potential
    sampling_rate = sampling_rate
    half_window_ms = half_window_ms
    half_window = (half_window_ms * sampling_rate)//1000
    global t_window
    t_window = abf.sweepX[dv_max-half_window:dv_max+half_window]
    v_window = abf.sweepY[dv_max-half_window:dv_max+half_window]
    # Calculate dv_dt for the selected action potential
    dv_ap = np.diff(v_window)
    dt_ap = np.diff(t_window*1000)
    dv_dt = (dv_ap)/(dt_ap)
    dv_dt_max = np.amax(dv_dt)
    # Remove the first v value to match the dv/dt array which is n-1
    v_ap_array = np.delete(v_window, 1)
    # Return the selected outputs from the function
    return {'voltage': v_window, 'dv_dt': dv_dt,
            'dv_dt_max': dv_dt_max, 'time': t_window,
            'voltage_array': v_ap_array}

from IPython.core import compilerop
from sys import breakpointhook
from IPython.lib.security import passwd
def spike_analysis1(abf_file: AbfFile):
  name = str(abf_file)
  print(abf_file.file_name)

  ## Initial Variables
  rheobase_sweep = None
  abf = pyabf.ABF(abf_file.full_path)
  dataframe = []
  currents = []
  stfx_table = pd.DataFrame()
  # print (abf)
  abf.setSweep(0)
  # start = None
  ## Read the first sweep
  time = abf.sweepX
  voltage = abf.sweepY
  current = abf.sweepC
  ## Set the time window for analysis
  for t in time:
    if t > 0.1:
      start = t
      break
  for t in time:
    if t > 1.1:
      end = t
      break

  ## loop through the sweeps
  for sweepnumber in abf.sweepList:
        # Set a break point of analysis
    if rheobase_sweep == None:
      pass
    elif sweepnumber > rheobase_sweep + 20:
      break

    abf.setSweep(sweepnumber)
    time = abf.sweepX
    voltage = abf.sweepY
    current = abf.sweepC
    # Read the Current Data
    t1 = int(300*abf.dataPointsPerMs)
    t2 = int(400*abf.dataPointsPerMs)
    current_mean = np.average(abf.sweepC[t1:t2])
    currents.append(np.average(abf.sweepC[t1:t2]))

    # Set up parameters for spike analysis
    sfx = SpikeFeatureExtractor(start, end, filter = None,
                                dv_cutoff = 20, thresh_frac = 0.05,
                                min_peak=0, max_interval = 0.05)
    # Analyze the sweep
    sfx_results = sfx.process (time, voltage, current)
    # See if it is rheobase

    current = {
        'date': abf_file.date,
        'backgrounds': abf_file.backgrounds,
        'genotype': abf_file.genotype,
        'age': abf_file.age,
        'slice_Num': abf_file.slice_num,
        'cell_Num': abf_file.cell_num,
        'stiprotocal': abf_file.stiprotocal,
        'record_Num': abf_file.record_num,
      }
    current = pd.DataFrame([current])

    if not sfx_results.empty:
      if rheobase_sweep == None:
        rheobase_sweep = sweepnumber
      else: pass

      # num_rows are the number of Aps in each sweep!
      # Spike Feature Write in
      num_rows = sfx_results.shape[0]

      # print (num_rows)
      current1 = pd.concat([current] * num_rows, ignore_index = True)
      mylist = [sweepnumber] * num_rows
      sweepcolumn = pd.Series(mylist, name = "sweep")
      file_list = [name] * num_rows
      filenamecolumn = pd.Series(file_list, name = "filename")
      rise_time = pd.Series(sfx_results['peak_t']-sfx_results['threshold_t'], name = 'rise_time')
      fall_time = pd.Series(sfx_results['trough_t']-sfx_results['peak_t'], name = 'fall_time')
      amplitude = pd.Series(sfx_results['peak_v']-sfx_results['trough_v'], name = 'amplitude')
      new_frame = pd.concat([current1, filenamecolumn, sweepcolumn, sfx_results, rise_time, fall_time, amplitude], axis = 1)
      dataframe.append(new_frame)
      indiv_table = pd.concat(dataframe)


    ## Spike Train Analysis
    stfx = SpikeTrainFeatureExtractor(start, end)
    stfx_results = stfx.process(time, voltage, current, sfx_results)
    # Read out the stfx data
    length = len(stfx_table)
    stfx_table.loc[length, 'current step'] = current_mean
    stfx_table.loc[length, 'average_rate'] = stfx_results["avg_rate"]
    for col in current.columns:
      stfx_table.loc[length, col] = current[col].values[0]
    if stfx_results['avg_rate'] > 0:
      stfx_table.loc[length, 'adaptation'] = stfx_results ["adapt"]
      stfx_table.loc[length, 'Latency_s'] = stfx_results ["latency"]
      stfx_table.loc[length, 'ISI_CV'] = stfx_results ["isi_cv"]
      stfx_table.loc[length, 'ISI_mean_ms'] = stfx_results ["mean_isi"]*1000
      stfx_table.loc[length, 'ISI_first_ms'] = stfx_results ["first_isi"]*1000
      stfx_table.loc[length, 'Mean_amplitude'] = new_frame["amplitude"].mean()
  # print (len(currents))
  # print (stfx_table.loc[:,'average_rate'])

  # Optional Plotting: example with three subplots
  fig = plt.figure(figsize=(15, 5))
  # Input-output curve
  ax1 = fig.add_subplot(1, 2, 1)
  ax1.scatter(currents, stfx_table.loc[:,'average_rate'])
  ax1.set_xlabel('Current step (pA)')
  ax1.set_ylabel('Action potentials')
  # print(table)

  # All traces
  ax2 = fig.add_subplot(2, 2, 2)
  for sweep in abf.sweepList:
      abf.setSweep(sweep)
      ax2.plot(abf.sweepX, abf.sweepY, alpha=.6, label="Sweep %d" % (sweep))
  ax2.set_ylabel('Membrane voltage (mV)')
  # ax2.legend() # Optional
  # To highllight one trace
  abf.setSweep(rheobase_sweep)
  ax2.plot(abf.sweepX, abf.sweepY, linewidth=1, color='black')
  ax2.axes.set_xlim(0, 1.6) # Range of the x-axis (seconds)

  # All current steps
  ax3 = fig.add_subplot(2, 2, 4, sharex=ax2)
  for sweep in abf.sweepList:
      abf.setSweep(sweep)
      current = abf.sweepC
      ax3.plot(abf.sweepX, current)
  ax3.set_ylabel("Current (pA)")
  ax3.set_xlabel("Time (s)")
  # To highllight one current trace
  abf.setSweep(rheobase_sweep)
  ax3.plot(abf.sweepX, abf.sweepC, linewidth=1, color='black')
  fig.tight_layout()
  fig.savefig(f"{InputOutput_BatchExport_path}/InputOutput_{abf_file.file_name}.png", dpi=300)
  stfx_table.to_csv(f"{InputOutput_BatchExport_path}/InputOutput_{abf_file.file_name}.csv")
  plt.close(fig)

  return indiv_table, rheobase_sweep

def phase_plots(abf_file, rheobase):
    abf = pyabf.ABF(abf_file)
    # Parse the file name
    folder_path_splitted = abf_file.split('/')
    file_name = folder_path_splitted[-1]
    file_name = file_name[:-4]
    # Inputs (the abf file, sweep number, sampling rate, half-window in ms)
    dv_dt80 = dv_dt(abf, rheobase, 20000, 12)
    # Table with the voltage and dV/dt values
    table80 = pd.DataFrame(columns = ['voltage', 'dv_dt'])
    table80['voltage'] = pd.Series(dv_dt80['voltage'])
    table80['dv_dt'] = pd.Series(dv_dt80['dv_dt'])
    # Graphs
    fig = plt.figure(figsize=(8, 3))
    # Action potential
    ax1 = fig.add_subplot(121)
    ax1.set_title('Action potential Rheobase')
    ax1.plot(dv_dt80['time'], dv_dt80['voltage'])
    ax1.set_ylabel("V (mV)")
    ax1.set_xlabel("t (s)")
    # Phase plot
    ax2 =fig.add_subplot(122)
    ax2.set_title('Phase-plane plot Rheobase')
    ax2.plot(dv_dt80['voltage_array'], dv_dt80['dv_dt'])
    ax2.set_ylabel("dV/dt (mV/ms)")
    ax2.set_xlabel("V (mV)")
    # Exporting files
    fig.savefig(f"{PhasePlot_BatchExport_path}/PhasePlot_{file_name}.png", dpi=300)
    plt.close()
    table80.to_csv(f"{PhasePlot_BatchExport_path}/PhasePlot_{file_name}.csv")
