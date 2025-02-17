set(LLVM_TARGETS_TO_BUILD X86 CACHE STRING "")

set(PACKAGE_VENDOR TheOrianSolutions CACHE STRING "")

set(_THEORIANSOLUTIONS_ENABLE_PROJECTS "clang;clang-tools-extra;lld;llvm")
set(LLVM_ENABLE_RUNTIMES "compiler-rt;libcxx;libcxxabi;libunwind" CACHE STRING "")

set(LLVM_ENABLE_BACKTRACES OFF CACHE BOOL "")
set(LLVM_ENABLE_DIA_SDK OFF CACHE BOOL "")
set(LLVM_ENABLE_HTTPLIB ON CACHE BOOL "")
set(LLVM_ENABLE_LIBCXX ON CACHE BOOL "")
set(LLVM_ENABLE_LIBEDIT OFF CACHE BOOL "")
set(LLVM_ENABLE_LLD ON CACHE BOOL "")
set(LLVM_ENABLE_LTO ON CACHE BOOL "")
set(LLVM_ENABLE_PER_TARGET_RUNTIME_DIR ON CACHE BOOL "")
set(LLVM_ENABLE_PLUGINS OFF CACHE BOOL "")
set(LLVM_ENABLE_TERMINFO OFF CACHE BOOL "")
set(LLVM_ENABLE_UNWIND_TABLES OFF CACHE BOOL "")
set(LLVM_ENABLE_Z3_SOLVER OFF CACHE BOOL "")
set(LLVM_ENABLE_ZLIB ON CACHE BOOL "")
set(LLVM_INCLUDE_DOCS OFF CACHE BOOL "")
set(LLVM_INCLUDE_EXAMPLES OFF CACHE BOOL "")
set(LLVM_STATIC_LINK_CXX_STDLIB ON CACHE BOOL "")
set(LLVM_USE_RELATIVE_PATHS_IN_FILES ON CACHE BOOL "")
set(LLDB_ENABLE_CURSES OFF CACHE BOOL "")
set(LLDB_ENABLE_LIBEDIT OFF CACHE BOOL "")
set(LLVM_TOOL_LLVM_DRIVER_BUILD ON CACHE BOOL "")
set(LLVM_DRIVER_TARGET llvm-driver)

set(CLANG_DEFAULT_CXX_STDLIB libc++ CACHE STRING "")
set(CLANG_DEFAULT_LINKER lld CACHE STRING "")
set(CLANG_DEFAULT_OBJCOPY llvm-objcopy CACHE STRING "")
set(CLANG_DEFAULT_RTLIB compiler-rt CACHE STRING "")
set(CLANG_DEFAULT_UNWINDLIB libunwind CACHE STRING "")
set(CLANG_ENABLE_ARCMT OFF CACHE BOOL "")
set(CLANG_ENABLE_STATIC_ANALYZER ON CACHE BOOL "")
set(CLANG_PLUGIN_SUPPORT OFF CACHE BOOL "")

set(ENABLE_LINKER_BUILD_ID ON CACHE BOOL "")
set(ENABLE_X86_RELAX_RELOCATIONS ON CACHE BOOL "")

set(CMAKE_BUILD_TYPE Release CACHE STRING "")

