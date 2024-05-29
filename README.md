## Introduction

This project is the implementation of **Wholly-WOOD** (**Wholly** Leveraging Diversified-quality Labels for **W**eakly-supervised **O**riented **O**bject **D**etection).

The code works with **PyTorch 1.13+** and it is forked from [MMRotate dev-1.x](https://github.com/open-mmlab/mmrotate/tree/dev-1.x). MMRotate is an open-source toolbox for rotated object detection based on PyTorch. It is a part of the [OpenMMLab project](https://github.com/open-mmlab).

### Highlight

We are excited to announce our latest work on oriented object detection tasks, **Wholly-WOOD**, a weakly-supervised OOD framework, capable of wholly leveraging various labeling forms (Points, HBoxes, RBoxes, and their combination) in a unified fashion. By only using HBox for training, Wholly-WOOD achieves performance very close to that of the RBox-trained counterpart on remote sensing and other areas, which significantly reduces the tedious efforts on labor-intensive annotation for oriented objects. Details can be found in our [paper](https://arxiv.org/abs/0).

## Installation

Please refer to [Installation](https://mmrotate.readthedocs.io/en/1.x/get_started.html) for more detailed instruction.

## Getting Started

Please see [Overview](https://mmrotate.readthedocs.io/en/1.x/overview.html) for the general introduction of MMRotate. 

For detailed user guides and advanced guides, please refer to MMRotate's [documentation](https://mmrotate.readthedocs.io/en/1.x/).

The examples of training and testing Wholly-WOOD can be found [here](configs/whollywood/README.md).

## Model Zoo

Results and models are available in the *README.md* of each method's config directory.
A summary can be found in the [Model Zoo](docs/en/model_zoo.md) page.

<details open>
<summary><b>Supported algorithms:</b></summary>

- [x] [Wholly-WOOD](configs/whollywood/README.md)

</details>

## Data Preparation

Please refer to [data_preparation.md](tools/data/README.md) to prepare the data.

## FAQ

Please refer to [FAQ](docs/en/notes/faq.md) for frequently asked questions.

## Acknowledgement

This project is based on MMRotate, an open source project that is contributed by researchers and engineers from various colleges and companies. We appreciate all the contributors who implement their methods or add new features, as well as users who give valuable feedbacks. We appreciate the [Student Innovation Center of SJTU](https://www.si.sjtu.edu.cn/) for providing rich computing resources at the beginning of the project. We wish that the toolbox and benchmark could serve the growing research community by providing a flexible toolkit to reimplement existing methods and develop their own new methods.

## Citation

Coming soon

## License

This project is released under the [Apache 2.0 license](LICENSE).
