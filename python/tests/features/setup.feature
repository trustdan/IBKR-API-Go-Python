Feature: IB Insync Initial Setup
  As a developer
  I want to set up the ib_insync implementation properly
  So that I can connect to Interactive Brokers

  Scenario: Create API instance with default parameters
    Given configuration with default connection parameters
    When I create an IB Insync API instance
    Then the API should be initialized with default values

  Scenario: Create API instance with custom parameters
    Given configuration with custom connection parameters
    When I create an IB Insync API instance
    Then the API should be initialized with custom values

  Scenario: Factory method returns IB Insync implementation
    Given I need a broker API instance
    When I call the factory method with use_ib_insync=True
    Then it should return an IB Insync API instance 