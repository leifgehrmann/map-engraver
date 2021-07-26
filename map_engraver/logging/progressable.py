import abc


class ProgressObservable(abc.ABC):
    @abc.abstractmethod
    def progress(self):
        pass
