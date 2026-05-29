from setuptools import find_packages, setup

package_name = "r1_inference"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages",
            [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="R1 Project",
    maintainer_email="dev@r1.local",
    description="Nodo ONNX inference + SDK Unitree bridge.",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "inference_node = r1_inference.inference_node:main",
            "sdk_bridge     = r1_inference.sdk_bridge:main",
        ],
    },
)
