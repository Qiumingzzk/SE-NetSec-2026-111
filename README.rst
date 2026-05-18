.. image:: https://raw.githubusercontent.com/pycqa/bandit/main/logo/logotype-sm.png
    :alt: Bandit

======

.. image:: https://github.com/PyCQA/bandit/actions/workflows/pythonpackage.yml/badge.svg?branch=main
    :target: https://github.com/PyCQA/bandit/actions?query=workflow%3A%22Build+and+Test+Bandit%22+branch%3Amain
    :alt: Build Status

.. image:: https://readthedocs.org/projects/bandit/badge/?version=latest
    :target: https://readthedocs.org/projects/bandit/
    :alt: Docs Status

.. image:: https://img.shields.io/pypi/v/bandit.svg
    :target: https://pypi.org/project/bandit/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/bandit.svg
    :target: https://pypi.org/project/bandit/
    :alt: Python Versions

.. image:: https://img.shields.io/pypi/format/bandit.svg
    :target: https://pypi.org/project/bandit/
    :alt: Format

.. image:: https://img.shields.io/badge/license-Apache%202-blue.svg
    :target: https://github.com/PyCQA/bandit/blob/main/LICENSE
    :alt: License

.. image:: https://img.shields.io/discord/825463413634891776.svg
    :target: https://discord.gg/qYxpadCgkx
    :alt: Discord

A security linter from PyCQA

* Free software: Apache license
* Documentation: https://bandit.readthedocs.io/en/latest/
* Source: https://github.com/PyCQA/bandit
* Bugs: https://github.com/PyCQA/bandit/issues
* Contributing: https://github.com/PyCQA/bandit/blob/main/CONTRIBUTING.md

Overview
--------

Bandit is a tool designed to find common security issues in Python code. To do
this Bandit processes each file, builds an AST from it, and runs appropriate
plugins against the AST nodes. Once Bandit has finished scanning all the files
it generates a report.

Bandit was originally developed within the OpenStack Security Project and
later rehomed to PyCQA.

.. image:: https://raw.githubusercontent.com/pycqa/bandit/main/bandit-terminal.png
    :alt: Bandit Example Screen Shot

Show Your Style
---------------

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security Status

Use our badge in your project's README!

using Markdown::

    [![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

using RST::

    .. image:: https://img.shields.io/badge/security-bandit-yellow.svg
        :target: https://github.com/PyCQA/bandit
        :alt: Security Status

References
----------

Python AST module documentation: https://docs.python.org/3/library/ast.html

Green Tree Snakes - the missing Python AST docs:
https://greentreesnakes.readthedocs.org/en/latest/

Documentation of the various types of AST nodes that Bandit currently covers
or could be extended to cover:
https://greentreesnakes.readthedocs.org/en/latest/nodes.html

Container Images
----------------

Bandit is available as a container image, built within the bandit repository
using GitHub Actions. The image is available on ghcr.io:

.. code-block:: console

    docker pull ghcr.io/pycqa/bandit/bandit

The image is built for the following architectures:

* amd64
* arm64
* armv7
* armv8

To pull a specific architecture, use the following format:

.. code-block:: console

    docker pull --platform=<architecture> ghcr.io/pycqa/bandit/bandit:latest

Every image is signed with sigstore cosign and it is possible to verify the
source of origin using the following cosign command:

.. code-block:: console

    cosign verify ghcr.io/pycqa/bandit/bandit:latest \
      --certificate-identity https://github.com/pycqa/bandit/.github/workflows/build-publish-image.yml@refs/tags/<version> \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com

Where `<version>` is the release version of Bandit.

Sponsors
--------

The development of Bandit is made possible by the following sponsors:

.. list-table::
   :width: 100%
   :class: borderless

   * - .. image:: https://avatars.githubusercontent.com/u/34240465?s=200&v=4
          :target: https://opensource.mercedes-benz.com/
          :alt: Mercedes-Benz
          :width: 88

     - .. image:: https://github.githubassets.com/assets/tidelift-8cea37dea8fc.svg
          :target: https://tidelift.com/lifter/search/pypi/bandit
          :alt: Tidelift
          :width: 88

     - .. image:: https://avatars.githubusercontent.com/u/110237746?s=200&v=4
          :target: https://stacklok.com/
          :alt: Stacklok
          :width: 88

If you also ❤️ Bandit, please consider sponsoring.

markdown
# 代码安全扫描平台 (SE-NetSec-2026-SecScan)

基于 Bandit 的自定义安全检测插件 + Flask 后端 + Celery 异步扫描

## 快速启动
<<<<<<< HEAD
=======

>>>>>>> b1b19cb379f16a65d9325cf0c8b8130bc375ac7d
# 代码安全扫描平台 - v1.0

## 功能列表
- ✅ 单文件 / 目录递归扫描
- ✅ ZIP 压缩包上传扫描
- ✅ 检测不安全反序列化（pickle, yaml, joblib, numpy）
- ✅ 检测危险动态代码执行（eval, exec）
- ✅ 检测系统命令注入（os.system, subprocess）
- ✅ 扫描结果对比（新增/修复/持续）
- ✅ 实时进度推送（SSE）
- ✅ 结果导出 CSV
- ✅ 代码片段高亮显示
- ✅ 历史记录分页
- ✅ Docker 一键部署

## 快速开始
```bash
git clone https://github.com/Qiumingzzk/SE-NetSec-2026-111
cd SE-NetSec-2026-111
docker-compose up -d