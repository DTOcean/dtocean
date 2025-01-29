project('f2py_examples', 'c',
  version : '0.1',
  license: 'BSD-3',
  meson_version: '>=0.64.0',
  default_options : ['warning_level=2'],
)

add_languages('fortran')

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

incdir_numpy = run_command(py,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

inc_np = include_directories(incdir_numpy, incdir_f2py)

read_db_path = 'src/dtocean_tidal/submodel/ParametricWake/read_db.f90'
read_db_source = custom_target('read_dbmodule.c',
  input : [read_db_path],
  output : ['read_db_modmodule.c', 'read_db_mod-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'read_db_mod', '--lower']
)

inc_np = include_directories(incdir_numpy, incdir_f2py)

py.extension_module('read_db_mod',
  [read_db_path, read_db_source],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies : [py_dep],
  install : true,
  install_dir : meson.project_source_root() / 'src' / 'dtocean_tidal' / 'submodel' / 'ParametricWake',
)
