ARG FROM=rust
FROM $FROM
USER appuser
RUN which cargo && cargo install --locked --bin jj jj-cli
ENV PATH="/home/appuser/.cargo/bin:${PATH}"
WORKDIR /home/appuser
ENV EDITOR=nvim
ENV VISUAL=nvim
RUN jj config set --user user.name "Alvaro Garcia"
RUN jj config set --user user.email "alvarogarcia7@noreply.users.github.com"

