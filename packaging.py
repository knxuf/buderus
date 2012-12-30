# -*- coding: utf-8 -*-

import zipfile
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1
import sys
import os
import re
import time
import subprocess
import tempfile
import difflib

timestamp= time.strftime("%Y%m%d-%H%M")

def sha_hash_file(filename):
    _f = open(filename,"rb")
    _data = _f.read()
    _f.close()
    return sha_hash(_data)


def sha_hash(_data):
    _s = sha1()
    _s.update("blob %u\0" % len(_data))
    _s.update(_data)
    return _s.hexdigest()

main_package = "12264_Buderus.py"
package = { 
    main_package : None,
    "12265_Buderus-Heizkreis.py":None,
    "12266_Buderus-Warmwasser.py": None,
    "12267_Buderus-Fehler.py": None,
    "12282_Buderus-Solar.py": None,
    "12283_Buderus-alternativer_Waermeerzeuger.py": None,
}

diffs=[]

class package_file_object(object):
    def __init__(self,filename):
        self.filename = filename
        _f = open(filename,"rb")
        _sourcecode = _f.read()
        _f.close()
        self.sha = sha_hash(_sourcecode)
        self.logikname, self.logikid, self.version = re.findall('^LOGIKNAME="(.*?)".*?^LOGIKID="(\d+)".*?^VERSION="(.*?)".*?',_sourcecode, re.MULTILINE | re.DOTALL)[0]

        _path, _file = os.path.split(filename)
        old_source = []
        try:
            _f = open( os.path.join(_path,"last",_file) ,"rb")
            old_source = _f.readlines()
            _f.close()
        except IOError:
            _sourcecode = ""
        _f = open( os.path.join(_path,"last",_file) ,"wb")
        _f.write(_sourcecode)
        _f.close()
        for line in difflib.unified_diff(old_source,_sourcecode.splitlines(1),fromfile=os.path.join(_path,"last",_file) ,tofile=filename):
            diffs.append(line)
        
    def __repr__(self):
        return "%s (%s) Version %s (%s)" % (self.logikid,self.logikname,self.version, self.sha)


current_dir = os.getcwd()
for _dir in ["package","sources","last"]:
    if not os.path.isdir(_dir):
        os.mkdir(_dir)

temp_dir = tempfile.mkdtemp()
os.chdir(temp_dir)
for _package in package.keys():
    _fullpath = os.path.join(current_dir,_package)
    package[_package] = package_file_object(_fullpath)
    _compile = subprocess.Popen([sys.executable, _fullpath])
    _compile.communicate()

compiled_files = os.listdir(temp_dir)

hsl_checksums = []
package_zip  = zipfile.ZipFile(os.path.join(current_dir,"package","buderus-%s-%s.zip" % (sys.version[:3],package.get(main_package).version) ),"w",zipfile.ZIP_DEFLATED)
for _file in compiled_files:
    hsl_checksums.append( (_file,sha_hash_file(_file)) )
    package_zip.write(_file)
    os.remove(_file)

_chksumfile = open("checksum.txt","wb")
for (_file,_chksum) in hsl_checksums:
    _chksumfile.write("%s * %s\r\n" % (_file,_chksum) )
_chksumfile.close()
package_zip.write("checksum.txt")
os.remove("checksum.txt")

package_zip.close()

os.chdir(current_dir)

os.rmdir(temp_dir)

if diffs:
    source_zip = zipfile.ZipFile(os.path.join(current_dir,"sources","buderus-sources-%s-%s.zip" % (package.get(main_package).version, timestamp) ),"w",zipfile.ZIP_DEFLATED)
    for _package in package.keys():
        source_zip.write(_package)
    source_zip.close()
    _f = open( os.path.join(current_dir,"sources","buderus-sources-%s-%s.diff" % (package.get(main_package).version, timestamp) ) ,"wb")
    for line in diffs:
      _f.write( line )
    _f.close()

