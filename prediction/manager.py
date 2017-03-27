class Manager:
    def __init__(self, config):
        self.backup_period = config.backup_period
        self.test_period = config.test_period

    def should_backup(self, state):
        return self._should(self.backup_period, state.step)

    def should_test(self, state):
        return self._should(self.backup_period, state.step)

    def _should(self, period, step):
        return step > 0 and step % period == 0
