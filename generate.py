"""Autogenerated protocols from type+method names, URI, sequence, etc."""

from interfaces import Protocol, allocate_lock, Interface
from advice import metamethod, supermeta
from api import declareAdapterForProtocol, declareAdapterForType
from api import declareAdapter, adapt
from adapters import NO_ADAPTER_NEEDED

__all__ = [
    'protocolForType', 'protocolForURI', 'sequenceOf', 'IBasicSequence',
    'URIProtocol', 'TypeSubset', 'WeakSubset', 'ADAPT_SEQUENCE',
    'SequenceProtocol'
]


class URIProtocol(Protocol):

    """Protocol representing a URI, UUID, or other unique textual identifier"""

    def __init__(self,uri):
        self.URI = uri
        Protocol.__init__(self)

    def __repr__(self):
        return "URIProtocol(%r)" % self.URI

    def __reduce__(self):
        return protocolForURI, (self.URI,)













class TypeSubset(Protocol):

    """Protocol representing some set of a type's methods"""

    def __init__(self,baseType,methods):
        self.baseType = baseType
        self.methods = methods
        Protocol.__init__(self)

    def __repr__(self):
        return "TypeSubset(%r,%r)" % (self.baseType,self.methods)

    def __reduce__(self):
        return protocolForType, (self.baseType, self.methods, False)



























class WeakSubset(TypeSubset,object):

    """TypeSubset that accepts any object with the right attributes"""

    __metaclass__ = type    # new-style so we can use super()

    def __adapt__(self,ob):

        result = supermeta(TypeSubset,self).__adapt__(ob)

        if result is not None:
            return result

        for name in self.methods:
            if not hasattr(ob,name):
                return None
        else:
            return ob

    __adapt__ = metamethod(__adapt__)


    def __repr__(self):
        return "WeakSubset(%r,%r)" % (self.baseType,self.methods)

    def __reduce__(self):
        return protocolForType, (self.baseType, self.methods, True)














class SequenceProtocol(Protocol):

    """Protocol representing a "sequence of" some base protocol"""

    def __init__(self,baseProtocol):
        self.baseProtocol = baseProtocol
        Protocol.__init__(self)

    def __repr__(self):
        return "sequenceOf(%r)" % self.baseProtocol

    def __reduce__(self):
        return sequenceOf, (self.baseProtocol,)


class IBasicSequence(Interface):

    """Non-string, iterable object sequence"""

    def __iter__():
        """Return an iterator over the sequence"""


declareAdapter(
    NO_ADAPTER_NEEDED,
    provides=[IBasicSequence],
    forTypes=[list,tuple]
)













def ADAPT_SEQUENCE(ob, proto):

    """Convert iterable 'ob' into list of objects implementing 'proto'"""

    marker = object()
    out = []
    proto = proto.baseProtocol  # get the protocol to adapt to
    for item in ob:
        item = adapt(item,proto, marker)
        if item is marker:
            return None     # can't adapt unless all members adapt
        out.append(item)
    return out




























__registryLock = allocate_lock()

registry = {}


def protocolForURI(uri):

    """Return a unique protocol object representing the supplied URI/UUID"""

    __registryLock.acquire()
    try:
        try:
            return registry[uri]
        except KeyError:
            proto = registry[uri] = URIProtocol(uri)
            return proto
    finally:
        __registryLock.release()


def protocolForType(baseType, methods=(), implicit=False):

    """Return a protocol representing a subset of methods of a specific type"""

    # Normalize 'methods' to a sorted tuple w/no duplicate names
    methods = dict([(k,k) for k in methods]).keys()
    methods.sort()
    methods = tuple(methods)

    key = baseType, methods, (not not implicit) # ensure implicit is true/false
    return __protocolForType(key)










def sequenceOf(baseProtocol):

    """Return a protocol representing an sequence of a given base protocol"""

    key = (sequenceOf, baseProtocol)

    __registryLock.acquire()

    try:

        try:
            return registry[key]

        except KeyError:
            proto = registry[key] = SequenceProtocol(baseProtocol)
            declareAdapterForProtocol(
                proto, lambda o: ADAPT_SEQUENCE(o,proto), IBasicSequence
            )
            return proto

    finally:
        __registryLock.release()



















def __protocolForType(key):

    """Recursive implementation of protocolForType; assumes standardized key"""

    __registryLock.acquire()

    try:
        try:
            return registry[key]

        except KeyError:
            baseType, methods, implicit = key

            if implicit:
                proto = WeakSubset(baseType,methods)
            else:
                proto = TypeSubset(baseType,methods)

            registry[key] = proto

    finally:
        __registryLock.release()

    # declare that proto implies all subset-method protocols
    if len(methods)>1:
        for method in methods:
            subset = tuple([m for m in methods if m!=method])
            implied = __protocolForType((baseType, subset, implicit))
            declareAdapterForProtocol(implied, NO_ADAPTER_NEEDED, proto)

    # declare that explicit form implies implicit form
    if implicit:
        impliedBy = __protocolForType((baseType, methods, False))
        declareAdapterForProtocol(proto, NO_ADAPTER_NEEDED, impliedBy)

    # declare that baseType implements this protocol
    declareAdapterForType(proto, NO_ADAPTER_NEEDED, baseType)
    return proto



