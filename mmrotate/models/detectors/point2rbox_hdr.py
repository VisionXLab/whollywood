# Copyright (c) OpenMMLab. All rights reserved.
import copy
import math
from typing import Tuple, Union

import torch
from mmdet.models.detectors.single_stage import SingleStageDetector
from mmdet.models.utils import unpack_gt_instances
from mmdet.structures import DetDataSample, SampleList
from mmdet.structures.bbox import get_box_tensor
from mmdet.utils import ConfigType, InstanceList, OptConfigType, OptMultiConfig
from mmengine.structures import InstanceData
from torch import Tensor
from torch.nn.functional import grid_sample
from torchvision import transforms
import torch.nn.functional as F

from mmrotate.models.task_modules.synthesis_generators import \
    point2rbox_generator
from mmrotate.registry import MODELS
from mmrotate.structures.bbox import RotatedBoxes, rbox2hbox, hbox2rbox


@MODELS.register_module()
class Point2RBoxHDR(SingleStageDetector):
    r"""Implementation of `Point2RBox
    <https://arxiv.org/abs/2311.14758>`_

    Args:
        backbone (:obj:`ConfigDict` or dict): The backbone module.
        neck (:obj:`ConfigDict` or dict): The neck module.
        bbox_head (:obj:`ConfigDict` or dict): The bbox head module.
        train_cfg (:obj:`ConfigDict` or dict, optional): The training config
            of YOLOF. Defaults to None.
        test_cfg (:obj:`ConfigDict` or dict, optional): The testing config
            of YOLOF. Defaults to None.
        data_preprocessor (:obj:`ConfigDict` or dict, optional):
            Model preprocessing config for processing the input data.
            it usually includes ``to_rgb``, ``pad_size_divisor``,
            ``pad_value``, ``mean`` and ``std``. Defaults to None.
        init_cfg (:obj:`ConfigDict` or dict, optional): the config to control
            the initialization. Defaults to None.
    """

    def __init__(self,
                 backbone: ConfigType,
                 neck: ConfigType,
                 bbox_head: ConfigType,
                 crop_size: Tuple[int, int] = (1024, 1024),
                 padding: str = 'reflection',
                 rot_range: Tuple[float, float] = (0.25, 0.75),
                 sca_range: Tuple[float, float] = (0.5, 1.5),
                 sca_fact: float = 1.0,
                 prob_rot: float = 0.95 * 0.7,
                 prob_flp: float = 0.05 * 0.7,
                 basic_pattern: str = 'data/dota',
                 dense_cls: list = [],
                 square_cls: list = [],
                 use_synthesis: bool = True,
                 use_setrc: bool = True,
                 use_setsk: bool = True,
                 debug: bool = False,
                 train_cfg: OptConfigType = None,
                 test_cfg: OptConfigType = None,
                 data_preprocessor: OptConfigType = None,
                 init_cfg: OptMultiConfig = None) -> None:
        super().__init__(
            backbone=backbone,
            neck=neck,
            bbox_head=bbox_head,
            train_cfg=train_cfg,
            test_cfg=test_cfg,
            data_preprocessor=data_preprocessor,
            init_cfg=init_cfg)

        self.crop_size = crop_size
        self.padding = padding
        self.rot_range = rot_range
        self.sca_range = sca_range
        self.sca_fact = sca_fact
        self.prob_rot = prob_rot
        self.prob_flp = prob_flp
        self.basic_pattern = basic_pattern
        self.dense_cls = dense_cls
        self.square_cls = square_cls
        self.use_synthesis = use_synthesis
        self.debug = debug
        self.basic_pattern = point2rbox_generator.load_basic_pattern(
            self.basic_pattern, use_setrc, use_setsk)

    def rotate_crop(
            self,
            batch_inputs: Tensor,
            rot: float = 0.,
            size: Tuple[int, int] = (768, 768),
            batch_gt_instances: InstanceList = None,
            padding: str = 'reflection') -> Tuple[Tensor, InstanceList]:
        """

        Args:
            batch_inputs (Tensor): Input images of shape (N, C, H, W).
                These should usually be mean centered and std scaled.
            rot (float): Angle of view rotation. Defaults to 0.
            size (tuple[int]): Crop size from image center.
                Defaults to (768, 768).
            batch_gt_instances (list[:obj:`InstanceData`]): Batch of
                gt_instance.  It usually includes ``bboxes`` and ``labels``
                attributes.
            padding (str): Padding method of image black edge.
                Defaults to 'reflection'.

        Returns:
            Processed batch_inputs (Tensor) and batch_gt_instances
            (list[:obj:`InstanceData`])
        """
        device = batch_inputs.device
        n, c, h, w = batch_inputs.shape
        size_h, size_w = size
        crop_h = (h - size_h) // 2
        crop_w = (w - size_w) // 2
        if rot != 0:
            cosa, sina = math.cos(rot), math.sin(rot)
            tf = batch_inputs.new_tensor([[cosa, -sina], [sina, cosa]],
                                         dtype=torch.float)
            x_range = torch.linspace(-1, 1, w, device=device)
            y_range = torch.linspace(-1, 1, h, device=device)
            y, x = torch.meshgrid(y_range, x_range)
            grid = torch.stack([x, y], -1).expand([n, -1, -1, -1])
            grid = grid.reshape(-1, 2).matmul(tf).view(n, h, w, 2)
            # rotate
            batch_inputs = grid_sample(
                batch_inputs, grid, 'bilinear', padding, align_corners=True)
            if batch_gt_instances is not None:
                for i, gt_instances in enumerate(batch_gt_instances):
                    gt_bboxes = get_box_tensor(gt_instances.bboxes)
                    xy, wh, a = gt_bboxes[..., :2], gt_bboxes[
                        ..., 2:4], gt_bboxes[..., [4]]
                    ctr = tf.new_tensor([[w / 2, h / 2]])
                    xy = (xy - ctr).matmul(tf.T) + ctr
                    a = a + rot
                    rot_gt_bboxes = torch.cat([xy, wh, a], dim=-1)
                    batch_gt_instances[i].bboxes = RotatedBoxes(rot_gt_bboxes)
        batch_inputs = batch_inputs[..., crop_h:crop_h + size_h,
                                    crop_w:crop_w + size_w]
        if batch_gt_instances is None:
            return batch_inputs
        else:
            for i, gt_instances in enumerate(batch_gt_instances):
                gt_bboxes = get_box_tensor(gt_instances.bboxes)
                xy, wh, a = gt_bboxes[..., :2], gt_bboxes[...,
                                                          2:4], gt_bboxes[...,
                                                                          [4]]
                xy = xy - xy.new_tensor([[crop_w, crop_h]])
                crop_gt_bboxes = torch.cat([xy, wh, a], dim=-1)
                batch_gt_instances[i].bboxes = RotatedBoxes(crop_gt_bboxes)

            return batch_inputs, batch_gt_instances
        
    def add_synthesis(self, batch_inputs, batch_gt_instances):

        def synthesis_single(img, bboxes, labels):
            labels = labels[:, None]
            bb = torch.cat((bboxes, torch.ones_like(labels), labels), -1)
            img, bb = point2rbox_generator.generate_sythesis(
                img, bb, self.sca_fact, *self.basic_pattern, self.dense_cls,
                self.crop_size[0])
            instance_data = InstanceData()
            instance_data.labels = bb[:, 6].long()
            square_mask = torch.zeros_like(bb[:, 6], dtype=torch.bool)
            for c in self.square_cls:
                square_mask = torch.logical_or(square_mask, bb[:, 6].long() == c)
            bb[square_mask, 4] = 0
            if hasattr(self.bbox_head, 'use_hbox_output') and self.bbox_head.use_hbox_output:
                instance_data.bboxes = hbox2rbox(rbox2hbox(bb[:, :5]))
            else:
                instance_data.bboxes = bb[:, :5]
            return img, instance_data

        p = ((synthesis_single)(img, gt.bboxes.cpu(), gt.labels.cpu())
             for (img, gt) in zip(batch_inputs.cpu(), batch_gt_instances))

        img, instance_data = zip(*p)
        batch_inputs = torch.stack(img, 0).to(batch_inputs)
        instance_data = list(instance_data)
        for i, gt in enumerate(instance_data):
            gt.labels = gt.labels.to(batch_gt_instances[i].labels)
            gt.bboxes = gt.bboxes.to(batch_gt_instances[i].bboxes)
            batch_gt_instances[i] = InstanceData.cat(
                [batch_gt_instances[i], gt])

        return batch_inputs, batch_gt_instances

    def loss(self, batch_inputs: Tensor,
             batch_data_samples: SampleList) -> Union[dict, list]:
        """Calculate losses from a batch of inputs and data samples.

        Args:
            batch_inputs (Tensor): Input images of shape (N, C, H, W).
                These should usually be mean centered and std scaled.
            batch_data_samples (list[:obj:`DetDataSample`]): The batch
                data samples. It usually includes information such
                as `gt_instance` or `gt_panoptic_seg` or `gt_sem_seg`.

        Returns:
            dict: A dictionary of loss components.
        """
        batch_gt_instances, _, _ = unpack_gt_instances(batch_data_samples)
        batch_metainfo = batch_data_samples[0].metainfo

        # Generate synthetic objects
        if self.use_synthesis:
            batch_inputs, batch_gt_instances = self.add_synthesis(
                batch_inputs, batch_gt_instances)

        if hasattr(self.bbox_head, 'use_transform_ss') and self.bbox_head.use_transform_ss:
            # Crop original images and gts
            batch_inputs, batch_gt_instances = self.rotate_crop(
                batch_inputs, 0, self.crop_size, batch_gt_instances,
                self.padding)
            offset = 1
            for gt_instances in batch_gt_instances:
                gt_instances.bids = torch.arange(
                    0,
                    len(gt_instances.bboxes),
                    1,
                    device=gt_instances.bboxes.device) + offset + 0.2
                offset += len(gt_instances.bboxes)

            # Concat original/rotated/flipped images and gts
            p = torch.rand(1)
            if p < self.prob_rot:  # rot
                # Generate rotated images and gts
                rot = math.pi * (
                    torch.rand(1, device=batch_inputs.device) *
                    (self.rot_range[1] - self.rot_range[0]) +
                    self.rot_range[0])
                batch_metainfo['ss'] = ('rot', rot)
                batch_gt_rot = copy.deepcopy(batch_gt_instances)
                batch_inputs_rot, batch_gt_rot = self.rotate_crop(
                    batch_inputs, rot, self.crop_size, batch_gt_rot,
                    self.padding)
                offset = 1
                for gt_instances in batch_gt_rot:
                    gt_instances.bids = torch.arange(
                        0,
                        len(gt_instances.bboxes),
                        1,
                        device=gt_instances.bboxes.device) + offset + 0.4
                    offset += len(gt_instances.bboxes)
                batch_inputs_all = torch.cat((batch_inputs, batch_inputs_rot))
                batch_gt_instances_all = batch_gt_instances + batch_gt_rot
            elif p < self.prob_rot + self.prob_flp:  # flp
                # Generate flipped images and gts
                batch_metainfo['ss'] = ('flp', 0)
                batch_inputs_flp = transforms.functional.vflip(batch_inputs)
                batch_gt_flp = copy.deepcopy(batch_gt_instances)
                offset = 1
                for gt_instances in batch_gt_flp:
                    gt_instances.bboxes.flip_(batch_inputs.shape[2:4],
                                              'vertical')
                    gt_instances.bids = torch.arange(
                        0,
                        len(gt_instances.bboxes),
                        1,
                        device=gt_instances.bboxes.device) + offset + 0.6
                    offset += len(gt_instances.bboxes)
                batch_inputs_all = torch.cat((batch_inputs, batch_inputs_flp))
                batch_gt_instances_all = batch_gt_instances + batch_gt_flp
            else:  # sca
                # Generate scaled images and gts
                sca = torch.rand(
                    1, device=batch_inputs.device
                ) * (self.sca_range[1] - self.sca_range[0]) + self.sca_range[0]
                batch_metainfo['ss'] = ('sca', sca)
                size = (self.crop_size[0] / sca).long()
                batch_inputs_sca = transforms.functional.resized_crop(
                    batch_inputs,
                    0,
                    0,
                    size,
                    size,
                    self.crop_size,
                    antialias=False)
                batch_gt_sca = copy.deepcopy(batch_gt_instances)
                offset = 1
                for gt_instances in batch_gt_sca:
                    boxes = gt_instances.bboxes.tensor
                    if hasattr(self.bbox_head, 'point_dummy'):
                        # Keep dummy value during resize
                        point_dummy = self.bbox_head.point_dummy
                        mask = torch.logical_and(boxes[..., 2] == point_dummy,
                                    boxes[..., 3] == point_dummy)
                        gt_instances.bboxes.tensor[:, 0:2] *= sca
                        gt_instances.bboxes.tensor[~mask, 2:4] *= sca
                    else:
                        gt_instances.bboxes.tensor[:, 0:4] *= sca
                    gt_instances.bids = torch.arange(
                        0,
                        len(gt_instances.bboxes),
                        1,
                        device=gt_instances.bboxes.device) + offset + 0.8
                    offset += len(gt_instances.bboxes)
                batch_inputs_all = torch.cat((batch_inputs, batch_inputs_sca))
                batch_gt_instances_all = batch_gt_instances + batch_gt_sca

            batch_gt_instances_filtered = []
            for gt_instances in batch_gt_instances_all:
                H = self.crop_size[0]
                D = 16
                ignore_mask = torch.logical_or(
                    gt_instances.bboxes.tensor[:, :2].min(1)[0] < D,
                    gt_instances.bboxes.tensor[:, :2].max(1)[0] > H - D)
                gt_instances_filtered = InstanceData()
                gt_instances_filtered.bboxes = RotatedBoxes(
                    gt_instances.bboxes.tensor[~ignore_mask])
                gt_instances_filtered.labels = gt_instances.labels[
                    ~ignore_mask]
                gt_instances_filtered.bids = gt_instances.bids[~ignore_mask]
                batch_gt_instances_filtered.append(gt_instances_filtered)

            batch_data_samples_all = []
            for gt_instances in batch_gt_instances_filtered:
                data_sample = DetDataSample(
                    metainfo=batch_metainfo)
                data_sample.gt_instances = gt_instances
                batch_data_samples_all.append(data_sample)

        else:
            offset = 1
            for gt_instances in batch_gt_instances:
                gt_instances.bids = torch.arange(
                    0,
                    len(gt_instances.bboxes),
                    1,
                    device=gt_instances.bboxes.device) + offset + 0.2
                offset += len(gt_instances.bboxes)

            batch_inputs_all = batch_inputs
            batch_data_samples_all = []
            for gt_instances in batch_gt_instances:
                data_sample = DetDataSample(
                    metainfo=batch_metainfo)
                gt_instances.bboxes = RotatedBoxes(gt_instances.bboxes)
                data_sample.gt_instances = gt_instances
                batch_data_samples_all.append(data_sample)

        # Plot
        if self.debug:
            import cv2
            import numpy as np
            idx = np.random.randint(100)
            B = batch_inputs.shape[0]
            batch_inputs_plot = batch_inputs_all[::B]
            batch_data_samples_plot = batch_data_samples_all[::B]
            for i in range(len(batch_inputs_plot)):
                img = batch_inputs_plot[i].permute(1, 2, 0).cpu().numpy()
                img = np.ascontiguousarray(img[..., (2, 1, 0)] * 58 + 127)
                bb = batch_data_samples_plot[i].gt_instances.bboxes.tensor
                if hasattr(self.bbox_head, 'point_dummy'):
                    point_dummy = self.bbox_head.point_dummy
                    mask = torch.logical_and(bb[..., 2] == point_dummy,
                                bb[..., 3] == point_dummy)
                    bb[mask, 2:4] = 3
                for b in bb.cpu().numpy():
                    point2rbox_generator.plot_one_rotated_box(img, b)
                cv2.imwrite(f'{idx}-{i}.png', img)
                
                # img = batch_inputs_plot[i].cpu()[None]
                # labels = batch_data_samples_plot[i].gt_instances.labels
                # for b, l in zip(bb.cpu().numpy(), labels.cpu().numpy()):
                #     cls = l

                #     def obb2poly(obb):
                #         cx, cy, w, h, t = obb
                #         dw, dh = (w - 1) / 2, (h - 1) / 2
                #         cost = np.cos(t)
                #         sint = np.sin(t)
                #         mrot = np.float32([[cost, -sint], [sint, cost]])
                #         poly = np.float32([[-dw, -dh], [dw, -dh], [dw, dh], [-dw, dh]])
                #         return np.matmul(poly, mrot.T) + np.float32([cx, cy])

                #     poly = obb2poly(b)
                #     pts1 = poly[0:3]
                #     pts2 = np.float32([[-1, -1], [1, -1], [1, 1]])
                #     M = cv2.getAffineTransform(pts1, pts2)
                #     M = np.concatenate((M, ((0, 0, 1),)), 0)

                #     H, W = img.shape[2:4]
                #     T = np.array([[2 / W, 0, -1],
                #                 [0, 2 / H, -1],
                #                 [0, 0, 1]])
                #     theta = T @ np.linalg.inv(M)
                #     theta = torch.from_numpy(theta[:2, :]).unsqueeze(0).type(torch.float32)
                #     grid = F.affine_grid(theta, [1, 3, int(b[3] + 1), int(b[2] + 1)], align_corners=True)
                #     img_chip = F.grid_sample(img, grid, align_corners=True)
                #     img_chip = img_chip[0].permute(1, 2, 0).numpy()
                #     img_chip = np.ascontiguousarray(img_chip[..., (2, 1, 0)] * 58 + 127)
                #     img_chip = img_chip.sum(axis=-1) / 3
                #     cv2.imwrite(f'patterns/{cls}.png', img_chip)

        feat = self.extract_feat(batch_inputs_all)
        losses = self.bbox_head.loss(feat, batch_data_samples_all)

        return losses
