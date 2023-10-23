import argparse
import math
import os
import random
import shutil
import time

import torch
from torch.utils.data import DataLoader
import numpy as np
from trainer.Recorder import Recorder
from trainer.data_utils import RegnetLoader
from trainer.logger import RegnetLogger
from trainer.criterion import RegnetLoss
from trainer.model import Regnet
# from test import test_checkpoint
from contextlib import redirect_stdout
from trainer.config import _C as config
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wandb
import subprocess
import site

import torch.quantization as quantization

# BASE_DATA_PATH = "/gcs/s2s_data/"

def prepare_dataloaders():
    # Get data, data loaders and collate function ready
    base_path = os.path.dirname(os.path.abspath(__file__))
    base_path = config.BASE_DATA_PATH

    # result = subprocess.run(['ls'], capture_output=True, text=True)
    # print(f"result of ls: {result.stdout}")

    # result = subprocess.run(['pwd'], capture_output=True, text=True)
    # print(f"result of pwd: {result.stdout}")

    # site_packages_path = site.getsitepackages()
    # print(f"the path of the site-packages: {site_packages_path}")

    # cmd = ['ls', '/root/.local/lib/python3.10/site-packages/trainer/']
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # print(result.stdout)

    # with open('/gcs/s2s_data/filelists/processed_test.txt', 'r') as f:
    #     lines = f.readlines()
    #     print(f"The file content is {lines}")

    # training_files_path = os.path.join(base_path, "filelists", "processed_test.txt")
    # test_files_path = os.path.join(base_path, "filelists", "processed_test.txt")
    # trainset = RegnetLoader(config.training_files)
    # valset = RegnetLoader(config.test_files)
    training_files_path = config.training_files
    test_files_path = config.test_files
    trainset = RegnetLoader(training_files_path)
    valset = RegnetLoader(test_files_path)

    train_loader = DataLoader(trainset, num_workers=4, shuffle=True,
                              batch_size=config.batch_size, pin_memory=False,
                              drop_last=True)
    test_loader = DataLoader(valset, num_workers=4, shuffle=False,
                             batch_size=config.batch_size, pin_memory=False)
    return train_loader, test_loader


def test_model(model, criterion, test_loader, epoch, logger, visualization=False):
    model.eval()
    reduced_loss_ = []
    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            model.parse_batch(batch)
            model.forward()
            if visualization:
                for j in range(len(model.fake_B)):
                    plt.figure(figsize=(8, 9))
                    plt.subplot(311)
                    plt.imshow(model.real_B[j].data.cpu().numpy(), 
                                    aspect='auto', origin='lower')
                    plt.title(model.video_name[j]+"_ground_truth")
                    plt.subplot(312)
                    plt.imshow(model.fake_B[j].data.cpu().numpy(), 
                                    aspect='auto', origin='lower')
                    plt.title(model.video_name[j]+"_predict")
                    plt.subplot(313)
                    plt.imshow(model.fake_B_postnet[j].data.cpu().numpy(), 
                                    aspect='auto', origin='lower')
                    plt.title(model.video_name[j]+"_postnet")
                    plt.tight_layout()
                    viz_dir = os.path.join(config.save_dir, "viz", f'epoch_{epoch:05d}')
                    os.makedirs(viz_dir, exist_ok=True)
                    plt.savefig(os.path.join(viz_dir, model.video_name[j]+".jpg"))
                    plt.close()
            loss = criterion((model.fake_B, model.fake_B_postnet), model.real_B)
            reduced_loss = loss.item()
            reduced_loss_.append(reduced_loss)
            if not math.isnan(reduced_loss):
                print("Test loss epoch:{} iter:{} {:.6f} ".format(epoch, i, reduced_loss))
        logger.log_testing(np.mean(reduced_loss_), epoch)
    model.train()


