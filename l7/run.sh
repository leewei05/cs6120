#!/bin/bash

cmake -B build/ --fresh -Wno-dev
make -C build/
clang -fpass-plugin=build/skeleton/SkeletonPass.dylib hello.c