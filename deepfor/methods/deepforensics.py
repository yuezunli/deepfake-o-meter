
class DeepForCls(object):
    def __init__(self, *args):
        pass

    def run(self, *args):
        raise NotImplementedError('This function is not implemented by subclass.')

    def preproc(sef, *args):
        pass

    def postproc(self, *args):
        pass

    def get_softlabel(self, *args):
        pass

    def get_hardlabel(self, *args):
        pass


class DeepForLoc(object):
    def __init__(self, *args):
        pass

    def run(self, *args):
        raise NotImplementedError('This function is not implemented by subclass.')

    def preproc(sef, *args):
        pass

    def postproc(self, *args):
        pass

    def get_scoremap(self, *args):
        pass

    def get_mask(self, *args):
        pass