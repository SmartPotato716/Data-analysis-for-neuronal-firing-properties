!pip install scikit-learn
!pip install --no-deps ipfx
!pip install pandas
!pip install pyabf
!pip install seaborn
!pip install matplotlib
# install muppy memory profiler
!pip install pympler
from ipfx.feature_extractor import (SpikeFeatureExtractor, SpikeTrainFeatureExtractor)


import pyabf
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import glob
from itertools import compress
from scipy.signal import find_peaks
from scipy.signal import peak_widths
from scipy.signal import peak_prominences
from scipy.optimize import curve_fit
from scipy.stats import linregress
import scipy.stats
import pandas as pd
import seaborn as sns
sns.set()

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# More memory efficient non interactive backend https://matplotlib.org/stable/users/explain/figure/backends.html
matplotlib.use('Agg')
