"""
Observer Pattern Implementation
(https://en.wikipedia.org/wiki/Observer_pattern)
"""

class Observable:
    def __init__(self):
        self.__observers = set()

    def notify_all(self,*args, **kwargs):
        for observer in self.__observers:
            observer.update(self, *args, **kwargs)

    def attach(self, observer):
        self.__observers.add(observer)
        print("Attached %s" % observer)

    def detach(self, observer):
        self.__observers.remove(observer)

class Observer:
    def __init__(self, observable):
        if observable is not None:
            observable.attach(self)

    def update(self, observable, *args, **kwargs):
        print('Got', args, kwargs, 'From', observable)