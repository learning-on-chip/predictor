import tensorflow as tf


class Comparator:
    def __init__(self):
        pass

    def run(self, subject, target, tag_prefix='comparison'):
        errors = getattr(subject, 'run_{}'.format(target))()
        for key in errors:
            tag = '{}_{}_{}'.format(tag_prefix, target, key)
            for i in range(len(errors[key])):
                value = tf.Summary.Value(tag=tag, simple_value=errors[key][i])
                subject.summarer.add_summary(tf.Summary(value=[value]), i + 1)
        subject.summarer.flush()