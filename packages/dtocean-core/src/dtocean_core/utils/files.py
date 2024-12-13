# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2021 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Created on Tue Feb 23 15:38:18 2016

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os
import time
import shutil
import pickle
import logging
import tarfile
import zipfile
import tempfile

# Set up logging
module_logger = logging.getLogger(__name__)


def pickle_test_data(file_path, test_data_dict):

    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_root = os.path.splitext(file_name)[0]
    dst_name = "{}.pkl".format(file_root)
    dst_path = os.path.join(dir_path, dst_name)
    
    with open(dst_path, 'wb') as dataf:
    
        # Pickle dictionary using protocol 0.
        pickle.dump(test_data_dict, dataf)
        
    return dst_path


def package_dir(src_dir_path, dst_path, archive=False):
    
    if not os.path.splitext(dst_path)[1]: archive = False
    
    if not archive:
        
        for root, dirs, files in os.walk(src_dir_path, topdown=True):
            
            for name in dirs:
                new_path = os.path.join(dst_path, name)
                if os.path.exists(new_path): shutil.rmtree(new_path)
                os.makedirs(new_path)

            for name in files:
                tmp_path = os.path.join(root, name)
                short_path = tmp_path.replace(src_dir_path, "")
                new_path = os.path.join(dst_path, short_path[1:])
                shutil.move(tmp_path, new_path)
                
        shutil.rmtree(src_dir_path)
     
        return

    tgz_dir_path = tempfile.mkdtemp()
    
    project_file_name = os.path.split(dst_path)[1]
    tgz_file_name = "{}.tar.gz".format(project_file_name)
    tgz_file_path = os.path.join(tgz_dir_path, tgz_file_name)

    with tarfile.open(tgz_file_path, "w:gz") as tar:
        
        for root, dirs, files in os.walk(src_dir_path):
    
            for name in files:
                
                file_path = os.path.join(root, name)
                short_path = file_path.replace(src_dir_path, "")
                tar.add(file_path, arcname=short_path)
    
    shutil.copyfile(tgz_file_path, dst_path)
    
    rmtree_retry(src_dir_path, fail_silent=True) # pylint: disable=unexpected-keyword-arg
    rmtree_retry(tgz_dir_path, fail_silent=True) # pylint: disable=unexpected-keyword-arg
    
    return


def unpack_archive(src_path, dst_path):
    
    # Determine if archive is new tar style or legacy zip
    if tarfile.is_tarfile(src_path):
        tar = tarfile.open(src_path, 'r:gz')
        tar.extractall(dst_path)
        tar.close()
    else:
        zf = zipfile.ZipFile(src_path, 'r')
        zf.extractall(dst_path)
        zf.close()
        
    return


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    
    Copyright Michael Foord 2004
    Released subject to the BSD License
    Please see http://www.voidspace.org.uk/python/license.shtml
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def os_retry(func):
    
    def wrapper(src_path,
                max_attempts=60,
                sleep_seconds=1,
                fail_silent=False):
        
        file_locked = True
        n_attempts = 0
        
        while file_locked:
        
            n_attempts += 1
            
            if n_attempts > max_attempts:
                
                if fail_silent: return
                
                total_seconds = max_attempts * sleep_seconds
                
                err_str = ("shutil.rmtree failed for over {} seconds: "
                           "{}").format(total_seconds, src_path)
                raise OSError(err_str)
            
            try:
                func(src_path)
                file_locked = False
            except OSError:
                time.sleep(sleep_seconds)
        
        return
    
    return wrapper


@os_retry
def rmtree_retry(src_path):
    shutil.rmtree(src_path)
    return


@os_retry
def remove_retry(src_path):
    os.remove(src_path)
    return


def init_dir(dir_name,
             clean_existing=False):
    
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        return
        
    if not clean_existing:
        
        err_msg = ("Directory {} already exists. Set clean_existing "
                   "argument to True to delete the contents of the "
                   "directory").format(dir_name)
        raise IOError(err_msg)
    
    for entry_name in os.listdir(dir_name):
        
        entry_path = os.path.join(dir_name, entry_name)
        
        if os.path.isfile(entry_path):
            remove_retry(entry_path)
        elif os.path.isdir(entry_path):
            rmtree_retry(entry_path)
        else:
            err_str = ("Path {} has unhandled filesystem "
                       "type").format(entry_path)
            raise RuntimeError(err_str)
    
    return
