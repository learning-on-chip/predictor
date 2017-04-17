from . import support
from . import tuner
from .random import Random
from .session import Session
import glob
import numpy as np
import os
import re
import threading


class Explorer:
    def __init__(self, input, config):
        self.input = input
        self.config = config.session
        self.tuner = getattr(tuner, config.tuner.name)
        self.tuner = self.tuner(**config.tuner.options)
        self.resource_scale = config.max_step_count / self.tuner.resource
        self.sampler = Sampler(config.sampler)
        self.semaphore = threading.BoundedSemaphore(config.concurrent_count)
        self.agents = {}

    def configure(self, case, restore=True):
        key = support.tokenize(case)
        config = self.config.copy()
        config.output.restore = restore
        config.output.path = os.path.join(config.output.path, key)
        for key in case:
            _adjust(config, key, case[key])
        return config

    def run(self):
        case, resource, score = self.tuner.run(self._generate, self._assess)
        step_count = int(self.resource_scale * resource)
        support.log(self, 'Best: case {}, step {}, score {}',
                    case, step_count, score)
        return (case, step_count)

    def _assess(self, resource, cases):
        step_count = int(self.resource_scale * resource)
        support.log(self, 'Assess: {} cases, up to {} steps',
                    len(cases), step_count)
        agents = []
        for case in cases:
            key = support.tokenize(case)
            agent = self.agents.get(key)
            if agent is None:
                config = self.configure(case)
                session = Session(self.input.copy(), config)
                agent = Agent(session, self.semaphore, config)
                self.agents[key] = agent
            agent.submit(step_count)
            agents.append(agent)
        return [agent.collect(step_count) for agent in agents]

    def _generate(self, count):
        support.log(self, 'Generate: {} cases', count)
        return [self.sampler.get() for _ in range(count)]


class Agent:
    def __init__(self, session, semaphore, config):
        self.session = session
        self.semaphore = semaphore
        self.scores = Agent._load(config.output.path)
        self.output_path = config.output.path
        self.lock = threading.Lock()
        self.done = threading.Lock()

    def collect(self, step_count):
        with self.done:
            return self.scores[step_count]

    def submit(self, step_count):
        with self.lock:
            if step_count in self.scores:
                return
            self.scores[step_count] = None
        self.done.acquire()
        worker = threading.Thread(target=self._run, args=(step_count,),
                                  daemon=True)
        worker.start()

    def _load(path):
        scores = {}
        for path in glob.glob(os.path.join(path, 'score-*.txt')):
            step_count = int(re.search('.*score-(.*).txt', path).group(1))
            scores[step_count] = float(open(path).read())
            support.log(Agent, 'Score: {}', path)
        return scores

    def _save(path, step_count, score):
        path = os.path.join(path, 'score-{}.txt'.format(step_count))
        with open(path, 'w') as file:
            file.write('{:.15e}'.format(score))

    def _run(self, step_count):
        with self.semaphore:
            with self.lock:
                last_step_count = 0
                for key in self.scores:
                    if self.scores[key] is None:
                        continue
                    if key > last_step_count:
                        last_step_count = key
            assert(last_step_count < step_count)
            support.log(self, 'Learn: start at step {}, stop at step {}',
                        last_step_count, step_count)
            self.session.run_training(step_count - last_step_count)
            error = self.session.run_validation()['MRMSE']
            decay = np.reshape(np.exp(-np.arange(len(error))), error.shape)
            score = np.sum(error * decay)
            Agent._save(self.output_path, step_count, score)
            self.session.run_backup()
            with self.lock:
                self.scores[step_count] = score
            support.log(self, 'Learn: stop at step {}, score {}',
                        step_count, score)
            self.done.release()


class Sampler:
    def __init__(self, config):
        self.parameters = config
        support.log(self, 'Cases: {}', self.case_count)

    @property
    def case_count(self):
        return np.prod([len(self.parameters[n]) for n in self.parameters])

    def get(self):
        case = {}
        for key in sorted(self.parameters.keys()):
            chosen = Random.get().randint(len(self.parameters[key]))
            case[key] = self.parameters[key][chosen]
        return case


def _adjust(config, key, value):
    if key == 'dropout_rate':
        config.learner.dropout.options.input_keep_prob = 1 - value[0]
        config.learner.dropout.options.output_keep_prob = 1 - value[1]
    elif key == 'layer_count':
        config.learner.layer_count = value
    elif key == 'learning_rate':
        config.teacher.optimizer.options.learning_rate = value
    elif key == 'unit_count':
        config.learner.unit_count = value
    elif key == 'use_peepholes':
        config.learner.cell.options.use_peepholes = value
    else:
        assert(False)
