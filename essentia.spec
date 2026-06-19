%global __brp_add_determinism true
%define debug_package %{nil}

Name:           essentia
Version:        2.1_beta6
Release:        1%{?dist}
Summary:        Library for audio analysis and audio-based music information retrieval
License:        GPL-3.0-or-later
URL:            https://essentia.upf.edu/

# Sourced from github.com/MTG/essentia (v2.1_beta5 base, repackaged as 2.1_beta6)
Source0:        essentia-%{version}.tar.gz
Source1:        README.MKL

BuildRequires:  python3
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig
BuildRequires:  eigen3-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  taglib-devel
BuildRequires:  libyaml-devel
BuildRequires:  libchromaprint-devel
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)

%description
Essentia is an open-source C++ library for audio analysis and audio-based music
information retrieval. It contains an extensive collection of algorithms.
This build statically links Intel oneMKL for FFT (replaces fftw3f), making
libessentia.so self-contained with zero runtime MKL dependencies.

%package devel
Summary:        Development files for essentia
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for essentia, including headers and pkg-config file.
The pkg-config module name is "essentia"; use:
  pkg_check_modules(essentia REQUIRED IMPORTED_TARGET essentia)
  pkg_check_modules(essentia_devel REQUIRED IMPORTED_TARGET essentia)

%prep
%setup -q -n essentia-%{version}
cp "%{SOURCE1}" .

%build
# Locate MKL pkgconfig directory — oneAPI installs under /opt/intel/oneapi/mkl/
MKL_PC_DIR=$(find /opt/intel/oneapi/mkl -name "mkl-static-lp64-seq.pc" -print -quit 2>/dev/null | xargs -r dirname)
if [ -z "$MKL_PC_DIR" ]; then
    # Fallback: broader search for older oneAPI layout
    MKL_PC_DIR=$(find /opt/intel/ -name "mkl-static-lp64-seq.pc" -print -quit 2>/dev/null | xargs -r dirname)
fi
if [ -n "$MKL_PC_DIR" ]; then
    export PKG_CONFIG_PATH="$MKL_PC_DIR:${PKG_CONFIG_PATH:-}"
fi

mkdir -p pkgconfig
MKL_LIBS=$(pkg-config --libs mkl-static-lp64-seq)
MKL_CFLAGS=$(pkg-config --cflags mkl-static-lp64-seq)
MKL_PREFIX=$(pkg-config --variable=prefix mkl-static-lp64-seq)

cat <<EOF >pkgconfig/fftw3f.pc
Name: fftw3f
Description: Intel MKL FFTW3 compatibility wrapper
Version: 2025.3
Libs: ${MKL_LIBS}
Cflags: -I${MKL_PREFIX}/include/fftw ${MKL_CFLAGS}
EOF

export PKG_CONFIG_PATH="$(pwd)/pkgconfig:${PKG_CONFIG_PATH:-}"
export CFLAGS="${CFLAGS:-} -march=x86-64-v3"
export CXXFLAGS="${CXXFLAGS:-} -march=x86-64-v3"
python3 waf configure \
    --prefix=/usr \
    --libdir=%{_libdir}
python3 waf build


%install
python3 waf install --destdir="%{buildroot}"
if [ "%{_libdir}" != "%{_prefix}/lib" ] && [ -d "%{buildroot}%{_prefix}/lib" ]; then
    mkdir -p "%{buildroot}%{_libdir}"
    mv "%{buildroot}%{_prefix}/lib"/lib* "%{buildroot}%{_libdir}/" || true
    mkdir -p "%{buildroot}%{_libdir}/pkgconfig"
    mv "%{buildroot}%{_prefix}/lib"/pkgconfig/*.pc "%{buildroot}%{_libdir}/pkgconfig/" || true
    sed -i "s|libdir=\${prefix}/lib|libdir=%{_libdir}|g" "%{buildroot}%{_libdir}/pkgconfig/essentia.pc"
    rm -rf "%{buildroot}%{_prefix}/lib/pkgconfig"
    rmdir "%{buildroot}%{_prefix}/lib" || true
fi
mkdir -p "%{buildroot}%{_datadir}/doc/%{name}"
cp README.MKL "%{buildroot}%{_datadir}/doc/%{name}/"


%files
%{_libdir}/libessentia.so
%{_datadir}/doc/%{name}/README.MKL

%files devel
%{_includedir}/essentia
%{_libdir}/pkgconfig/essentia.pc

%changelog
* Fri Jun 19 2026 Developer <developer@example.com> - 2.1_beta6-1
- Initial essentia package with static Intel MKL FFT integration
