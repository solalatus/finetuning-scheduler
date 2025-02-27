<div align="center">

<img src="docs/source/_static/images/logos/logo_fts.png" width="401px">

**A PyTorch Lightning extension that enhances model experimentation with flexible fine-tuning schedules.**

______________________________________________________________________

<p align="center">
  <a href="https://finetuning-scheduler.readthedocs.io/en/latest/">Docs</a> •
  <a href="#Setup">Setup</a> •
  <a href="#examples">Examples</a> •
  <a href="#community">Community</a>
</p>

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/finetuning-scheduler)](https://pypi.org/project/finetuning-scheduler/)
[![PyPI Status](https://badge.fury.io/py/finetuning-scheduler.svg)](https://badge.fury.io/py/finetuning-scheduler)\
[![codecov](https://codecov.io/gh/speediedan/finetuning-scheduler/branch/main/graph/badge.svg?flag=gpu)](https://codecov.io/gh/speediedan/finetuning-scheduler)
[![ReadTheDocs](https://readthedocs.org/projects/finetuning-scheduler/badge/?version=latest)](https://finetuning-scheduler.readthedocs.io/en/latest/)
[![DOI](https://zenodo.org/badge/455666112.svg)](https://zenodo.org/badge/latestdoi/455666112)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/speediedan/finetuning-scheduler/blob/master/LICENSE)

</div>

______________________________________________________________________

<img width="300px" src="docs/source/_static/images/fts/fts_explicit_loss_anim.gif" alt="FinetuningScheduler explicit loss animation" align="right"/>

[FinetuningScheduler](https://finetuning-scheduler.readthedocs.io/en/latest/api/finetuning_scheduler.fts.html#finetuning_scheduler.fts.FinetuningScheduler) is simple to use yet powerful, offering a number of features that facilitate model research and exploration:

- easy specification of flexible fine-tuning schedules with explicit or regex-based parameter selection
  - implicit schedules for initial/naive model exploration
  - explicit schedules for performance tuning, fine-grained behavioral experimentation and computational efficiency
- automatic restoration of best per-phase checkpoints driven by iterative application of early-stopping criteria to each fine-tuning phase
- composition of early-stopping and manually-set epoch-driven fine-tuning phase transitions

______________________________________________________________________

## Setup

### Step 0: Install from PyPI

```bash
pip install finetuning-scheduler
```

<!-- following section will be skipped from PyPI description -->

<details>
  <summary>Additional installation options</summary>
    <!-- following section will be skipped from PyPI description -->

#### *Install Optional Packages*

#### To install additional packages required for examples:

```bash
pip install finetuning-scheduler['examples']
```

#### or to include packages for examples, development and testing:

```bash
pip install finetuning-scheduler['all']
```

#### *Source Installation*

#### To install from source (editable) using a custom version of pytorch-lightning (includes docs as well)

#### **Note**: minimum supported pytorch-lightning release is 1.6.0

```bash
# update the url below with the desired release #, e.g. for finetuning-scheduler release 0.1.2:
git clone https://github.com/speediedan/finetuning-scheduler.git@release/0.1.2
cd finetuning-scheduler
# PACKAGE_NAME variable currently required to specify pytorch-lightning dev package dep (as of lightning 1.8.0)
export PACKAGE_NAME=pytorch
python -m pip install -e ".[all]" -r requirements/docs.txt
```

#### *Latest Docker Image*

![Docker Image Version (tag latest semver)](https://img.shields.io/docker/v/speediedan/finetuning-scheduler/latest?color=%23000080&label=docker)

</details>

<!-- end skipping PyPI description -->

### Step 1: Import the FinetuningScheduler callback and start fine-tuning!

```python
from pytorch_lightning import Trainer
from finetuning_scheduler import FinetuningScheduler

trainer = Trainer(callbacks=[FinetuningScheduler()])
```

Get started by following [the Fine-Tuning Scheduler introduction](https://finetuning-scheduler.readthedocs.io/en/latest/index.html) which includes a [CLI-based example](https://finetuning-scheduler.readthedocs.io/en/latest/index.html#example-scheduled-fine-tuning-for-superglue) or by following the [notebook-based](https://pytorch-lightning.readthedocs.io/en/latest/notebooks/lightning_examples/finetuning-scheduler.html) Fine-Tuning Scheduler tutorial.

______________________________________________________________________

## Examples

### Scheduled Fine-Tuning For SuperGLUE

- [Notebook-based Tutorial](https://pytorch-lightning.readthedocs.io/en/latest/notebooks/lightning_examples/finetuning-scheduler.html)
- [CLI-based Tutorial](https://finetuning-scheduler.readthedocs.io/en/latest/#example-scheduled-fine-tuning-for-superglue)
- [FSDP Scheduled Fine-Tuning](https://finetuning-scheduler.readthedocs.io/en/latest/advanced/fsdp_scheduled_fine_tuning.html)
- [LR Scheduler Reinitialization](https://finetuning-scheduler.readthedocs.io/en/latest/advanced/lr_scheduler_reinitialization.html) (advanced)

______________________________________________________________________

## Continuous Integration

Fine-Tuning Scheduler is rigorously tested across multiple CPUs, GPUs and against major Python and PyTorch versions. Each Fine-Tuning Scheduler minor release (major.minor.patch) is paired with a PyTorch Lightning minor release (e.g. Fine-Tuning Scheduler 0.4 depends upon PyTorch Lightning 1.9).

To ensure maximum stability, the latest PyTorch Lightning patch release fully tested with Fine-Tuning Scheduler is set as a maximum dependency in Fine-Tuning Scheduler's requirements.txt (e.g. \<= 1.7.1). If you'd like to test a specific PyTorch Lightning patch version greater than that currently in Fine-Tuning Scheduler's requirements.txt, it will likely work but you should install Fine-Tuning Scheduler from source and update the requirements.txt as desired.

<details>
  <summary>Current build statuses for Fine-Tuning Scheduler </summary>

| System / (PyTorch/Python ver) |                                                                                                         1.10/3.7                                                                                                         |                                                                                                             1.13.1/3.7, 1.13.1/3.10                                                                                                              |
| :---------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|      Linux \[GPUs\*\*\]       |                                                                                                            -                                                                                                             | [![Build Status](https://dev.azure.com//speediedan/finetuning-scheduler/_apis/build/status/Multi-GPU%20&%20Example%20Tests?branchName=main)](https://dev.azure.com/speediedan/finetuning-scheduler/_build/latest?definitionId=1&branchName=main) |
|     Linux (Ubuntu 20.04)      | [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml) |             [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml)             |
|           OSX (11)            | [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml) |             [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml)             |
|        Windows (2022)         | [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml) |             [![Test](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml/badge.svg?branch=main&event=push)](https://github.com/speediedan/finetuning-scheduler/actions/workflows/ci_test-full.yml)             |

- \*\* tests run on two RTX 2070s

</details>

## Community

Fine-Tuning Scheduler is developed and maintained by the community in close communication with the [Lightning team](https://pytorch-lightning.readthedocs.io/en/latest/governance.html). Thanks to everyone in the community for their tireless effort building and improving the immensely useful core PyTorch Lightning project.

PR's welcome! Please see the [contributing guidelines](https://finetuning-scheduler.readthedocs.io/en/latest/generated/CONTRIBUTING.html) (which are essentially the same as PyTorch Lightning's).

______________________________________________________________________

## Citing Fine-Tuning Scheduler

Please cite:

```tex
@misc{Dan_Dale_2022_6463952,
    author       = {Dan Dale},
    title        = {{Fine-Tuning Scheduler}},
    month        = Feb,
    year         = 2022,
    doi          = {10.5281/zenodo.6463952},
    publisher    = {Zenodo},
    url          = {https://zenodo.org/record/6463952}
    }
```

Feel free to star the repo as well if you find it useful or interesting. Thanks 😊!
