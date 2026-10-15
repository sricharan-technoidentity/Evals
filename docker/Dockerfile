# Sandbox image for `-T sandbox=docker` (one image covers both repos).
# NOTE: written for the POC but not yet run; the local sandbox is the tested path.
FROM eclipse-temurin:17-jdk

RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl ca-certificates \
 && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && npm install -g pnpm@10 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
