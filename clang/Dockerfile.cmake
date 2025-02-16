FROM clang-toolchain-base AS build_image

RUN apt install make -y

WORKDIR /src/cmake
RUN curl --fail-early --location https://github.com/Kitware/CMake/releases/download/v3.20.0/cmake-3.20.0.tar.gz \
  | tar --gz --extract --strip-components=1 --file -
RUN sed -i 's/cmake_options="-DCMAKE_BOOTSTRAP=1"/cmake_options="-DCMAKE_BOOTSTRAP=1 -DCMAKE_USE_OPENSSL=OFF"/g' bootstrap

ARG SRC_HOST_COMPILER_DIR
ENV HOST_COMPILER_DIR="/opt/cc-x86_64-host"
COPY "${SRC_HOST_COMPILER_DIR}" "${HOST_COMPILER_DIR}"
ENV PATH="${HOST_COMPILER_DIR}/bin:${PATH}"

ARG INSTALL_DIR
RUN ./bootstrap --prefix=${INSTALL_DIR} --parallel=`nproc`

RUN mkdir -p ${INSTALL_DIR}
RUN nice -n20 make -j`nproc`
RUN nice -n20 make install

# ----------------------------------------------------------------------------------------------------------------

FROM alpine:latest

ARG INSTALL_DIR
COPY --from=build_image "${INSTALL_DIR}" "${INSTALL_DIR}"
