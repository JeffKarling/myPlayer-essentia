[Release Page](https://github.com/JeffKarling/myPlayer-essentia/releases) | [GitHub Repository](https://github.com/JeffKarling/myPlayer-essentia)

# myPlayer-essentia

RPM packaging for [Essentia](https://essentia.upf.edu/) — an open-source C++ library for audio analysis and music information retrieval — built for Fedora 42 with **statically-linked Intel oneMKL** replacing the standard FFTW3 dependency.

## Packages

| RPM | Contents | pkg-config module |
|---|---|---|
| `essentia-2.1_beta6-1.fc42.x86_64.rpm` | `libessentia.so` (self-contained, zero MKL runtime deps) | — |
| `essentia-devel-2.1_beta6-1.fc42.x86_64.rpm` | Headers + `essentia.pc` | `essentia` |

## Installation

Download both RPMs from the [latest release](https://github.com/JeffKarling/myPlayer-essentia/releases/latest) and install:

```bash
sudo dnf install --nogpgcheck \
    essentia-2.1_beta6-1.fc42.x86_64.rpm \
    essentia-devel-2.1_beta6-1.fc42.x86_64.rpm
```

## CMake Integration

After installing `essentia-devel`, use `pkg_check_modules` in your `CMakeLists.txt`:

```cmake
find_package(PkgConfig REQUIRED)
pkg_check_modules(essentia GLOBAL REQUIRED IMPORTED_TARGET essentia)

# Then link your target:
target_link_libraries(myTarget PRIVATE PkgConfig::essentia)
```

## Why Intel MKL instead of FFTW3?

Essentia normally depends on `fftw3f` for single-precision FFT. This build redirects that dependency to Intel oneMKL via a compatibility shim, making `libessentia.so` completely self-contained — no MKL shared libraries required at runtime.

See [README.MKL](README.MKL) for full technical details.

## Building from Source (Local)

Requires the `essentia.spec` and `README.MKL` from this repo, plus Intel oneAPI MKL installed under `/opt/intel/`.

```bash
# Set up rpmbuild tree
rpmdev-setuptree

# Download upstream essentia source
curl -L https://github.com/MTG/essentia/archive/v2.1_beta6.tar.gz \
    -o ~/rpmbuild/SOURCES/essentia-2.1_beta6.tar.gz
cp README.MKL ~/rpmbuild/SOURCES/
cp essentia.spec ~/rpmbuild/SPECS/

# Build
rpmbuild -ba ~/rpmbuild/SPECS/essentia.spec
```

## CI / GitHub Actions

The workflow in `.github/workflows/build-rpm.yml` builds both RPMs automatically on Fedora 42 and publishes them as release assets when a `v*` tag is pushed.
