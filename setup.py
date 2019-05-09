from setuptools import setup


setup(
    name='findit',
    version='0.2.2',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    py_modules=['findit'],
    python_requires=">=3.6",
    install_requires=[
        'opencv-python',
        'imutils',
        'numpy',
    ]
)