def train():
    torch.manual_seed(config.seed)
    torch.cuda.manual_seed(config.seed)

    model = Regnet()

    criterion = RegnetLoss(config.loss_type)

    logger = RegnetLogger(os.path.join(config.save_dir, 'logs'))

    train_loader, test_loader = prepare_dataloaders()
    # Load checkpoint if one exists
    iteration = 0
    epoch_offset = 0

    if config.checkpoint_path != '':
        model.load_checkpoint(config.checkpoint_path)
        iteration = model.iteration
        iteration += 1  # next iteration is iteration + 1
        epoch_offset = max(0, int(iteration / len(train_loader)))
    config.epoch_count = epoch_offset
    model.setup()

    wandb.login(key=config.wandb_api_key)
    model.train()
    # ================ MAIN TRAINNIG LOOP! ===================
    # for epoch in range(epoch_offset, config.epochs):
    wandb.init(
    project = args.experiment_name,
    entity="ac215-s2s-leo",
    name = args.model_name,
    config = {
      "learning_rate": config.lr,
      "epochs": config.epochs,
      "batch_size": config.batch_size
    })
    for epoch in range(args.epochs):
        print("Epoch: {}".format(epoch))
        for i, batch in enumerate(train_loader):
            start = time.perf_counter()
            model.zero_grad()
            model.parse_batch(batch)
            model.optimize_parameters()
            learning_rate = model.optimizers[0].param_groups[0]['lr']
            loss = criterion((model.fake_B, model.fake_B_postnet), model.real_B)
            reduced_loss = loss.item()

            if not math.isnan(reduced_loss):
                duration = time.perf_counter() - start
                print("epoch:{} iter:{} loss:{:.6f} G:{:.6f} D:{:.6f} D_r-f:{:.6f} G_s:{:.6f} time:{:.2f}s/it".format(
                    epoch, i, reduced_loss, model.loss_G, model.loss_D, (model.pred_real - model.pred_fake).mean(), model.loss_G_silence, duration))
                logger.log_training(model, reduced_loss, learning_rate, duration, iteration)
            iteration += 1

            # YONG: moved the logging inside to make the WandB update more frequently
            wandb.log({"reduced_loss": reduced_loss,
                   "loss_G": model.loss_G,
                   "loss_D": model.loss_D})
        # wandb.log({"reduced_loss": reduced_loss,
        #            "loss_G": model.loss_G,
        #            "loss_D": model.loss_D})
        if epoch % config.num_epoch_save != 0:
            test_model(model, criterion, test_loader, epoch, logger)
        if epoch % config.num_epoch_save == 0:
            print("evaluation and save model")
            test_model(model, criterion, test_loader, epoch, logger, visualization=True)
            model.save_checkpoint(config.save_dir, iteration)

        model.update_learning_rate()
    model_path = model.save_checkpoint(config.save_dir, iteration)
    wandb.run.finish()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file', type=str, default='',
                        help='file for configuration')
    parser.add_argument("opts", default=None, nargs=argparse.REMAINDER)
    parser.add_argument("--wandb_key", dest="wandb_key", default="16", type=str, help="WandB API Key")
    parser.add_argument(
    "--model_name",
    dest="model_name",
    default="RegNet",
    type=str,
    help="Model name")
    parser.add_argument("--epochs", dest="epochs", default=50, type=int, help="Number of epochs.")
    parser.add_argument("--batch_size", dest="batch_size", default=1, type=int, help="Size of a batch.")
    parser.add_argument("--lr", dest="lr", default=0.0002, type=float, help="Learning rate.")
    parser.add_argument("--experiment_name", dest="experiment_name", default='experiment_regnet', type=str, help="Experiment's name on W&B.")
    args = parser.parse_args()

    # update config.py
    config.epochs = args.epochs
    config.batch_size = args.batch_size
    config.lr = args.lr

    if args.config_file:
        config.merge_from_file(args.config_file)
 
    # config.merge_from_list(args.opts)
    # config.freeze()

    # os.makedirs(config.save_dir, exist_ok=True)
    # with open(os.path.join(config.save_dir, 'opts.yml'), 'w') as f:
    #     with redirect_stdout(f): 
    #         print(config.dump())
    # f.close()

    # recorder = Recorder(config.save_dir, config.exclude_dirs)

    torch.backends.cudnn.enabled = config.cudnn_enabled
    torch.backends.cudnn.benchmark = config.cudnn_benchmark
    print("Dynamic Loss Scaling:", config.dynamic_loss_scaling)
    print("cuDNN Enabled:", config.cudnn_enabled)
    print("cuDNN Benchmark:", config.cudnn_benchmark)
    print("one line before train")

    train()
