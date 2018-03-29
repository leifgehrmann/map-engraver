from typing import Callable, no_type_check


class ProgressController:

    progress_callable = None

    def set_progress_callable(
            self,
            progress_callable: Callable[[str, float, float], no_type_check]
    ) -> 'ProgressController':
        self.progress_callable = progress_callable
        return self
