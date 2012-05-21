%{!?__python_ver:%define __python_ver 27}
#define __python_ver 27
%define unicode ucs4

%define _default_patch_fuzz 2

%if "%{__python_ver}" != "EMPTY"
%define main_python 0
%define python python%{__python_ver}
%define tkinter tkinter%{__python_ver}
%else
%define main_python 1
%define python python
%define tkinter tkinter
%endif

%define pybasever 2.7
%define tools_dir %{_libdir}/python%{pybasever}/Tools
%define demo_dir %{_libdir}/python%{pybasever}/Demo
%define doc_tools_dir %{_libdir}/python%{pybasever}/Doc/tools

Summary: An interpreted, interactive, object-oriented programming language
Name: %{python}
Version: 2.7.3
Release: 1%{?dist}
License: Python
Group: Development/Languages
Provides: python-abi = %{pybasever}
Provides: python(abi) = %{pybasever}
Source: http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
Patch0: Python-2.7.3-Centos6.patch

%if %{main_python}
Obsoletes: Distutils
Provides: Distutils
#Obsoletes: python2 
#Provides: python2 = %{version}
Obsoletes: python-elementtree <= 1.2.6
Obsoletes: python-sqlite < 2.3.2
Provides: python-sqlite = 2.3.2
Obsoletes: python-ctypes < 1.0.1
Provides: python-ctypes = 1.0.1
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: readline-devel, openssl-devel, gmp-devel
BuildRequires: ncurses-devel, gdbm-devel, zlib-devel, expat-devel
BuildRequires: libGL-devel tk tix gcc-c++ libX11-devel glibc-devel
BuildRequires: bzip2 tar /usr/bin/find pkgconfig tcl-devel tk-devel
BuildRequires: tix-devel bzip2-devel sqlite-devel
BuildRequires: autoconf
BuildRequires: db4-devel >= 4.3

URL: http://www.python.org/

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules, as well as modules for interfacing to the Tix widget
set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package libs
Summary: The libraries for python runtime
Group: Applications/System
Requires: %{python} = %{version}-%{release}
# Needed for ctypes, to load libraries, worked around for Live CDs size
# Requires: binutils

%description libs
The python interpreter can be embedded into applications wanting to 
use python as an embedded scripting language.  The python-libs package 
provides the libraries needed for this.

%package devel
Summary: The libraries and header files needed for Python development.
Group: Development/Libraries
Requires: %{python} = %{version}-%{release}
# Needed here because of the migration of Makefile from -devel to the main
# package
Conflicts: %{python} < %{version}-%{release}
%if %{main_python}
Obsoletes: python2-devel
Provides: python2-devel = %{version}-%{release}
%endif

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package tools
Summary: A collection of development tools included with Python.
Group: Development/Tools
Requires: %{name} = %{version}-%{release}
Requires: %{tkinter} = %{version}-%{release}
%if %{main_python}
Obsoletes: python2-tools
Provides: python2-tools = %{version}
%endif

%description tools
The Python package includes several development tools that are used
to build python programs.

%package -n %{tkinter}
Summary: A graphical user interface for the Python scripting language.
Group: Development/Languages
BuildRequires:  tcl, tk
Requires: %{name} = %{version}-%{release}
%if %{main_python}
Obsoletes: tkinter2
Provides: tkinter2 = %{version}
%endif

%description -n %{tkinter}

The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%package test
Summary: The test modules from the main python package
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description test

The test modules from the main python pacakge: %{name}
These have been removed to save space, as they are never or almost
never used in production.

You might want to install the python-test package if you're developing python
code that uses more than just unittest and/or test_support.py.

%prep
%setup -q -n Python-%{version}
%patch0 -p1

# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f


%build
topdir=`pwd`
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export LINKCC="gcc"
if pkg-config openssl ; then
  export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
  export LDFLAGS="$LDFLAGS `pkg-config --libs-only-L openssl`"
fi
# Force CC
export CC=gcc
# For patch 4, need to get a newer configure generated out of configure.in 
autoconf
%configure --enable-ipv6 --enable-unicode=%{unicode} --enable-shared

make OPT="$CFLAGS" %{?_smp_mflags}
LD_LIBRARY_PATH=$topdir $topdir/python Tools/scripts/pathfix.py -i "%{_bindir}/env python%{pybasever}" .
# Rebuild with new python
# We need a link to a versioned python in the build directory
ln -s python python%{pybasever}
LD_LIBRARY_PATH=$topdir PATH=$PATH:$topdir make -s OPT="$CFLAGS" %{?_smp_mflags}



%install
[ -d $RPM_BUILD_ROOT ] && rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT%{_mandir}

