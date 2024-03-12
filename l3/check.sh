#!/bin/bash

FILE=$1
OPT=$2
export PATH="/Users/lee/.deno/bin:$PATH"

echo "Orginial line count:"
bril2json < ../../bril/benchmarks/core/$FILE.bril | bril2txt | wc -l
echo "DCE:"
bril2json < ../../bril/benchmarks/core/$FILE.bril | python3 $OPT.py | bril2txt | wc -l

bril2json < ../../bril/benchmarks/core/$FILE.bril | bril2txt > org.txt
bril2json < ../../bril/benchmarks/core/$FILE.bril | python3 $OPT.py | bril2txt > opt.txt

diff -q org.txt opt.txt
diff -y --color org.txt opt.txt

rm org.txt opt.txt