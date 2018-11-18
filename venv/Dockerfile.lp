FROM fedora:latest

COPY ./xlinpack_xeon64 /
COPY ./linpack_benchmark.sh /

ENTRYPOINT ["./linpack_benchmark.sh"]