# Clean up patched .py files that are saved as .lib64
for f in distutils/command/install distutils/sysconfig; do
    rm -f Lib/$f.py.lib64
done

make install DESTDIR=$RPM_BUILD_ROOT
# Fix the interpreter path in binaries installed by distutils 
# (which changes them by itself)
# Make sure we preserve the file permissions
for fixed in $RPM_BUILD_ROOT%{_bindir}/pydoc; do
    sed 's,#!.*/python$,#!%{_bindir}/env python%{pybasever},' $fixed > $fixed- \
        && cat $fixed- > $fixed && rm -f $fixed-
done

# Junk, no point in putting in -test sub-pkg
rm -f $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/idlelib/testcode.py*

# don't include tests that are run at build time in the package
# This is documented, and used: rhbz#387401
if /bin/false; then
 # Move this to -test subpackage.
mkdir save_bits_of_test
for i in test_support.py __init__.py; do
  cp -a $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/test/$i save_bits_of_test
done
rm -rf $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/test
mkdir $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/test
cp -a save_bits_of_test/* $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/test
fi

%if %{main_python}
#ln -s python $RPM_BUILD_ROOT%{_bindir}/python2 # DON'T want to do this for centos6. comes with 2.6.6.
%else
mv $RPM_BUILD_ROOT%{_bindir}/python $RPM_BUILD_ROOT%{_bindir}/%{python}
#mv $RPM_BUILD_ROOT/%{_mandir}/man1/python.1 $RPM_BUILD_ROOT/%{_mandir}/man1/python%{pybasever}.1
%endif

# tools

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages

#modulator
cat > ${RPM_BUILD_ROOT}%{_bindir}/modulator << EOF
#!/bin/bash
exec %{_libdir}/python%{pybasever}/site-packages/modulator/modulator.py
EOF
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/modulator
#cp -r Tools/modulator \
#  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

#pynche
cat > ${RPM_BUILD_ROOT}%{_bindir}/pynche << EOF
#!/bin/bash
exec %{_libdir}/python%{pybasever}/site-packages/pynche/pynche
EOF
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/pynche
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche \
  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

#mv Tools/modulator/README Tools/modulator/README.modulator
mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py $RPM_BUILD_ROOT%{_bindir}/
install -m755  Tools/i18n/msgfmt.py $RPM_BUILD_ROOT%{_bindir}/

# Useful development tools
install -m755 -d $RPM_BUILD_ROOT%{tools_dir}/scripts
install Tools/README $RPM_BUILD_ROOT%{tools_dir}/
install Tools/scripts/*py $RPM_BUILD_ROOT%{tools_dir}/scripts/

# Documentation tools
install -m755 -d $RPM_BUILD_ROOT%{doc_tools_dir}
#install -m755 Doc/tools/mkhowto $RPM_BUILD_ROOT%{doc_tools_dir}

# Useful demo scripts
install -m755 -d $RPM_BUILD_ROOT%{demo_dir}
cp -ar Demo/* $RPM_BUILD_ROOT%{demo_dir}

# Get rid of crap
find $RPM_BUILD_ROOT/ -name "*~"|xargs rm -f
find $RPM_BUILD_ROOT/ -name ".cvsignore"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f
#zero length
rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/site-packages/modulator/Templates/copyright

rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/LICENSE.txt

## Do not link python2 to 2.7
rm $RPM_BUILD_ROOT%{_bindir}/python-config
rm $RPM_BUILD_ROOT%{_bindir}/python2-config
rm $RPM_BUILD_ROOT%{_bindir}/python2
rm $RPM_BUILD_ROOT%{_bindir}/python%{__python_ver}
(cd $RPM_BUILD_ROOT%{_bindir} ; ln -s python%{pybasever} python%{__python_ver} )

#make the binaries install side by side with the main python
%if !%{main_python}
pushd $RPM_BUILD_ROOT%{_bindir}
mv idle idle%{__python_ver}
mv modulator modulator%{__python_ver}
mv pynche pynche%{__python_ver}
mv pygettext.py pygettext%{__python_ver}.py
mv msgfmt.py msgfmt%{__python_ver}.py
mv smtpd.py smtpd%{__python_ver}.py
mv pydoc pydoc%{__python_ver}
popd
%endif



find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/lib-dynload -type d | sed "s|$RPM_BUILD_ROOT|%dir |" > dynfiles
find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/lib-dynload -type f | \
  grep -v "_tkinter.so$" | \
  grep -v "_ctypes_test.so$" | \
  grep -v "_testcapimodule.so$" | \
  sed "s|$RPM_BUILD_ROOT||" >> dynfiles

# Fix for bug #136654
rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/email/test/data/audiotest.au $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/test/audiotest.au

# Fix bug #143667: python should own /usr/lib/python2.x on 64-bit machines
%if "%{_lib}" == "lib64"
install -d $RPM_BUILD_ROOT/usr/lib/python%{pybasever}/site-packages
install -d $RPM_BUILD_ROOT/usr/lib64/python%{pybasever}/site-packages
%endif

# Make python-devel multilib-ready (bug #192747, #139911)
%define _pyconfig32_h pyconfig-32.h
%define _pyconfig64_h pyconfig-64.h

%ifarch ppc64 s390x x86_64 ia64 alpha sparc64
%define _pyconfig_h %{_pyconfig64_h}
%else
%define _pyconfig_h %{_pyconfig32_h}
%endif
mv $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/pyconfig.h \
   $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/%{_pyconfig_h}
cat > $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "%{_pyconfig32_h}"
#elif __WORDSIZE == 64
#include "%{_pyconfig64_h}"
#else
#error "Unknown word size"
#endif
EOF
ln -s ../../libpython%{pybasever}.so $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/config/libpython%{pybasever}.so

# Fix for bug 201434: make sure distutils looks at the right pyconfig.h file
#sed -i -e "s/'pyconfig.h'/'%{_pyconfig_h}'/" $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/distutils/sysconfig.py

# Get rid of egg-info files (core python modules are installed through rpms)
#rm $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/*.egg-info

# python's build is stupid and doesn't fail if extensions fail to build
# let's list a few that we care about...
#for so in _bsddb.so _ctypes.so _cursesmodule.so _elementtree.so _sqlite3.so _ssl.so readline.so _hashlib.so zlibmodule.so bz2.so pyexpat.so; do
for so in _bsddb.so _ctypes.so _curses.so _elementtree.so _sqlite3.so _ssl.so readline.so _hashlib.so zlib.so bz2.so pyexpat.so; do
    if [ ! -f $RPM_BUILD_ROOT/%{_libdir}/python%{pybasever}/lib-dynload/$so ]; then
       echo "Missing $so!!!"
       exit 1
    fi
done


%clean
#rm -fr $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files 
%defattr(-, root, root)
%doc LICENSE README
%{_bindir}/pydoc*
%{_bindir}/python*
%{_mandir}/*/*
#
%dir %{_libdir}/python%{pybasever}
%dir %{_libdir}/python%{pybasever}/site-packages

