#!/usr/bin/env bash
# vim :set ts=4 sw=4 sts=4 et:
die() { printf $'Error: %s\n' "$*" >&2; exit 1; }
root=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)
self=${BASH_SOURCE[0]:?}
project=${root##*/}
pexec() { >&2 printf exec; >&2 printf ' %q' "$@"; >&2 printf '\n'; exec "$@"; }
#---

go---virtualenv() {
    pexec "${self:?}" virtualenv \
    exec "${self:?}" "$@" \
    ##
}

go---spack() {
    pexec "${self:?}" spack \
    exec "${self:?}" "$@" \
    ##
}

go---poincare() {
    PYTHONPATH=${root:?}/src${PYTHONPATH:+:${PYTHONPATH:?}} \
    pexec "${self:?}" "$@" \
    ##
}

go-exec() {
    pexec "$@"
}

go-server() {
    pexec "${self:?}" \
        --virtualenv \
        --spack \
        --poincare \
        --server \
    ##
}

server_bind=0.0.0.0
server_port=8080
go---server() {
    pexec python3 -m poincare.server \
        --bind "${server_bind:?}" \
        --port "${server_port:?}" \
    ##
}


#--- Python Virtual Environment

virtualenv=${root:?}/venv

go-virtualenv() {
    "${FUNCNAME[0]:?}-${@:?}"
}

go-virtualenv-create() {
    pexec python3 -m venv \
        "${virtualenv:?}" \
    ##
}

go-virtualenv-install() {
    pexec "${virtualenv:?}/bin/python3" -m pip install \
        -r "${root:?}/requirements.txt" \
    ##
}

go-virtualenv-exec() {
    source "${virtualenv:?}/bin/activate" \
    && \
    pexec "$@" \
    ##
}


#--- Spack Environment

spack=${root:?}/spack

go-spack() {
    "${FUNCNAME[0]:?}-${@:?}"
}

go-spack-exec() {
    eval $(
        "${spack:?}/bin/spack" load \
            --sh \
            "adios2+python~bzip2~libcatalyst^openmpi@4.1.5" \
        ##
    ) \
    && \
    pexec "$@" \
    ##
}


#---
test -f "${root:?}/env.sh" && source "${_:?}"
"go-$@"
