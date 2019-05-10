from setuptools import setup


with open('requirements.txt') as f:
    install_requires_list = f.readlines()

setup(
    name='findit',
    version='0.3.0',
    description='find target icon on your picture, and get its position',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/findit',
    py_modules=['findit'],
    python_requires=">=3.6",
    install_requires=install_requires_list
)
