class SupplyChainProbError(Exception):
    pass

class ValidationError(ValueError, SupplyChainProbError):
    pass

class DomainError(ValueError, SupplyChainProbError):
    pass

class FractionalValueError(ValueError, SupplyChainProbError):
    pass
