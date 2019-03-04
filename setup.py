from setuptools import setup


setup(
    name='findit',
    version='0.2.1',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    py_modules=['findit'],
    install_requires=[
        'opencv-python',
        'imutils',
        'numpy',
    ]
)
