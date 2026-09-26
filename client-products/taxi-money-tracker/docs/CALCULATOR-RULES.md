# MMK Taxi Money & Profit Tracker
## Calculator Rules v1.0.0

## 1. Core Principle

The system records the taxi's money from the beginning of the working
day until the driver finishes work and performs Daily Close.

Every financial event is recorded separately.

Income must not be mixed with expenses.

## 2. Load Income

Each load records:

- Date
- Time
- Route
- Passenger count
- Fare per passenger
- Gross load amount
- Payment method
- Notes

Formula:

Gross Load = Passenger Count × Fare Per Passenger

Daily Gross Income = Sum of all completed loads.

## 3. Fuel

Each fuel record contains:

- Date
- Vehicle
- Odometer
- Litres
- Price per litre
- Total fuel cost
- Fuel station
- Notes

Formula:

Fuel Cost = Litres × Price Per Litre

Distance = End Odometer - Start Odometer

Fuel Cost Per KM = Fuel Cost ÷ Distance

Fuel Consumption = Distance ÷ Litres

Fuel price remains configurable.


## 4. Operating Expenses

Expense categories include:

- Car Wash
- Maintenance
- Repairs
- Tyres
- Oil
- Parking
- Tolls
- Association/operating costs
- Other

Every expense records:

- Date
- Category
- Description
- Amount
- Vehicle
- Odometer
- Notes

## 5. Maintenance Reserve

The owner may configure a maintenance reserve.

Example:

Maintenance Reserve Per KM = R0.80

Daily Maintenance Reserve:

Distance × Reserve Per KM

The reserve is recorded separately from actual maintenance spending.

## 6. Owner Target

The owner configures the operating agreement.

Example:

Daily Owner Target = R1,200

The system must NOT assume that R1,200 is a universal taxi rule.

Possible operating models:

- Fixed daily target
- Target after fuel
- Percentage/commission
- Custom agreement

## 7. Owner Contribution

Each contribution records:

- Date
- Vehicle
- Driver
- Expected amount
- Actual amount
- Shortfall
- Status

Formula:

Contribution Shortfall =
Expected Contribution - Actual Contribution

If actual contribution reaches the expected amount:

Status = TARGET REACHED

Otherwise:

Status = SHORT


## 8. Driver Balance

The system calculates the driver's remaining balance according to
the configured operating agreement.

The exact formula depends on the selected agreement.

The calculation must be visible to the user.

## 9. Daily Operating Result

At Daily Close the system calculates:

Gross Income
- Fuel
- Other Expenses
- Maintenance Reserve
= Operating Result

The system then calculates:

Expected Owner Contribution
- Actual Owner Contribution
= Contribution Shortfall

Driver Balance is calculated according to the selected agreement.

## 10. Daily Close

A working day records:

- Opening odometer
- Closing odometer
- Total loads
- Total passengers
- Gross income
- Fuel
- Other expenses
- Maintenance reserve
- Expected owner contribution
- Actual owner contribution
- Driver balance
- Notes

Once the day is closed, it becomes a historical operating record.

## 11. Weekly Review

Weekly totals include:

- Gross income
- Fuel
- Other expenses
- Car wash
- Maintenance
- Maintenance reserve
- Owner contributions
- Driver balances
- Kilometres
- Loads
- Passengers

The system calculates:

- Average daily income
- Average loads per day
- Average passengers per day
- Fuel cost per kilometre
- Total maintenance spending
- Contribution shortfalls

## 12. Data Integrity

Financial records contain:

- Created date/time
- Updated date/time
- Vehicle
- Driver where applicable
- Record type
- Amount

Financial changes should eventually be recorded in an audit log.

## 13. Product Rule

The application is a calculator and record-keeping system.

It does not determine the legal or contractual relationship between
a taxi owner, driver, association, or other party.

The owner enters the applicable business agreement and operating rules.

