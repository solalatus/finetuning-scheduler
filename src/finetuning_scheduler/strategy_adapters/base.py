# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""
Fine-Tuning Scheduler Strategy Adapters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Base adapter class to extend Fine-Tuning Scheduler support of complex or custom training strategies.

"""
from typing import Callable, List, Optional, Tuple

from lightning_fabric.utilities import rank_zero_info
from lightning_fabric.utilities.types import ReduceLROnPlateau
from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.callbacks import Callback
from pytorch_lightning.strategies.strategy import Strategy
from pytorch_lightning.utilities.rank_zero import rank_zero_debug
from torch.nn import Module


class StrategyAdapter:
    r"""Base class for all strategy adapters. Implements the default
    :class:`~finetuning_scheduler.fts.FinetuningScheduler` hooks. Can be subclassed to extend
    :class:`~finetuning_scheduler.fts.FinetuningScheduler` support for a complex or custom
    :external+pl:class:`~pytorch_lightning.strategies.Strategy` via an associated
    :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter`.

    .. warning::

        :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` is in BETA and subject to change. The interface
        can bring breaking changes and new features with the next release of FTS.

    .. tip::

        If you want to extend FTS to use a custom, currently unsupported strategy or override current FTS behavior in
        the context of a given training strategy, subclassing
        :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` is a way to do so. See
        :class:`~finetuning_scheduler.strategy_adapters.FSDPStrategyAdapter` for an example implementation.

    """

    fts_handle: Callback

    def __init__(self) -> None:
        """The default fine-tuning phase execution function is set on
        :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` initialization. This can be overridden by
        :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` subclasses to adapt fine-tuning phase
        execution to meet strategy-specific requirements.
        """
        self.exec_ft_phase = StrategyAdapter.base_ft_phase

    def connect(self, fts_parent: Callback) -> None:
        """Create a handle for the associated :class:`~finetuning_scheduler.fts.FinetuningScheduler` instance.

        Args:
            fts_parent (Callback): The associated :class:`~finetuning_scheduler.fts.FinetuningScheduler` instance
        """
        self.fts_handle = fts_parent

    @property
    def pl_module(self) -> LightningModule:
        """Convenient access to the :external+pl:class:`~pytorch_lightning.core.module.LightningModule` being fine-
        tuned.

        Returns:
            LightningModule: The user's :external+pl:class:`~pytorch_lightning.core.module.LightningModule`
        """
        return self.fts_handle.pl_module

    @property
    def pls_handle(self) -> Strategy:
        """Convenient access to the current :external+pl:class:`~pytorch_lightning.strategies.Strategy` in use.

        Returns:
            Strategy: The :external+pl:class:`~pytorch_lightning.strategies.Strategy` in use.
        """
        assert self.pl_module._trainer is not None
        return self.pl_module._trainer.strategy

    def on_before_init_fts(self) -> None:
        """Hook executed in :class:`~finetuning_scheduler.fts.FinetuningScheduler` setup immediately before
        :meth:`~finetuning_scheduler.fts_supporters.ScheduleImplMixin.init_fts`
        """

    def on_after_init_fts(self) -> None:
        """Hook executed in :class:`~finetuning_scheduler.fts.FinetuningScheduler` setup immediately after
        :meth:`~finetuning_scheduler.fts_supporters.ScheduleImplMixin.init_fts`.
        """
        _, self.fts_handle._fts_state._curr_thawed_params = self.exec_ft_phase(
            self.pl_module,
            thaw_pl=self.fts_optim_view(self.fts_handle.ft_schedule[0]["params"]),
            init_thaw=True,
        )

    def on_before_fts_fit_start(self) -> None:
        """Hook executed immediately before the :class:`~finetuning_scheduler.fts.FinetuningScheduler`
        :meth:`~finetuning_scheduler.fts.on_fit_start` hook begins.
        """

    def on_before_restore_optimizers_and_lrs(self) -> None:
        """Hook executed immediately before :class:`~finetuning_scheduler.fts.FinetuningScheduler` restores
        optimizers and schedulers."""

    def fts_optim_view(self, orig_pl: List) -> List:
        """A method that can be overridden by a :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` if
        a.

        :external+pl:class:`~pytorch_lightning.strategies.Strategy` performs parameter transformations that cause the
        current :external+torch:class:`~torch.optim.Optimizer`'s view of parameter names to diverge from the original
        parameter names.
        By default, no transformation of schedule parameter names is required for optimizer operations.

        Args:
            orig_pl (List): The original parameter name list before a given
                :external+pl:class:`~pytorch_lightning.strategies.Strategy`'s transformation of them.

        Returns:
            List: A transformed parameter name list that matches the current
                :external+torch:class:`~torch.optim.Optimizer`'s view of them after a given
                :external+pl:class:`~pytorch_lightning.strategies.Strategy`'s transformation of the original parameter
                names.
        """
        return orig_pl

    def logical_param_translation(self, param_names: List) -> List:
        """Effectively the reverse transformation of
        :meth:`~finetuning_scheduler.strategy_adapters.StrategyAdapter.fts_optim_view`. Can be overridden by a
        :class:`~finetuning_scheduler.strategy_adapters.StrategyAdapter` if a
        :external+pl:class:`~pytorch_lightning.strategies.Strategy` performs parameter transformations that cause the
        original user view of parameter names to diverge from the current
        :external+torch:class:`~torch.optim.Optimizer`'s view. By default, no transformation of
        :external+torch:class:`~torch.optim.Optimizer` parameter names is required.

        Args:
            param_names (List): A parameter name list from the current :external+torch:class:`~torch.optim.Optimizer`'s
                view of them after a :external+pl:class:`~pytorch_lightning.strategies.Strategy`'s transformation of the
                original parameter names.

        Returns:
            List: The original parameter name list before a given
                :external+pl:class:`~pytorch_lightning.strategies.Strategy`'s transformation.
        """
        return param_names

    @staticmethod
    def _clean_optim_lr_pgs(trainer: Trainer) -> List:
        """Delete existing param groups from an optimizer that was found to be misaligned with respect to phase 0
        of the specified fine-tuning schedule.

        Args:
            trainer (Trainer): The :external+pl:class:`~pytorch_lightning.trainer.trainer.Trainer` object.

        Returns:
            List: A list of the number of parameter groups pruned for each optimizer (since only a single optimizer is
                currently supported by FTS, this list will have only a single element in this verison.)
        """
        orig_num_pgs = []
        for optimizer in trainer.optimizers:
            orig_num_pgs.append(len(optimizer.param_groups))
            optimizer.param_groups = []
        for lrs_cfg in trainer.lr_scheduler_configs:
            lrs_cfg.scheduler.base_lrs = []
        return orig_num_pgs

    def phase0_optimizer_override(self) -> None:
        """Reconfigure the user-configured optimizer (configured via `configure_optimizers`) to optimize the
        parameters (and only those parameters) scheduled to be optimized in phase 0 of the current fine-tuning
        schedule.

        Reconfiguration only takes place here if FTS discovers the set of parameters to be initially thawed and present
        in the optimizer differs from the parameters specified in phase 0. Only the parameters included in the optimizer
        are affected; the choice of optimizer, lr_scheduler etc. remains unaltered.
        """
        trainer = self.pl_module.trainer
        orig_num_pgs = StrategyAdapter._clean_optim_lr_pgs(trainer)
        # refreeze in case user has thawed parameters not present in phase 0
        self.fts_handle.freeze_before_training(self.pl_module)
        # thaw only params scheduled in phase 0
        self.fts_handle.step_pg(depth=self.fts_handle.curr_depth, optimizer=trainer.optimizers[0], depth_sync=False)
        # since we may have added parameter groups (e.g. implementing ``no_decay`` for user), we need to reinitialize
        # certain lr_scheduler variables (including type-dependent ones like ``min_lrs`` and ``lr_lambdas``)
        for lrs_cfg in trainer.lr_scheduler_configs:
            lrs_cfg.scheduler._last_lr = [group["lr"] for group in lrs_cfg.scheduler.optimizer.param_groups]
            assert lrs_cfg.opt_idx is not None
            if isinstance(lrs_cfg.scheduler, ReduceLROnPlateau):
                lrs_cfg.scheduler.min_lrs = lrs_cfg.scheduler.min_lrs[orig_num_pgs[lrs_cfg.opt_idx] :]
            elif hasattr(lrs_cfg.scheduler, "lr_lambdas"):
                lrs_cfg.scheduler.lr_lambdas = lrs_cfg.scheduler.lr_lambdas[orig_num_pgs[lrs_cfg.opt_idx] :]
        p0_override_msg = self.fts_handle.PHASE_0_DIVERGENCE_MSG + (
            "Since `enforce_phase0_params` is currently set to `True` (the default), FinetuningScheduler has"
            " reconfigured the optimizer to optimize the parameters (and only those parameters) scheduled to be"
            " optimized in phase 0 of the current fine-tuning schedule.\n\n"
        )
        rank_zero_info(p0_override_msg)

    @staticmethod
    def base_ft_phase(
        module: Module, thaw_pl: List, translation_func: Optional[Callable] = None, init_thaw: bool = False
    ) -> Tuple[List, List]:
        """Thaw/unfreeze the provided list of parameters in the provided :class:`~torch.nn.Module`

        Args:
            module (:class:`~torch.nn.Module`): The :class:`~torch.nn.Module` that will have parameters selectively
                unfrozen/thawed.
            thaw_pl: The list of parameters that should be thawed/unfrozen in the :class:`~torch.nn.Module`
            init_thaw: If ``True``, modifies message to user accordingly. Defaults to ``False``.

        Returns:
            Tuple[List, List]: A Tuple of two lists.
                1. The list of newly thawed/unfrozen parameters thawed by this function
                2. A list of all currently thawed/unfrozen parameters in the target :class:`~torch.nn.Module`
        """
        thawed_p_names = []
        curr_thawed = []
        for n, p in module.named_parameters():
            if not p.requires_grad and n in thaw_pl:
                p.requires_grad = True
                thawed_p_names.append(n)
            elif p.requires_grad:
                curr_thawed.append(n)
        if thawed_p_names:
            rank_zero_debug(
                f"{'Initializing with' if init_thaw else 'Thawed'} the following module parameters: "
                f"{translation_func(thawed_p_names) if translation_func else [n for n in thawed_p_names]}"
            )
        curr_thawed.extend(thawed_p_names)
        rank_zero_debug(
            f"The following module parameters are currently thawed: "
            f"{translation_func(curr_thawed) if translation_func else [n for n in curr_thawed]}"
        )
        return thawed_p_names, curr_thawed
