FROM gitpod/workspace-full

RUN sudo apt-get update \
    && sudo apt-get install -y default-jre graphviz \
    && sudo rm -rf /var/lib/apt/lists/*

RUN pip install antlr4-python3-runtime graphviz liblet \

ENV ANTLR4_JAR=/workspace/liblet/jars/antlr-4.9.3-complete.jar