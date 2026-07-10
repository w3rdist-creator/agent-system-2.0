# Disposition

Blocker found: the required real install command exited with status 1 after installing 99 owned files and writing the manifest. Hermes configuration failed in `hermes config set skills.external_dirs.1 ...` with `IndexError: list assignment index out of range`. The subsequent verifier passed all 99 manifest file/hash checks, and both active packs installed successfully, but the clean-room install as a whole was not blocker-free because the required installer did not complete successfully.

blocked
