#!/bin/sh
# This is a mock of the `autotrace` command. This allows us to test
# functionality surrounding autotrace without having autotrace actually
# installed. This mock detects the parameter that has .svg and copies the
# pre-baked result in ./test.svg

# The autotrace command is used in the file: ./../../map_engraver/drawable/text/autotrace_text.py
# And is used in the unit test: ./../../tests/drawable/text/test_autotrace_text.py

for var in "$@"
do
    case $var in *.svg)
        cp .github/mocks/autotrace_mock.svg $var
    esac
done
