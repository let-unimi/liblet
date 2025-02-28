FROM gitpod/workspace-full

RUN sudo apt-get update \
    && sudo apt-get install -y graphviz \
    && sudo rm -rf /var/lib/apt/lists/*

RUN bash -c ". /home/gitpod/.sdkman/bin/sdkman-init.sh && sdk install java 17-open"

RUN wget -O - https://apt.llvm.org/llvm.sh > /tmp/llvm.sh && chmod u+x /tmp/llvm.sh && sudo /tmp/llvm.sh 11

RUN pip install antlr4-python3-runtime graphviz liblet

ENV ANTLR4_JAR=/workspace/liblet/jars/antlr-4.13.2-complete.jar