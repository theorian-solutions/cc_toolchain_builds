# C/C++ toolchains builds

## Introduction

Repository contains scripts for building and publishing C/C++ toolchains through GitHub Actions.

Available builds are fully-hermetic toolchains for Linux. This allows cross-compiling for different distributions and also makes it portable. Toolchains can be integrated into different build systems.

## Available toolchains

Currently only supported platform is `x86_64_linux_gnu`.

Following builds are currently available:

| compiler   | kernel   | glibc   | binutils   |
| :--------: | :------: | :-----: | :--------: |
| GCC 7.5    | 4.15     | 2.27    | 2.33.1     |
| GCC 8.5    | 4.15     | 2.27    | 2.36       |
| GCC 9.5    | 4.15     | 2.27    | 2.38       |
| GCC 10.5   | 4.15     | 2.27    | 2.40       |
| GCC 11.5   | 4.15     | 2.27    | 2.42       |
| GCC 12.4   | 4.15     | 2.27    | 2.42       |
| GCC 13.3   | 4.15     | 2.27    | 2.42       |
| GCC 14.2   | 4.15     | 2.27    | 2.42       |
