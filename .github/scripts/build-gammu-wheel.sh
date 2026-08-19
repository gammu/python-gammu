#!/usr/bin/env bash
#
# Build the deliberately minimal Gammu libraries used by Linux wheels.

set -euo pipefail

# renovate: datasource=github-release-attachments depName=gammu/gammu versioning=loose
readonly GAMMU_VERSION="1.44.1"
readonly GAMMU_SHA256="59876301ed7556c909b656b09c07d9d43ef167eba1ae976175710024188f053d"
readonly GAMMU_PREFIX="${GAMMU_WHEEL_PREFIX:-/opt/python-gammu-gammu}"
readonly GAMMU_ARCHIVE="Gammu-${GAMMU_VERSION}.tar.gz"
readonly GAMMU_URL="https://github.com/gammu/gammu/releases/download/${GAMMU_VERSION}/${GAMMU_ARCHIVE}"

if ! command -v cmake >/dev/null 2>&1; then
    dnf install -y cmake
fi

build_root="$(mktemp -d /tmp/python-gammu-wheel.XXXXXX)"
trap 'rm -rf "$build_root"' EXIT

curl --fail --location --silent --show-error \
    --output "${build_root}/${GAMMU_ARCHIVE}" \
    "$GAMMU_URL"
printf "%s  %s\n" "$GAMMU_SHA256" "${build_root}/${GAMMU_ARCHIVE}" \
    | sha256sum --check -
tar --extract --file "${build_root}/${GAMMU_ARCHIVE}" --directory "$build_root"

cmake \
    -S "${build_root}/Gammu-${GAMMU_VERSION}" \
    -B "${build_root}/build" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DBUILD_SHARED_LIBS=OFF \
    -DWITH_BLUETOOTH=OFF \
    -DWITH_USB=OFF \
    -DWITH_IRDA=OFF \
    -DWITH_MySQL=OFF \
    -DWITH_ODBC=OFF \
    -DWITH_Postgres=OFF \
    -DWITH_LibDBI=OFF \
    -DWITH_CURL=OFF \
    -DWITH_Glib=OFF \
    -DWITH_GObject=OFF \
    -DWITH_SystemD=OFF \
    -DWITH_Libintl=OFF \
    -DWITH_Iconv=OFF \
    -DWITH_Gettext=OFF \
    -DWITH_Doxygen=OFF \
    -DWITH_BashCompletion=OFF
cmake --build "${build_root}/build" \
    --parallel \
    --target libGammu gsmsd

install -d "${GAMMU_PREFIX}/include/gammu" "${GAMMU_PREFIX}/lib"
install -m 0644 "${build_root}/build/include/"*.h \
    "${GAMMU_PREFIX}/include/gammu/"
install -m 0644 "${build_root}/build/libgammu/libGammu.a" \
    "${build_root}/build/smsd/libgsmsd.a" \
    "${GAMMU_PREFIX}/lib/"
