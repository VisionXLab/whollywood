# Wholly-WOOD

> [Wholly-WOOD: Wholly Leveraging Diversified-quality Labels for Weakly-supervised Oriented Object Detection](https://arxiv.org/pdf/0)

<!-- [ALGORITHM] -->

## Abstract

<div align=center>
<img src="../../resources/whollywood.png" width="800"/>
</div>

Accurately estimating the orientation of visual objects with compact rotated bounding boxes (RBoxes) has become an increasing demand across applications, which yet challenges existing object detection paradigms that only use horizontal bounding boxes (HBoxes). To equip the detectors with orientation awareness, supervised regression/classification modules are introduced at the high cost of rotation annotation. Meanwhile, some existing datasets with oriented objects are already annotated with horizontal boxes. It becomes attractive yet remains open for how to effectively utilize only horizontal annotations to train an oriented object detector (OOD). We develop Wholly-WOOD, a weakly-supervised OOD framework, capable of wholly leveraging various labeling forms (Points, HBoxes, RBoxes, and their combination) in a unified fashion. By only using HBox for training, our Wholly-WOOD achieves performance very close to that of the RBox-trained counterpart on remote sensing and other areas, which significantly reduces the tedious efforts on labor-intensive annotation for oriented objects.

## Evaluation on DOTA-v1.0

All the commands assume that you are currently in the whollywood folder.
```
cd whollywood
```

### Data preparation

Step 1. Follow the instruction of MMRotate to prepare split_ss_dota. 

Step 2. If you already have split_ss_dota on your disk, create a link:
```
ln -s path/to/split_ss_dota data
```

### HBox-to-RBox

Step 1. Train
```
python tools/train.py configs/whollywood/whollywood-le90_r50_fpn-1x_dota.py
```
Note that you don't need to prepare HBox-annotated DOTA. The RBoxes are automatically converted to HBoxes in the train_pipeline of the config file as dict(type='ConvertBoxType', box_type_mapping=dict(gt_bboxes='hbox')).


Step 2. Test
```
python tools/test.py configs/whollywood/whollywood-le90_r50_fpn-1x_dota.py work_dirs/whollywood-le90_r50_fpn-1x_dota/epoch_12.pth
```
Now you can upload work_dirs/dota/Task1/Task1.zip to the DOTA-v1.0 server to evaluate the accuracy.

### Point-to-RBox

Step 1. Train P2R subnet to get pseudo labels
```
python tools/train.py configs/whollywood/whollywood-le90_r50_fpn-1x_dota-s1.py
```
The pseudo labels are saved to data/split_ss_dota/trainval/pseudo_labels. Note that you don't need to prepare Point-annotated DOTA. The RBoxes are automatically converted to Points in the train_pipeline of the config file as dict(type='RBox2Point', dummy=48, partial=1).

Step 2. Train the detector
```
python tools/train.py configs/whollywood/whollywood-le90_r50_fpn-1x_dota-s2.py
```

Step 3. Test
```
python tools/test.py configs/whollywood/whollywood-le90_r50_fpn-1x_dota-s2.py work_dirs/whollywood-le90_r50_fpn-1x_dota-s2/epoch_12.pth
```
Now you can upload work_dirs/dota/Task1/Task1.zip to the DOTA-v1.0 server to evaluate the accuracy.

## Results and configs

### DOTA1.0

|         Backbone         |      WS       | AP50  | lr schd |  Aug  | Batch Size |                                                                                  Configs                                                                                   |
| :----------------------: | :-----------: | :---: | :-----: | :---: | :--------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| ResNet50 (1024,1024,200) | HBox-to-RBox  | 73.48 |   1x    |   -   |     2      |                                                     [whollywood-le90_r50_fpn-1x_dota](./whollywood-le90_r50_fpn-1x_dota.py)                                                      |
| ResNet50 (1024,1024,200) | Point-to-RBox | 62.63 |   1x    |   -   |     2      |             [whollywood-le90_r50_fpn-1x_dota-s1](./whollywood-le90_r50_fpn-1x_dota-s1.py)<br>[whollywood-le90_r50_fpn-1x_dota-s2](./whollywood-le90_r50_fpn-1x_dota-s1.py)             |
| ResNet50 (1024,1024,200) | HBox-to-RBox  | 78.24 |   1x    | MS+RR |     2      |                                               [whollywood-le90_r50_fpn-ms_rr_1x_dota](./whollywood-le90_r50_fpn-ms_rr_1x_dota.py)                                                |
| ResNet50 (1024,1024,200) | Point-to-RBox | 65.10 |   1x    | MS+RR |     2      | [whollywood-le90_r50_fpn-ms_rr_1x_dota-s1](./whollywood-le90_r50_fpn-ms_rr_1x_dota-s1.py)<br>[whollywood-le90_r50_fpn-ms_rr_1x_dota-s2](./whollywood-le90_r50_fpn-ms_rr_1x_dota-s1.py) |

## Citation
```
@article{yu2025whollywood,
  title={Wholly-WOOD: Wholly Leveraging Diversified-quality Labels for Weakly-supervised Oriented Object Detection}, 
  author={Yi Yu and Xue Yang and Yansheng Li and Zhenjun Han and Feipeng Da and Junchi Yan},
  year={2025},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
}
```
