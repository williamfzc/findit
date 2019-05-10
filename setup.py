from setuptools import setup


install_requirement_list = [
    'opencv-python',
    'imutils',
    'numpy',
    'loguru',
]

setup(
    name='findit',
    version='0.3.1',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    py_modules=['findit'],
    python_requires=">=3.6",
    install_requires=install_requirement_list
)
