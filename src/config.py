def load_credentials() -> tuple[str, str]:
    with open("credentials") as f:
        auth_data = f.read().strip().split(";")
        return auth_data[0], auth_data[1]
