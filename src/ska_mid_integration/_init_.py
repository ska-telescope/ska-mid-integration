import os

if not os.getenv("SKA_TELESCOPE"):
    os.environ["SKA_TELESCOPE"] = "SKA-mid"