from typing import NamedTuple
import pyabf

class AbfFile(NamedTuple):
  ### how to name your file (seperate each parts with underscore)
  date: str = None
  backgrounds: str = None
  genotype: str = None
  age: str = None
  slice_num: str = None
  cell_num: str = None
  stiprotocal: str = None
  record_num: str = None
  ###-------------------
  file_name: str = None
  full_path: str = None
  abf: pyabf.ABF = None

def parse_file_name(abf_file: str) -> AbfFile:
  folder_path = abf_file.split('/')
  file_name = folder_path[-1]
  file_name = file_name[:-4]
  parts = file_name.split('_')
  date = parts[0]
  backgrounds = parts[1]
  genotype = parts[2]
  age = parts[3]
  slice_num = parts[4]
  cell_num = parts[5]
  stiprotocal = parts[6]
  record_num = parts[7]
  abf = pyabf.ABF(abf_file)
  return AbfFile(date=date, backgrounds=backgrounds, genotype=genotype,
                 age=age, slice_num=slice_num, cell_num=cell_num,
                 stiprotocal=stiprotocal, record_num=record_num, file_name=file_name,
                 full_path=abf_file, abf=abf)
