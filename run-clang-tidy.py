#!/usr/bin/env python

# Run clang-tidy recursively and parallel on directory
# Usage: run-clang-tidy sourcedir builddir excludedirs extensions
# extensions and excludedirs are specified as comma-separated
# string without dot, e.g. 'c,cpp'
# e.g. run-clang-tidy . build test,other c,cpp file

import os, sys, subprocess, multiprocessing
manager = multiprocessing.Manager()
failedfiles = manager.list()

# Get absolute paths from arguments
print("Arguments: " + str(sys.argv))
sourcedir = os.path.abspath(sys.argv[1])
print("Source directory: " + sourcedir)
builddir = os.path.abspath(sys.argv[2])
print("Build directory: " + builddir)

# If exclude dirs is not empty, split it into a tuple
excludedirs = ()
if sys.argv[3]:
    excludedirs = tuple([os.path.join(sourcedir, s) for s in sys.argv[3].split(',')])
# If the build directory is not the same as the source directory, exclude it
if not sourcedir == builddir:
    excludedirs = excludedirs + (builddir,)
print("Exclude directories: " + str(excludedirs))
# Split extensions into a tuple
extensions = tuple([("." + s) for s in sys.argv[4].split(',')])
print("Extensions: " + str(extensions))

def runclangtidy(filepath):
    print("Checking: " + filepath)
    proc = subprocess.Popen(f'clang-tidy --quiet -p={builddir} {filepath}', shell=True)
    if proc.wait() != 0:
        failedfiles.append(filepath)

def collectfiles(dir, exclude, exts):
    collectedfiles = []
    for root, dirs, files in os.walk(dir):
        root = os.path.abspath(root)
        for file in files:
            filepath = os.path.join(root, file)
            if (len(exclude) == 0 or not filepath.startswith(exclude)) and filepath.endswith(exts):
                collectedfiles.append(filepath)
    return collectedfiles

# Define the pool AFTER the global variables and subprocess function because WTF python
# See: https://stackoverflow.com/questions/41385708/multiprocessing-example-giving-attributeerror
pool = multiprocessing.Pool()
pool.map(runclangtidy, collectfiles(sourcedir, excludedirs, extensions))
pool.close()
pool.join()
if len(failedfiles) > 0:
    print("Errors in " + len(failedfiles) + " files")
    sys.exit(1)
print("No errors found")
sys.exit(0)
