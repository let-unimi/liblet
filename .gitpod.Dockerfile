FROM gitpod/workspace-full

RUN sudo apt-get update \
    && sudo apt-get install -y default-jre graphviz \
    && sudo rm -rf /var/lib/apt/lists/*

RUN wget -O - https://apt.llvm.org/llvm.sh > /tmp/llvm.sh && chmod u+x /tmp/llvm.sh && /tmp/llvm.sh 11

RUN pip install antlr4-python3-runtime graphviz liblet

ENV ANTLR4_JAR=/workspace/liblet/jars/antlr-4.10-complete.jar