import torch
import torch.nn as nn


class FCN(nn.Module):
    def __init__(self, d_model, n_commands, n_args, args_dim=256, abs_targets=False):
        super().__init__()

        self.n_args = n_args
        self.args_dim = args_dim
        self.abs_targets = abs_targets

        self.command_fcn = nn.Linear(d_model, n_commands)

        if abs_targets:
            self.args_fcn = nn.Linear(d_model, n_args)
        else:
            self.args_fcn = nn.Linear(d_model, n_args * args_dim)

    def forward(self, out):
        S, N, _ = out.shape

        command_logits = self.command_fcn(out)  # Shape [S, N, n_commands]
        args_logits = self.args_fcn(out)       # Shape [S, N, n_args * args_dim]

        if not self.abs_targets:
            args_logits = args_logits.reshape(S, N, self.n_args, self.args_dim)  # Shape [S, N, n_args, args_dim]

        return command_logits, args_logits


class FCN_args(nn.Module):
    def __init__(self, d_model, n_args, args_dim=256, abs_targets=False):
        super().__init__()

        self.n_args = n_args
        self.args_dim = args_dim
        self.abs_targets = abs_targets

        if abs_targets:
            self.args_fcn = nn.Linear(d_model, n_args)
        else:
            self.args_fcn = nn.Linear(d_model, n_args * args_dim)

    def forward(self, out):
        S, N, _ = out.shape

        args_logits = self.args_fcn(out)       # Shape [S, N, n_args * args_dim]

        if not self.abs_targets:
            args_logits = args_logits.reshape(S, N, self.n_args, self.args_dim)  # Shape [S, N, n_args, args_dim]

        return args_logits


class ArgumentFCN(nn.Module):
    def __init__(self, d_model, n_args, args_dim=256, abs_targets=False):
        super().__init__()

        self.n_args = n_args
        self.args_dim = args_dim
        self.abs_targets = abs_targets

        # classification -> regression
        if abs_targets:
            self.args_fcn = nn.Sequential(
                nn.Linear(d_model, n_args * args_dim),
                nn.Linear(n_args * args_dim, n_args)
            )
        else:
            self.args_fcn = nn.Linear(d_model, n_args * args_dim)

    def forward(self, out):
        S, N, _ = out.shape

        args_logits = self.args_fcn(out)  # Shape [S, N, n_args * args_dim]

        if not self.abs_targets:
            args_logits = args_logits.reshape(S, N, self.n_args, self.args_dim)  # Shape [S, N, n_args, args_dim]

        return args_logits


class HierarchFCN(nn.Module):
    def __init__(self, d_model, dim_z):
        super().__init__()

        self.visibility_fcn = nn.Linear(d_model, 2)
        self.z_fcn = nn.Linear(d_model, dim_z)
        # self.visibility_fcn = nn.Linear(dim_z, 2)
        # self.z_fcn = nn.Linear(dim_z, dim_z)

    def forward(self, out):
        G, N, _ = out.shape

        visibility_logits = self.visibility_fcn(out)  # Shape [G, N, 2]
        z = self.z_fcn(out)  # Shape [G, N, dim_z]

        return visibility_logits.unsqueeze(0), z.unsqueeze(0)


class ResNet(nn.Module):
    def __init__(self, d_model):
        super().__init__()

        self.linear1 = nn.Sequential(
            nn.Linear(d_model, d_model), nn.ReLU()
        )
        self.linear2 = nn.Sequential(
            nn.Linear(d_model, d_model), nn.ReLU()
        )
        self.linear3 = nn.Sequential(
            nn.Linear(d_model, d_model), nn.ReLU()
        )
        self.linear4 = nn.Sequential(
            nn.Linear(d_model, d_model), nn.ReLU()
        )

    def forward(self, z):
        z = z + self.linear1(z)
        z = z + self.linear2(z)
        z = z + self.linear3(z)
        z = z + self.linear4(z)

        return z
