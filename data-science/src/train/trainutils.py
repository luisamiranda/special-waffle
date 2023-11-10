# -*- coding: utf-8 -*-

from shared.generalutils import replace_in_file


def specialize_training_spec(training_spec_location, images_location, experiment_name=""):
    replace_in_file(training_spec_location, '@@STORAGE@@', images_location)
    replace_in_file(training_spec_location, '@@EXPERIMENT_NAME@@', experiment_name)
