#!/bin/bash

cmake -B build/ --fresh -Wno-dev
make -C build/
clang -O0 -emit-llvm -S -fpass-plugin=build/skeleton/SkeletonPass.dylib hello.c