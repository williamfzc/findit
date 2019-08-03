from setuptools import setup, find_packages


install_requirement_list = [
    'opencv-python',
    'imutils',
    'numpy',
    'loguru',
    'opencv-contrib-python==3.4.2.17',
    'scikit-learn',
    'scikit-image',
    'flask',
    'gevent',
    'scipy',
]

setup(
    name='findit',
    version='0.5.5',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=install_requirement_list
)
