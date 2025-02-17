cmake_minimum_required(VERSION 3.20)

set(CLANG_PREFIX "$ENV{HOST_COMPILER_DIR}/bin")

set(CMAKE_SYSROOT "$ENV{HOST_COMPILER_DIR}/x86_64-linux/sys-root")
set(CMAKE_C_COMPILER "${CLANG_PREFIX}/clang")
set(CMAKE_C_CLANG_TARGET ${CLANG_TARGET} CACHE STRING "")
set(CMAKE_CXX_COMPILER "${CLANG_PREFIX}/clang++")
set(CMAKE_CXX_CLANG_TARGET ${CLANG_TARGET} CACHE STRING "")
set(CMAKE_ASM_COMPILER "${CLANG_PREFIX}/clang")
set(CMAKE_ASM_CLANG_TARGET ${CLANG_TARGET} CACHE STRING "")
set(CMAKE_ADDR2LINE "${CLANG_PREFIX}/llvm-addr2line" CACHE PATH "")
set(CMAKE_AR "${CLANG_PREFIX}/llvm-ar" CACHE PATH "")
set(CMAKE_LINKER "${CLANG_PREFIX}/ld.lld" CACHE PATH "")
set(CMAKE_LIPO "${CLANG_PREFIX}/llvm-lipo" CACHE PATH "")
set(CMAKE_NM "${CLANG_PREFIX}/llvm-nm" CACHE PATH "")
set(CMAKE_OBJCOPY "${CLANG_PREFIX}/llvm-objcopy" CACHE PATH "")
set(CMAKE_OBJDUMP "${CLANG_PREFIX}/llvm-objdump" CACHE PATH "")
set(CMAKE_RANLIB "${CLANG_PREFIX}/llvm-ranlib" CACHE PATH "")
set(CMAKE_READELF "${CLANG_PREFIX}/llvm-readelf" CACHE PATH "")
set(CMAKE_STRIP "${CLANG_PREFIX}/llvm-strip" CACHE PATH "")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