%if "%{_lib}" == "lib64"
%attr(0755,root,root) %dir /usr/lib/python%{pybasever}
%attr(0755,root,root) %dir /usr/lib/python%{pybasever}/site-packages
%endif

%files libs -f dynfiles
%defattr(-,root,root)
%doc LICENSE README
%{_libdir}/libpython%{pybasever}.so.*
/usr/lib/python%{pybasever}
/usr/lib64/python%{pybasever}
/usr/lib64/pkgconfig/python-2.7.pc
/usr/lib64/pkgconfig/python.pc
/usr/lib64/pkgconfig/python2.pc

%files devel
%defattr(-,root,root)
/usr/include/*
%doc Misc/README.valgrind Misc/valgrind-python.supp Misc/gdbinit
%dir %{_libdir}/python%{pybasever}/config
%{_libdir}/python%{pybasever}/config/*
%{_libdir}/libpython%{pybasever}.so

%files tools
%defattr(-,root,root,755)
#%doc Tools/modulator/README.modulator
%doc Tools/pynche/README.pynche
#%{_libdir}/python%{pybasever}/lib2to3
#%{_libdir}/python%{pybasever}/site-packages/modulator
%{_libdir}/python%{pybasever}/site-packages/pynche
%{_bindir}/smtpd*.py*
%{_bindir}/2to3*
%{_bindir}/idle*
%{_bindir}/modulator*
%{_bindir}/pynche*
%{_bindir}/pygettext*.py*
%{_bindir}/msgfmt*.py*
%{tools_dir}
%{demo_dir}
%{_libdir}/python%{pybasever}/Doc

%files -n %{tkinter}
%defattr(-,root,root,755)
#%{_libdir}/python%{pybasever}/lib-tk
%{_libdir}/python%{pybasever}/lib-dynload/_tkinter.so

%files test
%defattr(-, root, root)
#%{_libdir}/python%{pybasever}/bsddb/test
#%{_libdir}/python%{pybasever}/ctypes/test
#%{_libdir}/python%{pybasever}/distutils/tests
#%{_libdir}/python%{pybasever}/email/test
#%{_libdir}/python%{pybasever}/json/tests
#%{_libdir}/python%{pybasever}/sqlite3/test
#%{_libdir}/python%{pybasever}/test
#%{_libdir}/python%{pybasever}/lib-dynload/_ctypes_test.so
#%{_libdir}/python%{pybasever}/lib-dynload/_testcapimodule.so

