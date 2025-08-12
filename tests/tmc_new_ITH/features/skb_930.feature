Feature: TMC is able to execute End2End observation cycles
@XTP-28347 @SKA_mid @XTP-86209
Scenario Outline: TMC skb-930
    Given a TMC
    When End2End observation is repeated <count> times on TMC
    Then Final ObsState is successfully calculated as EMPTY
    Examples:
        | count  |
        | 5      |