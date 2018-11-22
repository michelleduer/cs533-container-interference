FROM fedora:latest

COPY ./stress_benchmark.sh /
RUN dnf install stress -y

ENTRYPOINT ["./stress_benchmark.sh"]
