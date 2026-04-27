FROM debian
SHELL ["/bin/bash", "-c"]
ARG UID=1001 GID=1002 SHELL="zsh" GLAB_VERSION=1.90.0 PATH="/root/.cargo/bin:${PATH}" TZ=Asia/Dubai
# Root setup: base packages, ssh, rustup, git-worktree-runner, and docker
RUN apt update && apt install -y \
  bash curl gcc gh git jq libssl-dev make neovim openssh-server pkg-config \
  procps ssh unzip vim wget zip zsh libnss3-tools expect \
  && rm -rf /var/lib/apt/lists/* \
  && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y \
  && echo 'source $HOME/.cargo/env' >> $HOME/.bashrc \
  && mkdir -p /var/run/sshd \
  && rm /bin/sh && ln -s /bin/bash /bin/sh \
  && git clone https://github.com/coderabbitai/git-worktree-runner.git /bin/git-worktree-runner \
  && ssh-keygen -A && service ssh --full-restart \
  && curl -fsSL https://get.docker.com | sh
# Create app directory and clone vibe-kanban
WORKDIR /app
# Create user and group
RUN addgroup --gid ${GID} appgroup && useradd -m --uid ${UID} -g appgroup appuser
# Install glab
EXPOSE 22
USER appuser
# Install dotfiles and setup git-gtr symlink
RUN rm -rf /home/appuser/bin && \
  cd /tmp && git clone https://github.com/alvarogarcia7/dotfiles.git && \
  cd dotfiles && echo "O" | bash install.sh && \
  rm -f /home/appuser/bin/git-gtr && \
  cd /bin/git-worktree-runner && mkdir -p /home/appuser/bin && \
  ln -s "$(pwd)/bin/git-gtr" /home/appuser/bin/git-gtr
# Install pnpm and set zsh as default shell
RUN curl -fsSL https://get.pnpm.io/install.sh | sh -
USER root
RUN chsh -s /bin/zsh appuser
USER appuser
# Start zsh if bash is invoked
RUN echo '' >> ~/.bashrc && \
  echo '# Start zsh if invoked via bash' >> ~/.bashrc && \
  echo 'if [ -z "$ZSH_VERSION" ] && [ "$SHELL" = "/bin/zsh" ]; then' >> ~/.bashrc && \
  echo '  exec zsh' >> ~/.bashrc && \
  echo 'fi' >> ~/.bashrc

ENV PATH="/home/appuser/.nvm/versions/node/v${NODE_VERSION}/bin:${PATH}"
# Git config and Rust setup
RUN git config --global push.autoSetupRemote true && \
  git config --global credential.helper store && \
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y && \
  echo 'source $HOME/.cargo/env' >> $HOME/.bashrc && \
  chmod +x "$HOME/.cargo/env"
ENV PATH="$PATH:/home/appuser/.cargo/bin:/home/appuser/bin:/app/userapp/bin"
RUN which cargo && cargo install cargo-binstall && cargo binstall jj jj-cli
# Verification: test all installed tools
RUN node --version && npm --version && npx --version && \
  python3.14 -v && java -version && javac -version && \
  glab --version && nvim --version && \
  grep -q "git_rebase_continue_date" ~/.zshrc && \
  [ "$(getent passwd appuser | cut -d: -f7)" = "/bin/zsh" ]
USER root
CMD ["/usr/sbin/sshd", "-D"]
