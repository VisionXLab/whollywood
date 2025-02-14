<p align="center">
  <h1 align="center">Wholly-WOOD: Wholly Leveraging Diversified-quality Labels for Weakly-supervised Oriented Object Detection</h1>
  <p align="center">
    <a href='https://scholar.google.com/citations?user=OYtSc4AAAAAJ' style='text-decoration: none' >Yi Yu</a><sup></sup>&ensp; 
    <a href='https://yangxue0827.github.io/' style='text-decoration: none' >Xue Yang</a><sup></sup>&ensp;
    <a href='https://scholar.google.com/citations?user=wn9hc6UAAAAJ' style='text-decoration: none' >Yansheng Li</a><sup></sup>&ensp;   
    <a href='https://scholar.google.com/citations?user=0rK4yTcAAAAJ' style='text-decoration: none' >Zhenjun Han</a><sup></sup>&ensp;
    <a href='' style='text-decoration: none' >Feipeng Da</a><sup></sup>&ensp;
    <a href='https://scholar.google.com/citations?user=ga230VoAAAAJ&hl=en' style='text-decoration: none' >Junchi Yan</a><sup></sup>&ensp; 
    <div align="center">
      <a href='https://arxiv.org/abs/2502.09471'><img src='https://img.shields.io/badge/arXiv-2502.09471-brown.svg?logo=arxiv&logoColor=white'></a>
    </div>
    <p align='center'>
      If you find our work helpful, please consider giving us a ⭐!
    </p>
  </p>
</p>

## Introduction
We develop **Wholly-WOOD** (**Wholly** Leveraging Diversified-quality Labels for **W**eakly-supervised **O**riented **O**bject **D**etection), a weakly-supervised OOD framework, capable of wholly leveraging various labeling forms (Points, HBoxes, RBoxes, and their combination) in a unified fashion. By only using HBox for training, our Wholly-WOOD achieves performance very close to that of the RBox-trained counterpart on remote sensing and other areas, which significantly reduces the tedious efforts on labor-intensive annotation for oriented objects.

This project is the implementation of Wholly-WOOD. The code works with **PyTorch 1.13+** and it is forked from [MMRotate dev-1.x](https://github.com/open-mmlab/mmrotate/tree/dev-1.x). MMRotate is an open-source toolbox for rotated object detection based on PyTorch. It is a part of the [OpenMMLab project](https://github.com/open-mmlab).

**Note: Our new work [Point2RBox-v2](https://github.com/VisionXLab/point2rbox-v2) is released, which also contains our series of work including Wholly-WOOD. This repository will remain as a record of the original Wholly-WOOD implementation.**

## Installation
Please refer to [Installation](https://mmrotate.readthedocs.io/en/1.x/get_started.html) for more detailed instruction.

## Getting Started
Please see [Overview](https://mmrotate.readthedocs.io/en/1.x/overview.html) for the general introduction of MMRotate. 

For detailed user guides and advanced guides, please refer to MMRotate's [documentation](https://mmrotate.readthedocs.io/en/1.x/).

The examples of training and testing Wholly-WOOD can be found [here](configs/whollywood/README.md).

## Model Zoo
This repository contains the Wholly-WOOD model and our series of work on weakly-supervised OOD (i.e. H2RBox, H2RBox-v2, and Point2RBox).

<details open>
<summary><b>Supported algorithms:</b></summary>

- [x] [Wholly-WOOD](configs/whollywood/README.md)
- [x] [Point2RBox](configs/point2rbox/README.md)
- [x] [H2RBox-v2](configs/h2rbox_v2/README.md)
- [x] [H2RBox](configs/h2rbox/README.md)

</details>

## Data Preparation
Please refer to [data_preparation.md](tools/data/README.md) to prepare the data.

## FAQ
Please refer to [FAQ](docs/en/notes/faq.md) for frequently asked questions.

## Acknowledgement
This project is based on MMRotate, an open source project that is contributed by researchers and engineers from various colleges and companies. We appreciate all the contributors who implement their methods or add new features, as well as users who give valuable feedbacks. We appreciate the [Student Innovation Center of SJTU](https://www.si.sjtu.edu.cn/) for providing rich computing resources at the beginning of the project. We wish that the toolbox and benchmark could serve the growing research community by providing a flexible toolkit to reimplement existing methods and develop their own new methods.

## Citation
```
@article{yu2025whollywood,
  title={Wholly-WOOD: Wholly Leveraging Diversified-quality Labels for Weakly-supervised Oriented Object Detection}, 
  author={Yi Yu and Xue Yang and Yansheng Li and Zhenjun Han and Feipeng Da and Junchi Yan},
  year={2025},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
}
```

