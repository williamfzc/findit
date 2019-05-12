from setuptools import setup, find_packages


install_requirement_list = [
    'opencv-python',
    'imutils',
    'numpy',
    'loguru',
    'opencv-contrib-python==3.4.2.17'
]

setup(
    name='findit',
    version='0.4.0',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=install_requirement_list
)
