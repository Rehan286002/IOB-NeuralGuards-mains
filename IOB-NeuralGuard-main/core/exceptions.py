class FraudDetected(Exception):
    pass

class VelocityLimitExceeded(FraudDetected):
    pass

class VoiceDeepfakeDetected(FraudDetected):
    pass

class GraphMuleDetected(FraudDetected):
    pass

class CircuitBreakerTripped(Exception):
    pass
