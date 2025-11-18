#!/bin/bash
set -e

# Create pip3.12 alias that redirects to pip3
pip3.12() {
    pip3 "$@"
}
export -f pip3.12
