#
# Copyright (c) ZeroC, Inc. All rights reserved.
#

#
# git_tag, when defined, is typically a branch, for example master
#
%if 0%{?git_tag:1}
   %define archive_tag %{git_tag}
   %define archive_dir_suffix %{git_tag}
%else
   # git_tag_version is the git tag vX.Y.Z[...] less the v prefix
   # if not defined, we default to the version provided below
   %{!?git_tag_version:%define git_tag_version 3.7.3}
   %define archive_tag v%{git_tag_version}
   %define archive_dir_suffix %{git_tag_version}
%endif

%define bzip2devel bzip2-devel

%define libdbcxx libdb-cxx
%define libdbcxxdevel libdb-cxx-devel


#
# SLES12 does not define %{dist}
#
%if 0%{?suse_version} == 1315
%global dist                  .sles12
%endif

%if "%{dist}" == ".sles12"
  %define bzip2devel libbz2-devel
  %define libdbcxx db53
  %define libdbcxxdevel db53-devel
%endif

%if "%{dist}" == ".amzn1"
  %define libdbcxx db53
  %define libdbcxxdevel db53-devel
%endif

%if "%{_prefix}" == "/usr"
%define runpath embedded_runpath=no
%else
%define runpath embedded_runpath_prefix=%{_prefix}
%endif

%define makebuildopts CONFIGS="shared" OPTIMIZE=yes V=1 %{runpath} %{?_smp_mflags}
%define makeinstallopts CONFIGS="shared" OPTIMIZE=yes V=1 %{runpath} DESTDIR=%{buildroot} prefix=%{_prefix} install_bindir=%{_bindir} install_libdir=%{_libdir} install_includedir=%{_includedir} install_mandir=%{_mandir}

Name: %{?nameprefix}freeze
Version: 3.7.3
Summary: Persistent storage for Ice objects
Release: 1%{?dist}
%if "%{?ice_license}"
License: %{ice_license}
%else
License: GPLv2
%endif
Vendor: ZeroC, Inc.
URL: https://zeroc.com/
Source0: https://github.com/zeroc-ice/freeze/archive/%{archive_tag}/%{name}-%{version}.tar.gz
Source1: https://github.com/zeroc-ice/ice/archive/%{archive_tag}/ice-%{version}.tar.gz
BuildRequires: pkgconfig(expat), pkgconfig(mcpp), pkgconfig(openssl), libice-c++-devel, %{bzip2devel}, %{libdbcxxdevel}
%description
Not used

#
# Enable debug package except if it's already enabled
#
%if %{!?_enable_debug_packages:1}%{?_enable_debug_packages:0}
%debug_package
%endif

#
# libfreezeM.m-c++ package
#
%package -n lib%{?nameprefix}freeze3.7-c++
Summary: Freeze for C++ run-time library.
Group: System Environment/Libraries
Requires: lib%{?nameprefix}ice3.7-c++%{?_isa}
Requires: %{libdbcxx}%{?_isa} >= 5.3
%description -n lib%{?nameprefix}freeze3.7-c++
This package contains the C++ run-time library for the Freeze service.
Freeze provides persistent storage for Ice objects.

#
# libfreeze-c++-devel package
#
%package -n lib%{?nameprefix}freeze-c++-devel
Summary: Libraries and headers for developing Freeze applications in C++.
Group: Development/Tools
Obsoletes: ice-c++-devel < 3.6
Requires: lib%{?nameprefix}freeze3.7-c++%{?_isa} = %{version}-%{release}
Requires: %{?nameprefix}freeze-compilers(x86-64) = %{version}-%{release}
Requires: lib%{?nameprefix}ice-c++-devel%{?_isa} >= 3.7.1, lib%{?nameprefix}ice-c++-devel%{?_isa} < 3.8.0
%description -n lib%{?nameprefix}freeze-c++-devel
This package contains the library and header files needed for developing
Freeze applications in C++.
Freeze provides persistent storage for Ice objects.

#
# freeze-compilers package
#
%package -n %{?nameprefix}freeze-compilers
Summary: Slice compilers for developing Freeze applications
Group: Development/Tools
Requires: %{?nameprefix}ice-slice >= 3.7.1, %{?nameprefix}ice-slice < 3.8.0
%description -n %{?nameprefix}freeze-compilers
This package contains Slice compilers for developing Freeze applications.
Freeze provides persistent storage for Ice objects.

#
# freeze-utils package
#
%package -n %{?nameprefix}freeze-utils
Summary: Freeze utilities
Group: Applications/System
Obsoletes: ice-utils < 3.6
Requires: lib%{?nameprefix}freeze3.7-c++%{?_isa} = %{version}-%{release}
%description -n %{?nameprefix}freeze-utils
This package contains Freeze utilities.
Freeze provides persistent storage for Ice objects.

%prep
%setup -q -n freeze-%{archive_dir_suffix} -a 1
rmdir ice
mv ice-%{archive_dir_suffix} ice

%build
# recommended flags for optimized hardened build
export CXXFLAGS="%{optflags}"
export LDFLAGS="%{?__global_ldflags}"

make -C ice/cpp %{makebuildopts} IceUtil Slice
make -C cpp %{makebuildopts} ICE_BIN_DIST=all srcs

%install
make -C cpp %{makeinstallopts} ICE_BIN_DIST=all install

#
# libfreezeM.m-c++ package
#
%files -n lib%{?nameprefix}freeze3.7-c++
%license LICENSE
%{_libdir}/libFreeze.so.*
%post -n lib%{?nameprefix}freeze3.7-c++ -p /sbin/ldconfig
%postun -n lib%{?nameprefix}freeze3.7-c++
/sbin/ldconfig
exit 0

#
# libfreeze-c++-devel package
#
%files -n lib%{?nameprefix}freeze-c++-devel
%license LICENSE
%{_libdir}/libFreeze.so
%{_includedir}/Freeze

#
# freeze-compilers package
#
%files -n %{?nameprefix}freeze-compilers
%license LICENSE
%{_bindir}/slice2freeze
%{_mandir}/man1/slice2freeze.1*
%{_bindir}/slice2freezej
%{_mandir}/man1/slice2freezej.1*

#
# freeze-utils package
#
%files -n %{?nameprefix}freeze-utils
%license LICENSE
%{_bindir}/dumpdb
%{_mandir}/man1/dumpdb.1*
%{_bindir}/transformdb
%{_mandir}/man1/transformdb.1*

%changelog


* Fri Apr 13 2018 José Gutiérrez de la Concha <jose@zeroc.com> 3.7.1
- 3.7.1 release

* Thu Jun 8 2017 Bernard Normier <bernard@zeroc.com> 3.7.0
- Updated version

* Tue Mar 7 2017 Benoit Foucher <benoit@zeroc.com> 3.7b0
- Version bump

* Wed Feb 22 2017 Bernard Normier <bernard@zeroc.com> 3.7a4
- Initial package
