from setuptools import setup, find_packages


install_requirement_list = [
    "opencv-python",
    "imutils",
    "numpy",
    "loguru",
    "scikit-learn",
    "scikit-image",
    "scipy",
]

extras_require_dict = {"web": ["flask", "gevent"]}

setup(
    name="findit",
    version="0.5.8",
    description="find target icon on your picture, and get its position",
    author="williamfzc",
    author_email="fengzc@vip.qq.com",
    url="https://github.com/williamfzc/findit",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=install_requirement_list,
    extras_require=extras_require_dict,
)
