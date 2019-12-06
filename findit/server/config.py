import os

# globals
PIC_EXT_NAME = ".png"
DEFAULT_TARGET_NAME = "DEFAULT_TARGET_NAME"
ALLOWED_EXTRA_ARGS = set("mask_pic_path")

# arg parse
PORT_ENV_NAME = "FINDIT_SERVER_PORT"
PIC_ROOT_ENV_NAME = "FINDIT_SERVER_PIC_ROOT_PATH"

SERVER_PORT: int = int(os.environ.get(PORT_ENV_NAME, default=9410))
PIC_DIR_PATH: str = os.environ.get(PIC_ROOT_ENV_NAME, default="")