set(target "x86_64-unknown-linux-gnu")
if(LINUX_${target}_SYSROOT)
  # Set the per-target builtins options.
  set(LLVM_BUILTIN_TARGETS "${target}" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_SYSTEM_NAME Linux CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_BUILD_TYPE Release CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_C_FLAGS "--target=${target}" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_CXX_FLAGS "--target=${target}" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_ASM_FLAGS "--target=${target}" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_SYSROOT ${LINUX_${target}_SYSROOT} CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_SHARED_LINKER_FLAGS "-fuse-ld=lld" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_MODULE_LINKER_FLAGS "-fuse-ld=lld" CACHE STRING "")
  set(BUILTINS_${target}_CMAKE_EXE_LINKER_FLAG "-fuse-ld=lld" CACHE STRING "")
  set(BUILTINS_${target}_COMPILER_RT_BUILD_STANDALONE_LIBATOMIC ON CACHE BOOL "")

  # Set the per-target runtimes options.
  set(LLVM_RUNTIME_TARGETS "${target}" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_SYSTEM_NAME Linux CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_BUILD_TYPE Release CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_C_FLAGS "--target=${target}" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_CXX_FLAGS "--target=${target}" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_ASM_FLAGS "--target=${target}" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_SYSROOT ${LINUX_${target}_SYSROOT} CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_SHARED_LINKER_FLAGS "-fuse-ld=lld" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_MODULE_LINKER_FLAGS "-fuse-ld=lld" CACHE STRING "")
  set(RUNTIMES_${target}_CMAKE_EXE_LINKER_FLAGS "-fuse-ld=lld" CACHE STRING "")
  set(RUNTIMES_${target}_COMPILER_RT_CXX_LIBRARY "libcxx" CACHE STRING "")
  set(RUNTIMES_${target}_COMPILER_RT_USE_BUILTINS_LIBRARY ON CACHE BOOL "")
  set(RUNTIMES_${target}_COMPILER_RT_USE_LLVM_UNWINDER ON CACHE BOOL "")
  set(RUNTIMES_${target}_COMPILER_RT_CAN_EXECUTE_TESTS ON CACHE BOOL "")
  set(RUNTIMES_${target}_COMPILER_RT_BUILD_STANDALONE_LIBATOMIC ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBUNWIND_ENABLE_SHARED OFF CACHE BOOL "")
  set(RUNTIMES_${target}_LIBUNWIND_USE_COMPILER_RT ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXXABI_USE_COMPILER_RT ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXXABI_ENABLE_SHARED OFF CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXXABI_USE_LLVM_UNWINDER ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXXABI_INSTALL_LIBRARY OFF CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXX_USE_COMPILER_RT ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXX_ENABLE_SHARED OFF CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXX_ENABLE_STATIC_ABI_LIBRARY ON CACHE BOOL "")
  set(RUNTIMES_${target}_LIBCXX_ABI_VERSION 2 CACHE STRING "")
  set(RUNTIMES_${target}_LIBCXX_ADDITIONAL_LIBRARIES pthread CACHE STRING "")
  set(RUNTIMES_${target}_LLVM_ENABLE_ASSERTIONS OFF CACHE BOOL "")
  set(RUNTIMES_${target}_SANITIZER_CXX_ABI "libc++" CACHE STRING "")
  set(RUNTIMES_${target}_SANITIZER_CXX_ABI_INTREE ON CACHE BOOL "")
  set(RUNTIMES_${target}_SANITIZER_TEST_CXX "libc++" CACHE STRING "")
  set(RUNTIMES_${target}_SANITIZER_TEST_CXX_INTREE ON CACHE BOOL "")
  set(RUNTIMES_${target}_LLVM_TOOLS_DIR "${CMAKE_BINARY_DIR}/bin" CACHE BOOL "")
  set(RUNTIMES_${target}_LLVM_ENABLE_RUNTIMES "compiler-rt;libcxx;libcxxabi;libunwind" CACHE STRING "")

  # Use .build-id link.
  list(APPEND RUNTIME_BUILD_ID_LINK "${target}")
endif()

# Setup toolchain.
set(LLVM_INSTALL_TOOLCHAIN_ONLY ON CACHE BOOL "")
set(LLVM_TOOLCHAIN_TOOLS
  dsymutil
  llvm-ar
  llvm-cov
  llvm-cxxfilt
  llvm-debuginfod
  llvm-debuginfod-find
  llvm-dlltool
  ${LLVM_DRIVER_TARGET}
  llvm-dwarfdump
  llvm-dwp
  llvm-ifs
  llvm-gsymutil
  llvm-lib
  llvm-libtool-darwin
  llvm-lipo
  llvm-ml
  llvm-mt
  llvm-nm
  llvm-objcopy
  llvm-objdump
  llvm-otool
  llvm-pdbutil
  llvm-profdata
  llvm-rc
  llvm-ranlib
  llvm-readelf
  llvm-readobj
  llvm-size
  llvm-strings
  llvm-strip
  llvm-symbolizer
  llvm-undname
  llvm-xray
  sancov
  scan-build-py
  CACHE STRING "")

set(LLVM_Toolchain_DISTRIBUTION_COMPONENTS
  clang
  lld
  clang-apply-replacements
  clang-doc
  clang-format
  clang-resource-headers
  clang-include-fixer
  clang-refactor
  clang-scan-deps
  clang-tidy
  clangd
  find-all-symbols
  builtins
  runtimes
  ${LLVM_TOOLCHAIN_TOOLS}
  CACHE STRING "")

set(_THEORIANSOLUTIONS_DISTRIBUTIONS Toolchain)

set(LLVM_DISTRIBUTIONS ${_THEORIANSOLUTIONS_DISTRIBUTIONS} CACHE STRING "")
set(LLVM_ENABLE_PROJECTS ${_THEORIANSOLUTIONS_ENABLE_PROJECTS} CACHE STRING "")
